from chromadb.config import Settings
import chromadb
from chromadb.db import duckdb

from embedding import dialog_embedding, handbook_embedding, embeddings
from data_processing import dialog, handbook

import sys, argparse

class ChromaDatabase:
    COLLECTION_NAME = "medgpt_data"
    DIALOG_SOURCE = "HealthCareMagic + iCliniq"
    HANDBOOK_SOURCE = "Handbook of Signs & Symptoms"

    def __init__(self):
        self.client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chroma_database"))
        self.collection = self.client.get_or_create_collection(ChromaDatabase.COLLECTION_NAME)
        self.cur_id = 0

    def add_embedding(self, text_embedding, source):
        embeddings = []
        docs = []
        metas = []
        ids = []
        for doc, embedding in text_embedding.embeddings.items():
            docs.append(doc)
            embeddings.append(embedding)
            metas.append({"source": source, "credit": text_embedding.credits[doc]})      
            ids.append(f"id{self.cur_id}")
            self.cur_id += 1 
        self.collection.add(embeddings=embeddings, documents=docs, metadatas=metas, ids=ids)
        
    def populate_db(self):
        self.cur_id = 0
        input("Populating the database will require you to re-create all embeddings. Press enter to continue")
        dialog_data = dialog.DialogDataParser()
        handbook_data = handbook.HandbookDataParser()
        
        dialog_data.create_data()
        handbook_data.create_data()

        dialogs = dialog_embedding.DialogEmbeddings(dialog_data.data)
        handbooks = handbook_embedding.HandbookEmbeddings(handbook_data.data)

        self.add_embedding(dialogs, ChromaDatabase.DIALOG_SOURCE)
        self.add_embedding(handbooks, ChromaDatabase.HANDBOOK_SOURCE)

    def query(self, embedding, source, n=2):

        return self.collection.query(
            query_embeddings=embeddings.get_embedding(embedding),
            n_results=n,
            include=["metadatas", "documents"],
            where={"source": source}
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
            chroma_db.populate_db()