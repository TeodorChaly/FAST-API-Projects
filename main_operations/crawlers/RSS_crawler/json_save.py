import json
import os
from urllib.parse import urlparse

import feedparser
import requests

from configs.config_setup import main_site_topic
from content.news_file_extractor import get_language_name_by_code


async def rss_list_saver(url, topic):
    try:
        print(f"Processing RSS feed: {url}")
        domain = urlparse(url).netloc.replace('.', '_')

        rss_url = url

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }

        response = requests.get(rss_url, timeout=10, headers=headers)
        response.raise_for_status()
        feed = feedparser.parse(response.content)

        unique_links = set()

        for entry in feed.entries:
            unique_links.add(entry.link)

        if not os.path.exists(f'RSS_news/{topic}_rss_sites'):
            os.makedirs(f'RSS_news/{topic}_rss_sites')

        filename = f'RSS_news/{topic}_rss_sites/{domain}_rss.json'
        max_entries = 1000  # Maximum number of entries to keep in the file
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        existing_links = set()
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                try:
                    json_data = json.load(f)
                    existing_links = set(json_data)
                except Exception as e:
                    print("File open error", e)

        new_links = list(unique_links - existing_links)
        combined_links = new_links + list(existing_links)
        combined_links = combined_links[:max_entries]

        with open(filename, 'w') as f:
            json.dump(combined_links, f, indent=4)
        return new_links
    except Exception as e:
        print(f"An error occurred: {e}")


def process_json(input_json):
    start_key = '"rewritten_content":'
    end_key = '"seo_title":'

    start_index = input_json.find(start_key) + len(start_key)
    if start_index == -1:
        print("Error no 'rewritten_content'")
        return None

    end_index = input_json.find(end_key, start_index)
    if end_index == -1:
        print("Error no 'seo_title'")
        return None

    value_start_index = input_json.find('"', start_index) + 1
    value_end_index = input_json.find('"seo_title"', value_start_index) - 7
    if value_start_index == -1 or value_end_index == -1:
        print("Error no 'rewritten_content' content")
        return None

    content = input_json[value_start_index:value_end_index]
    content = content.replace('"', r'\"')
    fixed_json = (input_json[:value_start_index] + content +
                  input_json[value_end_index:])
    return fixed_json


async def get_link_source(url_to_delete, language):
    try:
        topic = main_site_topic
        language = language.lower()
        language = get_language_name_by_code(language)
        file_path = f"news_json/{topic}/{topic}_{language}.json"

        if not os.path.isfile(file_path):
            return {"error": "This topic does not exist. Use existing topic and language."}

        with open(file_path, 'r', encoding='utf-8') as file:
            articles = json.load(file)

        for article in articles:
            if article.get("url_part") == url_to_delete:
                return article.get("url")
        return {"error": "Article not found."}

    except Exception as e:
        print(f"Error: {e}")
        return "Error"


def test_rss(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    list1 = rss_list_saver(url, "r")
    print(requests.get(list1[0], headers=headers))
