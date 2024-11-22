from flask import Flask, jsonify, request
import redis
import os
from dotenv import load_dotenv
from rag import RAGService
from llm import LLM

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get environment variables with defaults
REDIS_HOST = os.getenv('REDIS_URL', 'redis://localhost:6379')
MILVUS_URI = os.getenv('MILVUS_URI', 'http://localhost:19530')
MILVUS_TOKEN = os.getenv('MILVUS_TOKEN', 'root:Milvus')

# Initialize services
redis_client = redis.from_url(REDIS_HOST, decode_responses=True)
rag_service = RAGService(uri=MILVUS_URI, token=MILVUS_TOKEN)
llm = LLM()

# Constants
MIN_TTL = int(os.getenv('MIN_TTL', '10'))
MAX_TTL = int(os.getenv('MAX_TTL', '60'))
IMPORTANCE_THRESHOLD = float(os.getenv('IMPORTANCE_THRESHOLD', '70'))

IMPORTANCE_CHECK_PROMPT = """Analyze the following input and determine its importance on a scale of 0-100.
Consider factors like:
- Long-term relevance
- Information density
- Uniqueness of information
Return only the numeric value."""

@app.route('/')
def home():
    return jsonify(message="Welcome to the Memory Management System!")

@app.route('/process', methods=['POST'])
def process_input():
    data = request.json
    if not data or 'input' not in data:
        return jsonify(error="No input provided"), 400

    input_text = data['input']
    
    # Determine importance using LLM
    importance_percentage = float(llm.generate_response(IMPORTANCE_CHECK_PROMPT, input_text))
    
    # Calculate TTL for short-term memory
    ttl = MIN_TTL + (MAX_TTL - MIN_TTL) * (importance_percentage / 100)
    
    if importance_percentage < IMPORTANCE_THRESHOLD:
        # Store in short-term memory (Redis)
        redis_client.set(input_text, "stored", ex=int(ttl))
        return jsonify({
            "status": "stored_short_term",
            "ttl": int(ttl),
            "importance": importance_percentage
        })

    # Store in long-term memory (RAG)
    rag_service.add_documents([input_text])
    return jsonify({
        "status": "stored_long_term",
        "importance": importance_percentage
    })

@app.route('/query', methods=['POST'])
def query_memory():
    data = request.json
    if not data or 'query' not in data:
        return jsonify(error="No query provided"), 400

    query_text = data['query']
    
    # Check short-term memory first
    short_term_result = redis_client.get(query_text)
    if short_term_result:
        return jsonify({
            "source": "short_term",
            "result": short_term_result
        })

    # Query long-term memory
    long_term_results = rag_service.search(query_text)
    if long_term_results:
        return jsonify({
            "source": "long_term",
            "results": long_term_results
        })

    return jsonify({
        "source": "none",
        "message": "No matching information found"
    })

if __name__ == '__main__':
    app.run(debug=True)
