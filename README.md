# GraphRAG

This project implements GraphRAG using LLaMA 3 for knowledge graph construction and evaluation on the 2WikiMultihopQA dataset.

## Setup

### Local Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Neo4j:
- Download and install Neo4j from https://neo4j.com/download/
- Start Neo4j server
- Create a new database and set password

3. Download the 2WikiMultihopQA dataset

### Docker Installation (Recommended)

1. Install Docker and Docker Compose

2. Build and run the containers:
```bash
docker-compose up --build
```

The web interface will be available at http://localhost:5010

## Project Structure

- `src/`: Source code
  - `data_processing/`: Data preprocessing and graph construction
  - `graph_rag/`: GraphRAG implementation
  - `evaluation/`: Evaluation scripts
  - `web/`: Web interface and API
- `config/`: Configuration files
- `scripts/`: Utility scripts
- `dataset/`: Dataset storage

## Usage

### Using Docker (Recommended)

1. Start the services:
```bash
docker-compose up
```

2. Access the web interface at http://localhost:5000

### Manual Usage

1. Process dataset and construct knowledge graph:
```bash
python src/data_processing/build_graph.py
```

2. Run evaluation:
```bash
python src/evaluation/evaluate.py
```

3. Start the web interface:
```bash
flask run --host=0.0.0.0
```
