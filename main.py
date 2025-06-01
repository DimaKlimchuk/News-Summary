# main.py

import os
import pandas as pd
from analytics.verificate_news import verify_important_news
from analytics.theme_clasification import classify_dataframe_topics
from analytics.find_main_news import find_important_news_by_text
from analytics.sentiment import analyze_sentiment
from analytics.clustering import cluster_news_with_bertopic
from processing.text_cleaner import clean_text_dataset
from summarizer.summarizer import summarize_dataset
from scraper.news_scraper import scrape_news
from scraper.telegram_scraper import scrape_telegram_news
from db.database import insert_news_batch


from db.database import create_database
create_database()

stopwords_file = 'stopwords_ua.txt'
text_columns = ['Text']

print("Збір новин з RSS...")
df_news = scrape_news()

print("Збір новин з Telegram...")
df_telegram = scrape_telegram_news()

df_all = pd.concat([df_news, df_telegram], ignore_index=True)

if not df_all.empty:
    print("Очищення всіх новин...")
    df_cleaned = clean_text_dataset(
        df=df_all,
        stopwords_file=stopwords_file,
        text_columns=text_columns,
        date_column='Date',
        dropna_columns=['Text'],
        deduplicate_column='Text',
        for_llm=True,
        for_classical_nlp=False
    )

    print("Дані очищено.")

    print("Кластеризація новин...")
    df_clustered, model = cluster_news_with_bertopic(df_cleaned, stopwords_file, text_column='Text')

    print("Класифікація тематик...")
    df_clustered = classify_dataframe_topics(df_clustered, column="Theme")

    print("Аналіз тональності...")
    df_clustered = analyze_sentiment(df_clustered, text_column='Text')

    print("Пошук головних новин...")
    df_important = find_important_news_by_text(df_clustered, stopwords_file, text_column="Text")

    print("Верифікація головних новин через RSS...")
    df_verified = verify_important_news(df_important)

    print("Генерація анотацій...")
    df_verified = summarize_dataset(
        df=df_verified,
        text_column='Text',
        summary_column='Summary'
    )

    print("Збереження в базу даних...")
    insert_news_batch(df_verified)

    print("Всі оброблені новини збережено в базу даних.")
else:
    print("Жодної новини для обробки не знайдено.")
