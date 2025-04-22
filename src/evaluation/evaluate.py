import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from datasets import load_dataset
from tqdm import tqdm
from sklearn.metrics import accuracy_score, f1_score
import json
from datetime import datetime

from graph_rag.graph_rag import GraphRAG
from config.config import *

def evaluate_graphrag():
    # Load test dataset
    dataset = load_dataset(WIKI_DATASET_NAME)
    test_data = dataset["test"]
    
    # Initialize GraphRAG
    graph_rag = GraphRAG()
    
    results = {
        "predictions": [],
        "ground_truth": [],
        "metrics": {}
    }
    
    # Evaluate on test set
    print("Evaluating GraphRAG on test set...")
    # Limit to first 10 examples for faster evaluation
    for item in tqdm(test_data[:10]):
        question = item["question"]
        answer = item["answer"]
        
        # Generate prediction
        predicted_answer = graph_rag.generate_response(question)
        
        results["predictions"].append({
            "question": question,
            "predicted": predicted_answer,
            "actual": answer
        })
        results["ground_truth"].append(answer)
    
    # Calculate metrics
    accuracy = accuracy_score(
        [a.lower() for a in results["ground_truth"]], 
        [p["predicted"].lower() for p in results["predictions"]]
    )
    
    results["metrics"] = {
        "accuracy": float(accuracy),  # Convert numpy float to Python float for JSON serialization
        "timestamp": datetime.now().isoformat(),
        "num_examples": len(results["predictions"])
    }
    
    graph_rag.close()
    return results

if __name__ == "__main__":
    evaluate_graphrag()
