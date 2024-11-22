import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from loguru import logger

class LLM:
    def __init__(self):
        logger.info("Initializing LLM service")
        load_dotenv()
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=None,
            max_retries=2
        )
        logger.info("LLM service initialized successfully")
    
    def generate_response(self, system_prompt, prompt):
        logger.info(f"Generating response for prompt: {prompt[:50]}...")
        try:
            messages = [
                ("system", system_prompt),
                ("human", prompt)
            ]
            response = self.llm.invoke(messages)
            logger.success("Response generated successfully")
            return response.content
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
