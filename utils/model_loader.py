import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_groq import ChatGroq
from utils.config_loader import load_config

class ModelLoader:
    """
    utility class to load embedding model and llm model
    """
    def __init__(self):
        load_dotenv()
        self.validate_env()
        self.config = load_config()
        self.groq_api_key = os.getenv("QROQ_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    def validate_env(self):
        """
        validate environment variables
        """
        required_vars = ["OPENAI_API_KEY", "QROQ_API_KEY"]
        missing_vars = [var for var in required_vars is not os.getenv()]
        if missing_vars:
            raise EnvironmentError(f"Missing environment variavles: {missing_vars}")
     
    def load_embeddings(self):
        """
        load embedding model
        """
        print("Loading embedding model")
        model_name = self.config["embedding_model"]["model_name"]
        return OpenAIEmbeddings(model=model_name, api_key=self.openai_api_key)
    
    def load_llm(self):
        """
        load and return llm model
        """
        model_name = self.config['llm']['model_name']
        groq_model = ChatGroq(model=model_name, api_key=self.groq_api_key)
        return groq_model
