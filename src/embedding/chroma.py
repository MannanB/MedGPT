from chromadb.config import Settings
from chromadb.utils import embedding_functions
from chromadb.db import duckdb
import chromadb

from data_processing import dialog, handbook
from ai import api

from tqdm import tqdm

import sys, argparse

class ChromaDatabase:
    COLLECTION_NAME = "medgpt_data"
    SOURCES = ["HealthCareMagic + iCliniq", "Handbook of Signs & Symptoms"]

    def __init__(self):
        self.st_embedder = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="multi-qa-distilbert-dot-v1")
        self.client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chroma_database"))
        self.collection = self.client.get_or_create_collection(ChromaDatabase.COLLECTION_NAME)

        self.parsers = (dialog.DialogDataParser(), handbook.HandbookDataParser())
        for parser in self.parsers:
            parser.load_data()

        print(len(self.parsers[0].documents)+len(self.parsers[1].documents))

        self.cur_id = 0

    def add_embeddings(self):      
        for i in range(len(self.parsers)):
            for j, doc in tqdm(enumerate(self.parsers[i].documents)):
                embed_text = self.parsers[i].embedding_text[j]
                self.collection.add(documents=doc,
                                    embeddings=api.get_embedding(embed_text),
                                    metadatas={"source": ChromaDatabase.SOURCES[i], "credit": self.parsers[i].credits[doc]},
                                    ids=f"id{self.cur_id}")
                self.cur_id += 1

    def query(self, query, source, n=2):
        return self.collection.query(
            query_embeddings=api.get_embedding(query),
            n_results=n,
            include=["metadatas", "documents"],
            where={"source": source},
        )  
    
    def delete(self):
        self.client.delete_collection(name=ChromaDatabase.COLLECTION_NAME)
    

if __name__ == "__main__":
    # cli mode
    parser = argparse.ArgumentParser(prog='MedGPT Chroma Database')
    parser.add_argument('--populate', '-p', action='store_true')
    parser.add_argument('--delete', '-d', action='store_true')
    args = parser.parse_args()
    chroma_db = ChromaDatabase()
    if args.delete:
        input("This will delete the entire database. Press enter to continue")
        chroma_db.delete()

    if args.populate:
        if chroma_db.collection.count() != 0:
            print("Database is already populated. Use --delete first if you want to re-create the database")
        else:
            chroma_db.add_embeddings()