import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from datetime import datetime
from nltk.tokenize import RegexpTokenizer
from collections import Counter
import spacy

_tokenizer = RegexpTokenizer(r'\w+')

nlp = spacy.load("uk_core_news_sm")


def load_stopwords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        stopwords = set(file.read().splitlines())
    return stopwords

def lemmatize_text(text):
    doc = nlp(text)
    return ' '.join([token.lemma_ for token in doc if token.lemma_ != ''])

def has_enough_unique_words(text, min_unique=10):
    words = set(_tokenizer.tokenize(text))
    return len(words) >= min_unique



def clean_text_dataset(df, stopwords_file, text_columns,
                       date_column=None, time_column=None,
                       dropna_columns=None, deduplicate_column=None,
                       for_llm=True, for_classical_nlp=False):


    for col in text_columns:
        df = df[~df[col].str.lower().str.contains('no article text', na=False)]

    stopwords = load_stopwords(stopwords_file)

    if dropna_columns:
        df.dropna(subset=dropna_columns, inplace=True)

    if date_column:
        df[date_column] = df[date_column].fillna('Unknown')
    if time_column:
        df[time_column] = df[time_column].fillna('Unknown')

    def convert_date(date_str):
        try:
            dt = pd.to_datetime(date_str)
            return dt.date()
        except:
            return pd.NaT

    if date_column:
        df[date_column] = df[date_column].apply(convert_date)

    if deduplicate_column:
        df.drop_duplicates(subset=[deduplicate_column], inplace=True)

    def basic_clean(text):
        text = re.sub(r'<.*?>', '', str(text))
        text = re.sub(r'\S*(http|https|www)\S*', '', text)
        text = re.sub(r'[^a-zA-Zа-яА-ЯґҐєЄіІїЇ0-9\s\$\€\+\-]', '', text)
        text = ' '.join([word for word in text.split() if len(word) > 1 and word.lower() not in ['top', 'news', 'підписатись']])
        return text.lower()

    def remove_stopwords(text):
        words = _tokenizer.tokenize(text)
        return ' '.join([word for word in words if word not in stopwords])

    for col in text_columns:
        df[col] = df[col].astype(str).apply(basic_clean)

        if for_classical_nlp:
            df[col] = df[col].apply(remove_stopwords)
            df[col] = df[col].apply(lemmatize_text)

        if for_llm:
            pass 

    for col in text_columns:
        df = df[df[col].apply(has_enough_unique_words)]

    return df 
