import json
import pandas as pd
import argparse
from pathlib import Path
import os

def extract_top_records(json_file, output_excel, num_records=10):
    """
    Extract the top N records from a JSON file and save them to an Excel file
    
    Args:
        json_file: Path to the JSON file
        output_excel: Path to save the Excel file
        num_records: Number of records to extract (default: 10)
    """
    print(f"Loading dataset from {json_file}")
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        print(f"Successfully loaded data with {len(data)} examples")
    except Exception as e:
        print(f"Error loading file: {e}")
        return
    
    # Take the top N records
    top_records = data[:num_records]
    print(f"Extracted {len(top_records)} records")
    
    # Convert to a flat structure for Excel
    excel_data = []
    for record in top_records:
        # Extract basic info
        flat_record = {
            "_id": record.get("_id", ""),
            "question": record.get("question", ""),
            "answer": record.get("answer", ""),
            "type": record.get("type", ""),
            "entity_ids": record.get("entity_ids", ""),
        }
        
        # Context (simplified)
        context_titles = [ctx[0] for ctx in record.get("context", [])]
        flat_record["context_titles"] = ", ".join(context_titles)
        
        # Supporting facts (simplified)
        sup_facts = record.get("supporting_facts", [])
        flat_record["num_supporting_facts"] = len(sup_facts)
        flat_record["supporting_facts"] = str(sup_facts[:3]) + "..." if len(sup_facts) > 3 else str(sup_facts)
        
        # Evidences (simplified)
        evidences = record.get("evidences", [])
        flat_record["num_evidences"] = len(evidences)
        flat_record["evidences"] = str(evidences[:3]) + "..." if len(evidences) > 3 else str(evidences)
        
        # Add full JSON as a string (optional)
        flat_record["full_json"] = json.dumps(record)
        
        excel_data.append(flat_record)
    
    # Convert to DataFrame
    df = pd.DataFrame(excel_data)
    
    # Save to Excel
    print(f"Saving to Excel file: {output_excel}")
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_excel), exist_ok=True)
        df.to_excel(output_excel, index=False)
        print(f"Successfully saved {len(excel_data)} records to {output_excel}")
    except Exception as e:
        print(f"Error saving to Excel: {e}")

    # Additionally, save a small JSON file with the top records
    json_output = os.path.splitext(output_excel)[0] + ".json"
    print(f"Also saving JSON file: {json_output}")
    try:
        with open(json_output, 'w') as f:
            json.dump(top_records, f, indent=2)
        print(f"Successfully saved {len(top_records)} records to {json_output}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")

def main():
    parser = argparse.ArgumentParser(description="Extract top records from a JSON file and save to Excel")
    parser.add_argument("--json_file", type=str, default="/mnt/znzz/jus/code/self/GraphRAG/dataset/train.json", 
                      help="Path to the JSON file")
    parser.add_argument("--output_excel", type=str, default="/mnt/znzz/jus/code/self/GraphRAG/dataset/train_sample.xlsx", 
                      help="Path to save the Excel file")
    parser.add_argument("--num_records", type=int, default=10, 
                      help="Number of records to extract")
    
    args = parser.parse_args()
    
    extract_top_records(args.json_file, args.output_excel, args.num_records)

if __name__ == "__main__":
    main() 