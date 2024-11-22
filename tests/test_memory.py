import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5001"

def make_request(endpoint, data):
    response = requests.post(f"{BASE_URL}/{endpoint}", json=data)
    return response.json()

def test_memory_system():
    print("\n=== Testing Memory Management System ===\n")

    # Test 1: Temporal Context
    print("Test 1: Temporal Context")
    temporal_inputs = [
        "The current time is " + datetime.now().strftime("%H:%M:%S"),
        "Today's weather is sunny and warm",
        "The FIFA World Cup happens every four years",
    ]
    
    for input_text in temporal_inputs:
        result = make_request("process", {"input": input_text})
        print(f"Input: {input_text}")
        print(f"Result: {json.dumps(result, indent=2)}\n")

    # Test 2: Conversation Context
    print("\nTest 2: Conversation Context")
    conversation = [
        "My name is John Doe",
        "I live in New York",
        "I work as a software engineer",
        "I'm currently working on a project about AI",
    ]
    
    for message in conversation:
        result = make_request("process", {"input": message})
        print(f"Processing: {message}")
        print(f"Result: {json.dumps(result, indent=2)}\n")

    # Test retrieval
    query = "What do you know about John?"
    result = make_request("query", {"query": query})
    print(f"Query: {query}")
    print(f"Result: {json.dumps(result, indent=2)}\n")

    # Test 3: Information Importance
    print("\nTest 3: Information Importance")
    test_inputs = [
        "The speed of light is 299,792,458 meters per second",  # Important scientific fact
        "I just had a coffee",  # Trivial information
        "Breaking News: Major scientific breakthrough in quantum computing",  # Important current event
        "The sky is blue today",  # Trivial observation
    ]
    
    for input_text in test_inputs:
        result = make_request("process", {"input": input_text})
        print(f"Input: {input_text}")
        print(f"Result: {json.dumps(result, indent=2)}\n")

    # Test 4: Memory Decay
    print("\nTest 4: Memory Decay")
    short_term_input = "This is a temporary note that should expire soon"
    result = make_request("process", {"input": short_term_input})
    print(f"Initial storage: {json.dumps(result, indent=2)}")
    
    # Wait for short-term memory to expire
    if result.get("status") == "stored_short_term":
        ttl = result.get("ttl", 10)
        print(f"Waiting {ttl} seconds for memory to decay...")
        time.sleep(ttl + 1)
        
        # Try to retrieve after expiry
        result = make_request("query", {"query": short_term_input})
        print(f"After decay: {json.dumps(result, indent=2)}\n")

    # Test 5: Complex Queries
    print("\nTest 5: Complex Queries")
    # Store related information
    context_inputs = [
        "OpenAI was founded in December 2015",
        "OpenAI released GPT-3 in June 2020",
        "OpenAI's mission is to ensure AGI benefits all of humanity",
    ]
    
    for input_text in context_inputs:
        make_request("process", {"input": input_text})

    complex_queries = [
        "When was OpenAI founded?",
        "What are OpenAI's major developments?",
        "What is OpenAI's mission?",
    ]
    
    for query in complex_queries:
        result = make_request("query", {"query": query})
        print(f"Query: {query}")
        print(f"Result: {json.dumps(result, indent=2)}\n")

if __name__ == "__main__":
    test_memory_system()
