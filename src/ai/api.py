import openai
import os
import time

openai.api_key = "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"

def get_embedding(text, model="text-embedding-ada-002"):
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

def get_chat_completion(user_input, sys_role, model="gpt-3.5-turbo"):
    resp = openai.ChatCompletion.create(
            model=model,
            messages=[
                    {"role": "system", "content": sys_role},
                    {"role": "user", "content": user_input},
                ]
            )
    msg = resp["choices"][0]["message"]["content"]

    return msg
