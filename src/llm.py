import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

class LLM:
    def __init__(self):
        load_dotenv()
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # Note: "gpt-4o-mini" doesn't exist, using "gpt-4" instead
            temperature=0,
            max_tokens=None,
            max_retries=2
        )
    
    def generate_response(self, system_prompt, prompt):
        messages = [
            ("system", system_prompt),
            ("human", prompt)
        ]
        response = self.llm.invoke(messages)
        return response.content
