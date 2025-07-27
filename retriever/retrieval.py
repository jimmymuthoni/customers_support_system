import os
from langchain_astradb import AstraDBVectorStore
from typing import List
from langchain_core.documents import Document
from utils.config_loader import load_config
from utils.model_loader import ModelLoader
from dotenv import load_dotenv

class Retriever:
    """
    class to perform retrieval from the astradb vector store
    """
    def __init__(self):
        self.model_loader = ModelLoader()
        self.config = load_config()
        self.load_env_variables()
        self.vstore = None
        self.retriever = None

    def load_env_variables(self):
        """
        loading the environment variables
        """
        load_dotenv()
        required_vars = ['OPENAI_API_KEY', 'ASTRA_DB_API_ENDPOINT', 'ASTRA_DB_APPLICATION_TOKEN', 'ASTRADBKEYSPACE']
        missing_vars = [var for var in required_vars if os.getenv is None]
        if missing_vars:
            raise EnvironmentError(f"Missing environment variable: {missing_vars}")
        
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.db_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
        self.db_application_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
        self.db_keyspace = os.getenv("ASTRA_DB_KEYSPACE")

    def load_retriever(self):
        """
        creating a vector retriever
        """
        if not self.vstore:
            collection_name = self.config["astra_db"]["collection_name"]
            self.vstore = AstraDBVectorStore(
                embedding = self.model_loader.load_embeddings(),
                collection_name=collection_name,
                api_endpoint=self.db_api_endpoint,
                token=self.db_application_token,
                namespace=self.db_keyspace

            )

        if not self.retiever:
            top_k = self.config['retriever']['top_k'] if "retriever" in self.config else 3
            retriever = self.vstore.as_retriever(search_kwargs={"k": top_k})
            print("Retriever loaded successfully")
            return retriever
        
    def call_retriever(self, query:str) -> List[Document]:
        """
        function to call and invoke retriever
        """
        retriever = self.load_retriever()
        output = retriever.invoke(query)
        return output

if __name__ == "__main__":
    retriever_obj = Retriever()
    user_query = "Can you suggest good budget laptops?"
    results = retriever_obj.call_retriever(user_query)

    for idx, doc in enumerate(results, 1):
        print(f"Result {idx}: {doc.page_content}\nMetadata: {doc.metadata}\n")


            
