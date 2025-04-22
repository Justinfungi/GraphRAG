import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
import numpy as np
from config.config import *

class GraphRAG:
    def __init__(self):
        try:
            print(f"Initializing LLaMA model on {DEVICE}...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                LLAMA_MODEL_PATH,
                token=os.getenv('HUGGING_FACE_HUB_TOKEN'),
                cache_dir=CACHE_PATH
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                LLAMA_MODEL_PATH,
                token=os.getenv('HUGGING_FACE_HUB_TOKEN'),
                cache_dir=CACHE_PATH,
                device_map='auto',  # Automatically handle device placement
                torch_dtype=torch.float16  # Use half precision to reduce memory usage
            )
            print("LLaMA model loaded successfully")
            
            print("Loading embedding model...")
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
            self.embedding_model = self.embedding_model.to(DEVICE)
            print("Embedding model loaded successfully")
            
            print("Connecting to Neo4j...")
            self.neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            print("Connected to Neo4j successfully")
        except Exception as e:
            print(f"Error initializing GraphRAG: {str(e)}")
            raise

    def get_graph_context(self, query, max_hops=2):
        """Retrieve relevant subgraph context based on the query"""
        # Encode query
        query_embedding = self.embedding_model.encode(query)
        
        # Neo4j query to find relevant entities and their relationships
        cypher_query = """
        MATCH path = (e1:Entity)-[r:RELATES*1..2]->(e2:Entity)
        WHERE e1.name CONTAINS $query OR e2.name CONTAINS $query
        RETURN path LIMIT 10
        """
        
        with self.neo4j_driver.session() as session:
            result = session.run(cypher_query, query=query)
            paths = result.values()
        
        # Convert paths to text context
        context = []
        for path in paths:
            path_text = self._path_to_text(path[0])
            context.append(path_text)
        
        return " ".join(context)

    def _path_to_text(self, path):
        """Convert a Neo4j path to natural text"""
        nodes = path.nodes
        rels = path.relationships
        text_parts = []
        
        for i in range(len(nodes) - 1):
            text_parts.append(f"{nodes[i]['name']} {rels[i].type} {nodes[i+1]['name']}")
        
        return ". ".join(text_parts)

    def generate_response(self, query):
        """Generate response using GraphRAG approach"""
        # Get graph context
        graph_context = self.get_graph_context(query)
        
        # Construct prompt with graph context
        prompt = f"""Context from Knowledge Graph:
        {graph_context}
        
        Question: {query}
        
        Answer: """
        
        # Generate response
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=MAX_LENGTH, truncation=True)
        outputs = self.model.generate(
            **inputs,
            max_length=MAX_LENGTH,
            temperature=TEMPERATURE,
            num_return_sequences=1
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

    def close(self):
        """Close Neo4j connection"""
        self.neo4j_driver.close()
