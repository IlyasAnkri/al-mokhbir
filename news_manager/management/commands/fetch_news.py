from django.core.management.base import BaseCommand
from news_manager.news_fetcher import fetch_all_news
import logging

class Command(BaseCommand):
    help = 'Fetch, group by topics, and send news to Telegram'

    def handle(self, *args, **kwargs):
        logging.info("Starting fetch_all_news...")
        grouped_summary = fetch_all_news()
        self.stdout.write(self.style.SUCCESS("News summary grouped and sent to Telegram"))
        logging.info("Completed fetch_all_news.")
