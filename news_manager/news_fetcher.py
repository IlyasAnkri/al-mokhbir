import logging
import feedparser
import openai
import telegram
import asyncio
import requests
from datetime import datetime, timedelta
from .models import NewsSource, BotSetting

# Configure logging
logging.basicConfig(level=logging.INFO)

def fetch_rss_news(url):
    feed = feedparser.parse(url)
    news_items = []

    for entry in feed.entries:
        if 'published_parsed' in entry:
            published_date = datetime(*entry.published_parsed[:6])
            news_items.append({
                'title': entry.title,
                'link': entry.link,
                'summary': entry.summary,
                'published_date': published_date,
            })

    logging.info(f"Fetched {len(news_items)} news items from {url}")
    return news_items

def fetch_news_from_websites():
    news_sources = NewsSource.objects.filter(source_type='website')
    all_news = []
    now = datetime.now()
    last_12_hours = now - timedelta(hours=12)

    for source in news_sources:
        news_items = fetch_rss_news(source.url)
        recent_news = [item for item in news_items if item['published_date'] > last_12_hours]
        all_news.extend(recent_news)

    logging.info(f"Total news items fetched in the last 12 hours: {len(all_news)}")
    return all_news

def group_summaries_by_topics(news_items):
    openai.api_key = BotSetting.objects.get(name='OPENAI_API_KEY').value
    summaries = [item['summary'] for item in news_items]
    prompt = "I want you to group those news by topics professionally and exclude everything related to sports:\n\n"

    for summary in summaries:
        prompt += f"- {summary}\n"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Forget everything before, You are a professional political journalist, you have been in the industry for more than 20 years."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000
    )

    grouped_summary = response['choices'][0]['message']['content'].strip()
    logging.info("Grouped summaries by topics.")
    return grouped_summary

async def async_send_text_to_telegram(bot, chat_id, text):
    await bot.send_message(chat_id=chat_id, text=text)
    logging.info("Message sent to Telegram.")

def send_text_to_telegram(text):
    bot_token = BotSetting.objects.get(name='TELEGRAM_BOT_TOKEN').value
    chat_id = BotSetting.objects.get(name='TELEGRAM_CHAT_ID').value
    bot = telegram.Bot(token=bot_token)

    logging.info(f"Sending message to Telegram chat_id: {chat_id}")
    asyncio.run(async_send_text_to_telegram(bot, chat_id, text))

def fetch_all_news():
    now = datetime.now()
    if now.hour == 8:
        report_title = "Morning Summary"
    elif now.hour == 23 and now.minute == 30:
        report_title = "Evening Summary"
    else:
        report_title = "Summary"

    website_news = fetch_news_from_websites()
    grouped_summary = group_summaries_by_topics(website_news)

    final_summary = f"{report_title}:\n\n{grouped_summary}"
    logging.info("Final summary prepared.")

    # Send the grouped summary to Telegram
    send_text_to_telegram(final_summary)

    return final_summary
