import os

import json
import logging
from pathlib import Path
from fastapi import FastAPI
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles
from starlette.requests import Request

from languages.router import router as languages_router
from configs.prepare_config_file import create_config_file

create_config_file()

from main_operations.crawlers.RSS_crawler.router import router as crawler_router
from main_operations.router import router as scraping_router
from configs.robots import router as robots_router
from configs.sitemap import router as sitemap_router
from content.router import router as topics_router
from other_content.router import router as other_content_router

logging.basicConfig(
    filename='access.log',
    level=logging.INFO,
    format='%(asctime)s - IP: %(clientip)s, User-Agent: %(useragent)s, Method: %(method)s, Path: %(path)s'
)

app = FastAPI(
    title="News generator API",
    version="0.1"
)

app.mount("/assets", StaticFiles(directory="templates/assets"), name="assets")


@app.on_event("startup")
async def startup_event():
    file_path = "languages/languages.json"
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(["english"], file)

    if not os.path.exists("scraped_urls.json"):
        with open("scraped_urls.json", 'w', encoding='utf-8') as file:
            json.dump([], file)

    if not os.path.exists("news_json"):
        os.makedirs("news_json")


# Middleware production
@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    client_ip = request.client.host
    user_agent = request.headers.get('user-agent', 'Unknown')
    method = request.method
    path = request.url.path

    blocked_paths = ["/Image not found", "/imagen/3923384"]

    if not path.startswith("/get_images/") and not path.startswith("/assets") and path not in blocked_paths:
        logging.info(
            '',
            extra={
                'clientip': client_ip,
                'useragent': user_agent,
                'method': method,
                'path': path
            }
        )

    response = await call_next(request)
    return response


@app.get('/get_images/image')
async def serve_image(topic, img):
    current_file_path = os.path.abspath(__file__)
    main_directory = os.path.dirname(current_file_path)
    folder_name = os.path.join(main_directory, "news_json")
    reserve_directory = os.path.join(folder_name, topic)
    save_directory = os.path.join(reserve_directory, "main_images")
    name_file = img
    result_directory = Path(os.path.join(save_directory, name_file))  # For Linux
    # result_directory = Path(os.path.join(save_directory, name_file).replace("/", "\\"))
    try:
        if result_directory.exists():
            return FileResponse(result_directory)
        else:
            return {"error": "File not found"}
    except Exception as e:
        print("Image error", e)
        return {"error": "File don t exist"}


app.include_router(robots_router)
app.include_router(sitemap_router)
app.include_router(crawler_router)
app.include_router(other_content_router)
app.include_router(languages_router)
app.include_router(topics_router)
app.include_router(scraping_router)
