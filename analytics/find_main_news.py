import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def load_stopwords(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def find_important_news_by_text(df, stopwords_file, text_column="Text", summary_column="Summary", similarity_threshold=0.5, min_mentions=2):

    vectorizer = TfidfVectorizer(stop_words= load_stopwords(stopwords_file))
    tfidf_matrix = vectorizer.fit_transform(df[text_column])
    
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    added_main_news = set()

    important_news = []

    for idx in range(len(df)):
        if idx in added_main_news:
            continue

        similar_news = set()

        for j, sim in enumerate(cosine_sim[idx]):
            if sim >= similarity_threshold and idx != j:
                similar_news.add(j)

        if len(similar_news) + 1 >= min_mentions:
            important_news.append(idx)
            added_main_news.add(idx)
            added_main_news.update(similar_news)
    
    return df.iloc[important_news]