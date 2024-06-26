from fastapi import APIRouter
from fastapi.params import Query

from main_operations.crawlers.RSS_crawler.json_save import rss_list_saver
from main_operations.crawlers.RSS_crawler.rss_crawler import *
from main_operations.router import scraper_fun

router = APIRouter()


@router.post("/crawler_by_RSS", tags=["RSS crawler"])
async def crawler_by_rss_or_feed(topic: str = Query(..., description="Topic"), google: bool = Query(False)):
    list_of_feeds = await extract_all_rss_function(topic)
    new_links_number = 0
    new_links = []
    for feed in list_of_feeds:
        results = await rss_list_saver(feed["url"], feed["topic"])
        new_links_number += len(results)
        new_links.append(results)

    counter = 0
    for urls in new_links:
        for _ in urls:
            counter += 1

    # Fix
    if counter < 10:
        for urls in new_links:
            for url in urls:
                if google:
                    print(f"Scraping for {url}")
                    await scraper_fun(url, topic, google=True)
                else:
                    await scraper_fun(url, topic)
    else:
        print("Too many new links. Not scraping.")

    print(f"RSS list was scraped. New - {new_links_number}")
    return f"RSS scraped. New - {new_links_number}"


@router.post("/add_rss_url", tags=["RSS config"])
async def add_by_rss_by_url(url: str = Query(..., description="URL to RSS"),
                            topic: str = Query(..., description="Topic")):
    return await add_by_rss_function(url, topic)


@router.get("/list_of_rss", tags=["RSS config"])
async def extract_all_rss(topic: str):
    return await extract_all_rss_function(topic)


@router.get("/check_rss_url", tags=["RSS config"])
async def check_by_rss_by_url(url: str = Query(..., description="URL to RSS")):
    result = await check_by_rss_by_url_function(url)
    return result
