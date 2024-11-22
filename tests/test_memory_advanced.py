import requests
import json
import time

BASE_URL = "http://0.0.0.0:5001"

def make_request(endpoint, data):
    print(f"Requesting {endpoint} with data: {json.dumps(data)}")
    response = requests.post(f"{BASE_URL}/{endpoint}", json=data)
    return response.json()

def test_advanced_quantum_mechanics():
    print("\n=== Teaching Advanced Quantum Mechanics to the AI ===\n")

    # Step 1: Feed comprehensive knowledge
    print("Step 1: Feeding Comprehensive Knowledge")
    advanced_knowledge = [
        "Schrodinger's equation describes how the quantum state of a system changes over time. It is a key mathematical framework in quantum mechanics.",
        "The collapse of the wavefunction occurs when a quantum system's state becomes definite due to measurement, leaving superposition.",
        "The Copenhagen interpretation suggests that quantum mechanics does not describe reality itself, but only probabilities of measurement outcomes.",
        "The many-worlds interpretation posits that all possible outcomes of quantum measurements are realized in separate, branching universes.",
        "Quantum tunneling is a phenomenon where particles pass through potential barriers that they classically should not be able to cross.",
        "Bell's theorem demonstrates that no physical theory of local hidden variables can reproduce all the predictions of quantum mechanics.",
        "The double-slit experiment shows that particles like electrons and photons can display interference patterns, indicating wave-like behavior.",
        "In quantum field theory, particles are excitations of underlying quantum fields, providing a framework for understanding fundamental forces.",
        "The quantum Zeno effect states that a quantum system's evolution can be frozen by frequent observation or measurement."
    ]

    for concept in advanced_knowledge:
        result = make_request("process", {"input": concept})
        print(f"Input: {concept}")
        print(f"Result: {json.dumps(result, indent=2)}\n")
        time.sleep(1)  # Simulate gradual input

    # Step 2: Ask challenging questions
    print("Step 2: Asking Challenging Questions")
    difficult_questions = [
        "What does Schrodinger's equation describe, and why is it important?",
        "What happens during the collapse of the wavefunction?",
        "What are the key differences between the Copenhagen interpretation and the many-worlds interpretation?",
        "Explain the concept of quantum tunneling with an example.",
        "What does Bell's theorem tell us about local hidden variables?",
        "Why is the double-slit experiment considered foundational in quantum mechanics?",
        "What are quantum fields, and how do they explain particles?",
        "How does the quantum Zeno effect impact the evolution of a quantum system?"
    ]

    for question in difficult_questions:
        result = make_request("query", {"query": question})
        print(f"Question: {question}")
        print(f"Result: {json.dumps(result, indent=2)}\n")
        time.sleep(1)

    # Step 3: Test synthesis and critical reasoning
    print("Step 3: Testing Synthesis and Critical Reasoning")
    complex_queries = [
        "How does Schrodinger's equation relate to the collapse of the wavefunction?",
        "Compare the double-slit experiment with the quantum Zeno effect.",
        "If Bell's theorem disproves local hidden variables, what does that imply about reality?",
        "Summarize the core ideas of quantum mechanics, including interpretations and paradoxes."
    ]

    for query in complex_queries:
        result = make_request("query", {"query": query})
        print(f"Complex Query: {query}")
        print(f"Result: {json.dumps(result, indent=2)}\n")
        time.sleep(1)

    # Step 4: Assess adaptive learning
    print("Step 4: Assessing Adaptive Learning")
    repeated_query = "Explain the many-worlds interpretation of quantum mechanics."
    for i in range(3):  # Simulate repeated queries to observe response improvement
        result = make_request("query", {"query": repeated_query})
        print(f"Query: {repeated_query} (Iteration {i + 1})")
        print(f"Result: {json.dumps(result, indent=2)}\n")
        time.sleep(1)

if __name__ == "__main__":
    test_advanced_quantum_mechanics()
