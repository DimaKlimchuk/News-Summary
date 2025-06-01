def run_pipeline_main(update_progress, sources=None, telegram_channels=None):
    from scraper.news_scraper import scrape_news
    from scraper.telegram_scraper import scrape_telegram_news
    from processing.text_cleaner import clean_text_dataset
    from analytics.clustering import cluster_news_with_bertopic
    from analytics.find_main_news import find_important_news_by_text
    from analytics.sentiment import analyze_sentiment
    from analytics.theme_clasification import classify_dataframe_topics
    from analytics.verificate_news import verify_important_news
    from summarizer.summarizer import summarize_dataset
    from db.database import insert_news_batch
    import asyncio
    import pandas as pd

    stopwords_file = "stopwords_ua.txt"
    text_columns = ['Text']
    print(sources)
    update_progress("Збір новин...", 5)

    df_news = scrape_news(sources)
    if df_news is None or df_news.empty:
        df_news = pd.DataFrame(columns=["Source", "Title", "Text", "Date", "Link"])

    df_telegram = asyncio.run(scrape_telegram_news(telegram_channels=telegram_channels))
    if df_telegram is None or df_telegram.empty:
        df_telegram = pd.DataFrame(columns=["Source", "Title", "Text", "Date", "Link"])

    # 3. Об’єднання
    df_all = pd.concat([df_news, df_telegram], ignore_index=True)

    if df_all.empty:
        update_progress("Новин не знайдено", 100)
        return

    # 4. Очищення
    update_progress("Очищення новин...", 15)
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

    # 5. Кластеризація
    update_progress("Кластеризація...", 30)
    df_clustered, model = cluster_news_with_bertopic(df_cleaned, stopwords_file, text_column='Text')

    if df_clustered is None:
        update_progress("Немає достатньо текстів для кластеризації.", 100)
        return

    # 6. Тематична класифікація
    update_progress("Тематична класифікація...", 45)
    df_clustered = classify_dataframe_topics(df_clustered, column="Theme")

    # 7. Аналіз тональності
    update_progress("Аналіз тональності...", 60)
    df_clustered = analyze_sentiment(df_clustered, text_column='Text')

    # 8. Визначення головних новин
    update_progress("Вибір головних новин...", 70)
    df_important = find_important_news_by_text(df_clustered, stopwords_file, text_column="Text")

    # 9. Верифікація
    update_progress("Верифікація...", 80)
    df_verified = verify_important_news(df_important)

    # 10. Резюмування
    update_progress("Резюмування...", 90)
    df_verified = summarize_dataset(
        df=df_verified,
        text_column='Text',
        summary_column='Summary'
    )

    # 11. Збереження в базу
    insert_news_batch(df_verified)
    update_progress("Готово!", 100)
