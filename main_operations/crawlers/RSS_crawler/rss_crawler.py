import json
import os

import feedparser
import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
import aiofiles

from content.news_file_extractor import get_language_name_by_code
from main_operations.main_function import regenerate_function

rss_list = "_rss_list"
rss_sites = "_rss_sites"


async def show_all_topics_function():
    directory = "RSS_news"

    try:
        items = os.listdir(directory)

        folders = [item for item in items if os.path.isdir(os.path.join(directory, item))]
        results = []
        for folder in folders:
            topic = folder.replace(rss_list, "")
            topic = topic.replace(rss_sites, "")

            if topic not in results:
                results.append(topic)

        return results

    except Exception as e:
        print(f"An error occurred: {e}")


async def add_by_rss_function(url, topic):
    if not os.path.exists("RSS_news"):
        os.makedirs("RSS_news")

    if not os.path.exists(f"RSS_news/{topic}{rss_list}"):
        os.makedirs(f"RSS_news/{topic}{rss_list}")

    filename = f"RSS_news/{topic}{rss_list}/rss_{topic}.json"

    data = {
        "feeds": []
    }

    try:
        async with aiofiles.open(filename, 'r') as file:
            content = await file.read()
            if content:
                data = json.loads(content)
    except FileNotFoundError:
        pass

    for feed in data["feeds"]:
        if feed["url"] == url:
            raise HTTPException(status_code=400, detail="This RSS feed already exists.")

    new_feed = {
        "url": url,
        "topic": topic
    }
    data["feeds"].append(new_feed)

    async with aiofiles.open(filename, 'w') as file:
        await file.write(json.dumps(data, ensure_ascii=False, indent=4))

    return {"message": "RSS feed added successfully"}


async def extract_all_rss_function(topic):
    directory = "RSS_news"
    directory2 = f"RSS_news/{topic}{rss_list}"

    if not os.path.exists(directory):
        os.makedirs(directory)

    # if not os.path.exists(directory2):
    #     os.makedirs(directory2)

    filename = f"{directory2}/rss_{topic}.json"
    data = {
        "feeds": []
    }

    try:
        async with aiofiles.open(filename, 'r', encoding='utf-8') as file:
            content = await file.read()
            if content:
                data = json.loads(content)
                return data["feeds"]
    except FileNotFoundError:
        pass
    return data["feeds"]


async def check_by_rss_by_url_function(rss_url):
    try:
        feed = feedparser.parse(rss_url)
        test_topic = "crypto"
        test_language = ["english", "german", "russian"]
        test_rss = feed.entries[1].link
        print(test_rss)
        url = test_rss

        session = requests.Session()

        try:
            response = session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            result = await regenerate_function(soup, test_language, test_topic, url, "test")

            return result
        except requests.exceptions.RequestException as e:
            return f"Error: {e}"
    except Exception as e:
        print(f"Problem with RSS: {e}")
        return "Problem with RSS url"


async def delete_article_by_url_function(url_to_delete, topic, language):
    topic = topic.lower()
    language = language.lower()
    language = get_language_name_by_code(language)
    file_path = f"news_json/{topic}/{topic}_{language}.json"

    if not os.path.isfile(file_path):
        return {"error": "This topic does not exist. Use existing topic and language."}

    with open(file_path, 'r', encoding='utf-8') as file:
        articles = json.load(file)

    length = len(articles)
    for article in articles:
        if article.get("url_part") == url_to_delete:
            articles.remove(article)
            break
    new_length = len(articles)

    if length == new_length:
        return {"error": "Article not found."}
    else:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(articles, file, indent=4)

        return {"message": "Article deleted successfully"}
