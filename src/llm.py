import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

class LLM:
    def __init__(self):
        load_dotenv()
        self.llm = ChatOpenAI(
            model="gpt-4",  # Note: "gpt-4o-mini" doesn't exist, using "gpt-4" instead
            temperature=0,
            max_tokens=None,
            max_retries=2
        )
    
    def generate_response(self, prompt):
        messages = [("human", prompt)]
        response = self.llm.invoke(messages)
        return response.content
