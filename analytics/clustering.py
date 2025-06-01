import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from processing.text_cleaner import load_stopwords
from umap import UMAP

import spacy
nlp = spacy.load("uk_core_news_sm")

def lemmatize_texts(texts):
    lemmatized = []
    for doc in nlp.pipe(texts, disable=["ner", "parser"]):
        lemmas = [token.lemma_ for token in doc if not token.is_punct and not token.is_space]
        lemmatized.append(" ".join(lemmas))
    return lemmatized

def cluster_news_with_bertopic(df, stopwords_file, text_column='Text'):
    stopwords = load_stopwords(stopwords_file)
    texts = df[text_column].astype(str).tolist()

    texts = lemmatize_texts(texts)

    if len(texts) < 3:
        raise ValueError("Недостатньо даних для кластеризації (мінімум 3 записи).")

    embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    vectorizer_model = CountVectorizer(stop_words=list(stopwords))

    umap_model = UMAP(n_neighbors=min(5, len(texts) - 1), n_components=5, metric='cosine')

    print("Кластеризація...")
    topic_model = BERTopic(embedding_model=embedding_model,
                           vectorizer_model=vectorizer_model,
                           umap_model=umap_model,
                           language="multilingual")

    topics, probs = topic_model.fit_transform(texts)

    topic_info = topic_model.get_topic_info()
    topic_dict = {row['Topic']: row['Name'] for _, row in topic_info.iterrows()}

    df['Cluster'] = topics
    df['Theme'] = df['Cluster'].map(topic_dict)

    return df, topic_model
