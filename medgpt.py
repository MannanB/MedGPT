import openai
import numpy as np
import pandas as pd
import tiktoken

from chroma import ChromaDatabase
import keywords

openai.api_key = "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"

class MedGPT:
    def __init__(self):
        self.past_knowledge = []
        self.chroma_db = ChromaDatabase()
        self.tfdf = keywords.tfidf()
        self.query = None
        self.enc = tiktoken.get_encoding("cl100k_base")

    def query_db(self, query, source, n=15, max_tokens=-1):
        res = self.chroma_db.query(query, source, n=n)
        texts = []
        total_tokens = 0
        for doc in res['documents']:
            texts.append(doc[0])
            total_tokens += len(self.enc.encode(doc[0]))
            if max_tokens != -1 and total_tokens > max_tokens:
                break
        credits = []
        if res['metadatas']:
            credits = [meta['credit'] for meta in res['metadatas'][0]]
        return texts, credits

    def create_textbook_context(self):
        best_previous_queries = sorted(self.past_knowledge, key = lambda e: e[2], reverse=True)
        extended_query = self.query
        max_queries = 3 # TODO: arbitrary value. Why not top 4?
        i = 0
        for query, _, _ in best_previous_queries:
            extended_query += ' ' + query
            if i >= max_queries:
                break
            i += 1

        best_text = ''

        textbook_texts, textbook_credits = self.query_db(extended_query, source=ChromaDatabase.HANDBOOK_SOURCE, n=5, max_tokens=500)
        dialog_texts, dialogs_credits = self.query_db(extended_query, source=ChromaDatabase.DIALOG_SOURCE, n=15, max_tokens=1000)

        best_text += ' ' + ' '.join(textbook_texts)
        best_text += ' ' + ' '.join(dialog_texts)

        return best_text, textbook_credits+dialogs_credits

    def get_answer(self):
        if not self.query: return
        
        context, credits = self.create_textbook_context()
        score = keywords.find_tfidf_value(self.query, self.tfdf)
        user_data = f"You are a doctor that is talking to the patient in order to find the cause of their symptoms and how to help them. You will be given a passage from a medical textbook for advice on what to say and ask the user based on their query. Make sure you ask for more information if you need it to answer the question. If you are absolutely unsure of the question, say \"I don't know.\" Make sure you provide concise information."
        user_data += f"\n\nTextbook: {context}"

        if self.past_knowledge:
            best_previous_queries = sorted(self.past_knowledge, key = lambda e: e[2], reverse=True)
            best_previous_queries.remove(self.past_knowledge[-1])
            best_previous_queries.insert(0, self.past_knowledge[-1]) # ensure that at least the last qna is added
            for pk in best_previous_queries: # sort past knowledge by importance (tfidf)
                user_data += f"\nPatient: {pk[0]}\nDoctor: {pk[1]}"
                if len(self.enc.encode(user_data)) > 1000:
                    break

        user_data += f"\nPatient: {self.query}\nDoctor:"

        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                    {"role": "system", "content": "You are a doctor. Answer as concisely as possible, and make sure to ask the user for more information if needed. Use simple terms."},
                    {"role": "user", "content": user_data},
                ]
            )
        msg = resp["choices"][0]["message"]["content"]

        self.past_knowledge.insert(0, [self.query, msg, score])

        return msg, score, credits
    
    def run(self):
        while 1:     
            self.query = input('Ask a question > ') 
            ans = self.get_answer()
            print(ans)
            print()

