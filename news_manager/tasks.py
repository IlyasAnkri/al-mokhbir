from celery import shared_task
from .news_fetcher import fetch_all_news

@shared_task
def fetch_and_send_news():
    fetch_all_news()
