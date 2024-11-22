from flask import Flask, jsonify, request
import redis
import os
import threading
import time
from dotenv import load_dotenv
from rag import RAGService
from llm import LLM
from loguru import logger

# Configure loguru
logger.add("logs/app.log", rotation="500 MB", level="INFO")

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get environment variables with defaults
REDIS_HOST = os.getenv('REDIS_URL', 'redis://redis:6379/0')
MILVUS_URI = os.getenv('MILVUS_URI', 'http://milvus:19530')
MILVUS_TOKEN = os.getenv('MILVUS_TOKEN', 'root:Milvus')
SHORT_TERM_ACCESS_THRESHOLD = int(os.getenv('SHORT_TERM_ACCESS_THRESHOLD', '3'))
SLEEP_PROCESS_INTERVAL = int(os.getenv('SLEEP_PROCESS_INTERVAL', '300'))  # 5 minutes

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
    return jsonify(message="Welcome to the Enhanced Memory Management System!")

@app.route('/process', methods=['POST'])
def process_input():
    data = request.json
    if not data or 'input' not in data:
        logger.error("No input provided in request")
        return jsonify(error="No input provided"), 400

    input_text = data['input']
    logger.info(f"Processing new input: {input_text[:50]}...")
    
    # Determine importance using LLM
    importance_percentage = float(llm.generate_response(IMPORTANCE_CHECK_PROMPT, input_text))
    logger.info(f"Calculated importance: {importance_percentage}")
    
    # Calculate TTL for short-term memory
    ttl = MIN_TTL + (MAX_TTL - MIN_TTL) * (importance_percentage / 100)
    
    if importance_percentage < IMPORTANCE_THRESHOLD:
        # Store in short-term memory (Redis)
        redis_client.set(input_text, "stored", ex=int(ttl))
        redis_client.hincrby("access_count", input_text, 0)  # Initialize access count
        logger.info(f"Stored in short-term memory with TTL: {int(ttl)}")
        return jsonify({
            "status": "stored_short_term",
            "ttl": int(ttl),
            "importance": importance_percentage
        })

    # Store in long-term memory (RAG)
    rag_service.add_documents([input_text])
    logger.info("Stored in long-term memory")
    return jsonify({
        "status": "stored_long_term",
        "importance": importance_percentage
    })

@app.route('/query', methods=['POST'])
def query_memory():
    data = request.json
    if not data or 'query' not in data:
        logger.error("No query provided in request")
        return jsonify(error="No query provided"), 400

    query_text = data['query']
    logger.info(f"Processing query: {query_text[:50]}...")
    
    # Check short-term memory first
    short_term_result = redis_client.get(query_text)
    if short_term_result:
        redis_client.hincrby("access_count", query_text, 1)  # Increment access count
        return jsonify({
            "source": "short_term",
            "result": short_term_result
        })

    # Query long-term memory
    long_term_results = rag_service.search(query_text)
    if long_term_results:
        # Assume LLM uses some content from the retrieved documents
        used_data = long_term_results[0]['text']  # Simplified assumption
        logger.info(f"LLM used data: {used_data}")
        return jsonify({
            "source": "long_term",
            "results": long_term_results,
            "used_data": used_data
        })

    return jsonify({
        "source": "none",
        "message": "No matching information found"
    })

def sleep_like_processing():
    """
    Background process to review short-term memory, decide if items should go to long-term memory,
    and clean up unnecessary long-term memory data.
    """
    while True:
        logger.info("Starting sleep-like processing...")

        # Process short-term memory
        keys = redis_client.keys()
        for key in keys:
            if redis_client.ttl(key) > 0:  # Ensure the key is still valid
                access_count = int(redis_client.hget("access_count", key) or 0)
                if access_count >= SHORT_TERM_ACCESS_THRESHOLD:
                    # Summarize and move to long-term memory
                    summarized_content = llm.summarize(key)
                    rag_service.add_documents([summarized_content])
                    logger.info(f"Promoted to long-term memory: {summarized_content}")
                    redis_client.delete(key)
                    redis_client.hdel("access_count", key)

        # Clean up long-term memory
        all_documents = rag_service.get_all_documents()
        for doc in all_documents:
            usage_feedback = llm.check_importance(doc["text"])
            if usage_feedback < IMPORTANCE_THRESHOLD:
                logger.info(f"Removed unnecessary document from long-term memory: {doc['text'][:50]}...")
                rag_service.delete_document(doc["id"])

        logger.info("Completed sleep-like processing.")
        time.sleep(SLEEP_PROCESS_INTERVAL)

if __name__ == '__main__':
    # Start the background sleep-like processing thread
    threading.Thread(target=sleep_like_processing, daemon=True).start()
    app.run(debug=True, port=5000, host='0.0.0.0')
