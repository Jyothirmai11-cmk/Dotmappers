import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), 'chroma_db')
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'documents')
EVAL_LOG_DB = os.path.join(os.path.dirname(__file__), 'eval_log.db')

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = 'BAAI/bge-small-en-v1.5'
LLM_MODEL = 'gemini-1.5-flash'
TOP_K_RETRIEVAL = 10
TOP_K_RERANK = 5

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")
