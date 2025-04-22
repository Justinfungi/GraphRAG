import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from neo4j import GraphDatabase
import json
from tqdm import tqdm
import spacy
from config.config import *

#spacy.cli.download("en_core_web_sm")


class KnowledgeGraphBuilder:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(LLAMA_MODEL_PATH)
        self.model = AutoModelForCausalLM.from_pretrained(LLAMA_MODEL_PATH)
        self.nlp = spacy.load("en_core_web_sm")
        self.neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def extract_entities_relations(self, text, hyperlinks):
        """Extract entities and relations using LLaMA model and hyperlinks"""
        # First, add all hyperlinked entities as known entities
        triples = []
        for hyperlink in hyperlinks:
            entity = hyperlink['target_title']
            mention = hyperlink['mention']
            if entity != mention:
                triples.append((mention, "refers_to", entity))

        # Then use LLaMA to extract additional relations
        prompt = f"""Extract relationships between entities from the following text.
        Format: Entity1 | Relation | Entity2
        Known entities: {', '.join(set([h['target_title'] for h in hyperlinks]))}
        
        Text: {text}
        
        Relationships:"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=MAX_LENGTH, truncation=True)
        outputs = self.model.generate(**inputs, max_length=MAX_LENGTH, temperature=TEMPERATURE)
        extracted_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Parse the extracted text to get additional entity-relation triples
        for line in extracted_text.split("\n"):
            if "|" in line:
                parts = [p.strip() for p in line.split("|")] 
                if len(parts) == 3:
                    triples.append(tuple(parts))
        
        return triples

    def create_graph_nodes(self, tx, entity):
        """Create nodes in Neo4j"""
        tx.run("MERGE (e:Entity {name: $name})", name=entity)

    def create_graph_relations(self, tx, entity1, relation, entity2):
        """Create relationships in Neo4j"""
        query = """
        MATCH (e1:Entity {name: $entity1})
        MATCH (e2:Entity {name: $entity2})
        MERGE (e1)-[r:RELATES {type: $relation}]->(e2)
        """
        tx.run(query, entity1=entity1, relation=relation, entity2=entity2)

    def process_document(self, paragraph):
        """Process a single paragraph and update the knowledge graph"""
        text = paragraph['text']
        hyperlinks = paragraph['hyperlinks']
        
        triples = self.extract_entities_relations(text, hyperlinks)
        
        with self.neo4j_driver.session() as session:
            # Create nodes for all hyperlinked entities first
            for hyperlink in hyperlinks:
                session.execute_write(self.create_graph_nodes, hyperlink['target_title'])
                session.execute_write(self.create_graph_nodes, hyperlink['mention'])
            
            # Create relationships
            for entity1, relation, entity2 in triples:
                session.execute_write(self.create_graph_nodes, entity1)
                session.execute_write(self.create_graph_nodes, entity2)
                session.execute_write(self.create_graph_relations, entity1, relation, entity2)

    def build_knowledge_graph(self):
        """Build knowledge graph from train.json"""
        # Using the absolute path from config
        print(f"Processing data from {DATASET_PATH}...")
        
        with open(DATASET_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in tqdm(data):
                # Extract and process paragraphs based on the structure of train.json
                # Note: This will need to be adjusted based on the actual structure of train.json
                if 'context' in item:
                    for paragraph_data in item['context']:
                        # Create a paragraph object in the expected format
                        paragraph = {
                            'text': paragraph_data[1][0] if paragraph_data[1] else "",
                            'hyperlinks': self._extract_hyperlinks(paragraph_data[1][0]) if paragraph_data[1] else []
                        }
                        self.process_document(paragraph)
    
    def _extract_hyperlinks(self, text):
        """Extract hyperlinks from text using NLP techniques"""
        hyperlinks = []
        doc = self.nlp(text)
        
        # Use Named Entity Recognition to identify potential hyperlinks
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'LOC', 'WORK_OF_ART']:
                hyperlinks.append({
                    'target_title': ent.text,
                    'mention': ent.text
                })
        
        return hyperlinks

def main():
    builder = KnowledgeGraphBuilder()
    builder.build_knowledge_graph()

if __name__ == "__main__":
    main()
