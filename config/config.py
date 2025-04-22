from pathlib import Path
import torch

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATASET_PATH = PROJECT_ROOT / "dataset"
CACHE_PATH = PROJECT_ROOT / "cache"

# Neo4j configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"  # Change this to your Neo4j password

# LLaMA configuration
LLAMA_MODEL_PATH = "meta-llama/Llama-2-7b-chat-hf"  # Using smaller 7B chat model
MAX_LENGTH = 512
TEMPERATURE = 0.7
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Graph construction
MAX_ENTITIES_PER_DOC = 50
MAX_RELATIONS_PER_DOC = 100
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

# Hyperlink processing
MAX_HYPERLINKS_PER_PARA = 30
