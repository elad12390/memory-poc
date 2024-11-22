from flask import Flask, jsonify, request
from llm import LLM

app = Flask(__name__)
llm = LLM()

@app.route('/')
def home():
    return jsonify(message="Welcome to the Flask server!")

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt')
    if not prompt:
        return jsonify(error="No prompt provided"), 400
    
    response = llm.generate_response(prompt)
    return jsonify(response=response)

if __name__ == '__main__':
    app.run(debug=True)