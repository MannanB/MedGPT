from .embeddings import TextEmbedding, get_embedding
import tiktoken

# Handbook of Signs & Symptoms

HANDBOOK_EMBEDS_PATH = "././processed_data/handbook_embeds.json"

class HandbookEmbeddings(TextEmbedding):
    def __init__(self, dp):
        super().__init__(HANDBOOK_EMBEDS_PATH, dp)

    def create_embeddings(self):
        for line in self.text:
            headers = list(line.keys())
            bigheader = headers[0]
            for header in headers:
                for text in line[header]['paragraphs']:
                    # add the header to the text to increase relevance with embedding queries
                    text_with_header = bigheader
                    if bigheader != header:
                        text_with_header += ' ' + header
                    text_with_header +=  ": " + text
                    self.embeddings[text] = get_embedding(text_with_header)

    def create_credits(self):
        # TODO: combine create_credits and create_embeddings + cache credits
        for line in self.text:
            headers = list(line.keys())
            for header in headers:
                for text in line[header]['paragraphs']:
                    self.credits[text] = line[header]['page']

                

