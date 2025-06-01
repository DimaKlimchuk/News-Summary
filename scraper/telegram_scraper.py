from telethon import TelegramClient
from telethon.errors import RpcCallFailError
import pandas as pd
from datetime import datetime
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
phone_number = os.getenv('TELEGRAM_PHONE')
session_name = os.getenv('SESSION_NAME')

DEFAULT_CHANNELS = [
    'https://t.me/UkraineNow',
    'https://t.me/lachentyt',
    'https://t.me/ssternenko',
    'https://t.me/business_ua'
]

async def scrape_telegram_news(telegram_channels=None):
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start(phone_number)

    today = datetime.now().date()
    all_messages = []
    print(telegram_channels)
    selected_channels = telegram_channels or DEFAULT_CHANNELS

    for channel_url in selected_channels:
        try:
            username = channel_url.replace('https://t.me/', '').strip()

            async for message in client.iter_messages(username, limit=1000):
                if message.text:
                    msg_date = message.date.date()
                    if msg_date != today:
                        continue

                    message_text = message.text.strip()
                    timestamp = message.date.strftime('%Y-%m-%d')
                    message_link = f"https://t.me/{username}/{message.id}"

                    all_messages.append({
                        'Source': channel_url,
                        'Title': message_text[:100],
                        'Text': message_text,
                        'Date': timestamp,
                        'Link': message_link
                    })

        except RpcCallFailError as e:
            print(f"Помилка отримання запису з {channel_url}: {e}")
        except Exception as e:
            print(f"Неочікувана помилка з {channel_url}: {e}")

    await client.disconnect()
    return pd.DataFrame(all_messages)
