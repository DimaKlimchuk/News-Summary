import feedparser
import time
import pandas as pd
import difflib
import re

rss_sources = {
    'ukrinform': 'https://www.ukrinform.ua/rss/main.xml',
    'pravda': 'https://www.pravda.com.ua/rss/',
    'tsn': 'https://tsn.ua/rss',
    '24tv': 'https://24tv.ua/rss/all.xml',
    'nv': 'https://nv.ua/ukr/rss/all.xml',
    'unian': 'https://www.unian.ua/rss/publications',
    'obozrevatel': 'https://www.obozrevatel.com/rss.xml',
    'glavcom': 'https://glavcom.ua/rss/all.xml',
    'liga': 'https://news.liga.net/news/rss.xml',
    'bbc_ukrainian': 'https://feeds.bbci.co.uk/ukrainian/rss.xml'
}

def clean_title(text):
    return re.sub(r'\s+', ' ', text.strip()).lower()

def is_similar(title1, title2, threshold=0.5):
    return difflib.SequenceMatcher(None, clean_title(title1), clean_title(title2)).ratio() >= threshold

def verify_news_in_rss(title, rss_sources, threshold=1):
    verified_sources = []
    for source_name, rss_url in rss_sources.items():
        feed = feedparser.parse(rss_url)
        for entry in feed.entries:
            if is_similar(title, entry.title):
                verified_sources.append(source_name)
                break
        time.sleep(1)
    return verified_sources if len(verified_sources) >= threshold else []

def verify_important_news(df, title_column='Title'):
    df = df.copy()
    verificated_flags = []
    sources_list = []

    for idx, row in df.iterrows():
        title = row[title_column]
        verified_sources = verify_news_in_rss(title, rss_sources)

        if verified_sources:
            verificated_flags.append(True)
            sources_list.append(', '.join(verified_sources))
        else:
            verificated_flags.append(False)
            sources_list.append('')

    df['Verificated'] = verificated_flags
    df['Sources'] = sources_list
    return df
