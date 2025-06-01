import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import feedparser
import time as t

RSS_SOURCES = [
    {"name": "tsn", "url": "https://tsn.ua/rss"},
    {"name": "pravda", "url": "https://www.pravda.com.ua/rss/"},
    {"name": "24tv", "url": "https://24tv.ua/rss/all.xml"},
    {"name": "bbc", "url": "https://www.bbc.com/ukrainian/index.xml"},
    {"name": "unian", "url": "https://rss.unian.net/site/news_ukr.rss"}
]

def get_article_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        if "tsn.ua" in url:
            content = soup.select_one('div.c-post__inner') or soup.select_one('div.article-content')
        elif "pravda.com.ua" in url:
            content = soup.select_one('div.article__text') or soup.select_one('div.post_text')
        elif "24tv.ua" in url:
            content = soup.select_one('div.news-text') or soup.select_one('div.article-text')
        elif "bbc.com" in url:
            content = soup.select_one('article') or soup.select_one('main')
        elif "unian.ua" in url:
            content = soup.select_one('div.article__body') or soup.select_one('div.article-text')
        else:
            return "No article text (unknown source)"

        if not content:
            return "No article content found"

        for tag in content.find_all(['script', 'style', 'figure', 'figcaption', 'aside', 'noscript', 'video']):
            tag.decompose()

        paragraphs = []
        for p in content.find_all('p'):
            text = p.get_text(strip=True)
            if not text:
                continue
            if any(phrase in text.lower() for phrase in [
                "реклама", "відео дня", "джерело", "читайте також", "дивіться також",
                "вас також можуть зацікавити", "підписуйтесь", "теми дня", "дивіться відео"
            ]):
                continue
            paragraphs.append(text)

        return " ".join(paragraphs).strip()

    except Exception as e:
        print(f"Error parsing article text from {url}: {e}")
        return "No article text"

def scrape_news(sources=None):
    today = datetime.now().date()
    all_news = []

    selected_sources = [s for s in RSS_SOURCES if not sources or s["name"] in sources]
    print(selected_sources)

    for source in selected_sources:
        print(f"Парсимо: {source['name']} ({source['url']})")
        feed = feedparser.parse(source['url'])

        for entry in feed.entries:
            try:
                published = entry.get('published', '') or entry.get('updated', '')
                if not published:
                    continue

                pub_date = datetime(*entry.published_parsed[:6]).date()
                if pub_date != today:
                    continue

                title = entry.title.strip()
                link = entry.link.strip()
                print(f"Отримуємо: {title}")

                text = get_article_text(link)

                all_news.append([source['name'], title, text, today, link])
                t.sleep(1)  # Avoid overloading servers

            except Exception as e:
                print(f"Помилка при обробці новини: {e}")

    return pd.DataFrame(all_news, columns=['Source', 'Title', 'Text', 'Date', 'Link']) if all_news else pd.DataFrame()
