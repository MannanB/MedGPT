
import numpy as np
import pandas as pd
import tiktoken
import time

from embedding.chroma import ChromaDatabase
import relevance as relevance
from ai import api

import os

class MedGPT:
    def __init__(self):
        self.past_knowledge = []
        self.chroma_db = ChromaDatabase()
        self.enc = tiktoken.get_encoding("cl100k_base")

        # How much past knowledge to add to the query when using chroma
        self.query_context = 3
        # Amount of docs per source
        self.n_retrievals = 5
        # Amount of tokens per source
        self.max_tokens_per_source = 1000
        # How much past knowledge to keep in order
        self.sustain_past = 1

        try:
            with open('./prompt.txt', 'r') as f:
                self.prompt = f.read()
        except FileNotFoundError:
            raise FileNotFoundError("Prompt file not found.")

    def query_db(self, query, source, n=15, max_tokens=-1):
        res = self.chroma_db.query(query, source, n=n)
        texts = []
        total_tokens = 0
        for doc in res['documents'][0]:
            texts.append(doc)
            total_tokens += len(self.enc.encode(doc))
            if max_tokens != -1 and total_tokens > max_tokens:
                break
        credits = []
        if res['metadatas']:
            credits = [meta['credit'] for meta in res['metadatas'][0][:len(texts)]]
        return texts, credits

    def create_textbook_context(self, query):
        best_previous_queries = sorted(self.past_knowledge, key = lambda e: e[2], reverse=True)

        for q, _, _ in best_previous_queries[:self.query_context]:
            query += ' ' + q

        best_text = ''
        credits = []

        for source in ChromaDatabase.SOURCES:
            # TODO: Arbitrary value. Add to a config (n, max_tokens; maybe unique per source)
            texts, _credits = self.query_db(query, source=source, n=self.n_retrievals, max_tokens=self.max_tokens_per_source)
            best_text += ' ' + ' '.join(texts)
            credits += _credits

        return best_text, credits
    
    def build_prompt(self, query, context):
        prompt = self.prompt
        prompt += f"\n\nTextbook: {context}"

        # TODO: arbitrary value. add to a config
        if self.past_knowledge:
            best_previous_queries = sorted(self.past_knowledge, key = lambda e: e[2], reverse=True)
            for i in range(self.sustain_past):
                if i >= len(self.past_knowledge):
                    break
                best_previous_queries.remove(self.past_knowledge[-(i+1)]) 
                best_previous_queries.insert(i, self.past_knowledge[-(i+1)])

            previous_queries_ctx = []

            tokens = 0
            for pk in best_previous_queries:
                previous_queries_ctx.append(pk)
                tokens += len(self.enc.encode(pk[0]+' '+pk[1]))
                if tokens > 750:
                    break

            previous_queries_ctx.reverse()
            
            for pk in previous_queries_ctx:
                prompt += f"\nPatient: {pk[0]}\nDoctor: {pk[1]}"
        
        prompt += f"\nPatient: {query}\nDoctor:"

        # store the prompt in aifle for debugging
        with open('./promptdebug.txt', 'w', encoding="UTF-8") as f:
            f.write(prompt)
        
        return prompt

    def get_answer(self, query):
        context, credits = self.create_textbook_context(query)
        score = relevance.get_relevance(query)
        prompt = self.build_prompt(query, context)
        msg = api.get_chat_completion(prompt, "You are a doctor. Answer as concisely as possible, and make sure to ask the user for more information if needed. Use simple terms.")
        self.past_knowledge.append([query, msg, score])

        return msg, score, credits
    
    def run(self):
        while 1:     
            query = input('Ask a question > ') 
            ans = self.get_answer(query)
            print(ans)
            print()

MedGPT().run()