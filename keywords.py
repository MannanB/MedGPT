from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import pandas as pd

from data_processing import handbook

def tfidf():
    tfidf_train_raw = []
    datap = handbook.HandbookDataParser()
    datap.create_data()
    for line in datap.data:
        headers = list(line.keys())
        for header in headers:
            for text in line[header]['paragraphs']:
                tfidf_train_raw.append(text)

    ps = PorterStemmer()
    tfidf_train = []
    for train in tfidf_train_raw:
        cleaned_words = ''
        for word in word_tokenize(train.lower().strip()):
            cleaned_words += ps.stem(word) + ' '
        tfidf_train.append(cleaned_words)

    print(len(tfidf_train))
    tfidfvectorizer = TfidfVectorizer(analyzer='word',stop_words= 'english', use_idf=True)
    tfidf_wm = tfidfvectorizer.fit_transform(tfidf_train)

    tfidf_tokens = tfidfvectorizer.get_feature_names_out()

    df_tfidfvect = pd.DataFrame(data = tfidf_wm.toarray(),index = ['Doc'+str(i) for i in range(0, len(tfidf_train))],columns = tfidf_tokens)
    df_tfidfvect = df_tfidfvect.sum().sort_values(ascending=False)
    return df_tfidfvect

def find_tfidf_value(text, df_tfidfvect):
    ps = PorterStemmer()
    score = 0
    for word in word_tokenize(text.lower().strip()):
        # TODO: user error prevention: maybe use embeddings (openai or otherwise) to find similar words in tfidf vocab?
        sWord = ps.stem(word)
        if sWord in df_tfidfvect:
            score += df_tfidfvect[sWord]
    return score

