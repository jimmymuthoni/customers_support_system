import os
import sys
import pandas as pd
from dotenv import load_dotenv
from typing import List, Tuple
from langchain_core.documents import Document
from astrapy.info import VectorServiceOptions
from langchain_astradb import AstraDBStore, AstraDBVectorStore
from utils.model_loader import ModelLoader
from custom_exceptions.exceptions import CustomerSupportException
from utils.config_loader import load_config


class DataIngestion:
    """
    class to handle data ingestion, transformation and loading it to astradb
    """
    def __init__(self):
        """
        Initialize environmenent variables, embedding model and csv path
        """
        self.model_loader = ModelLoader()
        self.load_env_variables()
        self.csv_path = self.get_csv_path()
        self.product_data = self.load_csv()
        self.config = load_config()

    def load_env_variables(self):
        """
        load and validate required environments varibales
        """
        load_dotenv()
        required_vars = ["OPENAI_API_KEY", "ASTRA_DB_API_ENDPOINT", "ASTRA_DB_APPLICATION_TOKEN"]
        missing_vars = [vars for vars in required_vars if not os.getenv(vars)]
        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {missing_vars}")
        
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.db_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
        self.application_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
        self.db_keyspace = os.getenv("ASTRA_DB_KEYSPACE")

    def get_csv_path(self):
        """
        get the path ro the csv file located in 'data' folder
        """
        current_dir = os.getcwd()
        csv_path = os.path.join(current_dir, 'data', 'flipkart_product_review.csv')

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at: {csv_path}")
        
        return csv_path
    
    def load_csv(self):
        """
        load product data from csv
        """
        df = pd.read_csv(self.csv_path)
        expected_columns = {'product_title','rating','summary','review'}
        if not expected_columns.issubset(set(df.columns)):
            raise ValueError(f"CSV must contain columns: {expected_columns}")
        
        return df
    
    def transform_data(self):
        """
        Transform product data into list of Langchain Document ojects.
        """
        product_list = []
        for _, row in self.product_data.iterrows():
            product_entry = {
                "product_name": row['product_title'],
                "product_rating": row['rating'],
                'product_summary': row['summary'],
                'product_review': row['review']
            }
            product_list.append(product_entry)
        
        documents = []
        for entry in product_list:
            metadata = {
                "product_name": entry['product_name'],
                'product_rating': entry['product_rating'],
                'product_summary': entry['product_summary']
            }
            doc = Document(page_content=entry['product_review'], metadata=metadata)
            documents.append(doc)
        return documents
    
    def store_in_vector_db(self, documents: List[Document]):
        """
        store documens into astraDB vector store.
        """
        collection_name = self.config['astra_db']['collection_name']
        vector_store = AstraDBVectorStore(
            embedding = self.model_loader.load_embeddings(),
            collection_name = collection_name,
            api_endpoint = self.db_api_endpoint,
            token = self.application_token,
            namespace = self.db_keyspace,
        )
        vector_store.add_documents(documents)
        inserted_ids = vector_store.add_documents(documents)
        print(f"Successfully inserted {len(inserted_ids)} documents into AstraDB")
        return vector_store, inserted_ids
    
    def run_pipeline(self):
        """
        run the full pipeline: transform data and store into vector DB.
        """
        documents = self.transform_data()
        vstore, inserted_ids = self.store_in_vector_db(documents)
        
        #sample query
        query = "Can you tell me the low budget headphone?"
        results = vstore.similarity_search(query)

        print(f"\nSample search for query: '{query}'")
        for res in results:
            print(f"Content: {res.page_content}\nMetadata: {res.metadata}\n")

if __name__ == "__main__":
    ingestion = DataIngestion()
    ingestion.run_pipeline()