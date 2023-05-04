from .embeddings import TextEmbedding, get_embedding

DIALOG_EMBEDS_PATH = "././processed_data/dialog_embeds.json"

class DialogEmbeddings(TextEmbedding):
    def __init__(self, dp):
        super().__init__(DIALOG_EMBEDS_PATH, dp)

    def create_embeddings(self):
        for patient_data in self.text:
            doc_data, url = self.text[patient_data]
            self.embeddings[doc_data] = get_embedding(patient_data)

    def create_credits(self):
        for patient_data in self.text:
            doc_data, url = self.text[patient_data]
            self.credits[doc_data] = url

