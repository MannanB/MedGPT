import openai, time, json, os
import numpy as np
from tqdm import tqdm

MODEL_NAME = "ada"
EMBEDDINGS_MODEL = f"text-embedding-{MODEL_NAME}-002"


class TextEmbedding:
    def __init__(self, source, data):
        self.source = source

        self.text = data
        self.embeddings = {}
        self.credits = {}

        if os.path.exists(self.source):
            self.load_embeddings()
        else:
            input(f"Embedding source {source} was not found. Press Enter to re-create the embeddings")
            self.create_embeddings()
            with open(self.source, "w") as f:
                f.write(json.dumps(self.embeddings, indent=4))
        self.create_credits()

    def load_text(self):
        pass

    def create_embeddings(self):
        pass

    def create_credits(self):
        pass

    def load_embeddings(self):
        with open(self.source, 'r') as f:
            print(f'loading {self.source}...')
            self.embeddings = json.load(f)

def get_embedding(text, model=EMBEDDINGS_MODEL):
    result = None
    while not result:
        try:
            result = openai.Embedding.create(
            model=model,
            input=text)
        except Exception as e:
            print(e)
            time.sleep(5)
    return result["data"][0]["embedding"]
