# coding=utf-8

import platform
from DrissionPage import Chromium, ChromiumOptions
import os
import atexit
import asyncio
from rss_parser import RSSParser
import httpx
from loguru import logger
from dateutil import parser as date_parser
from pathvalidate import sanitize_filename
import shutil
import argparse
from tenacity import (
    retry,
    stop_after_attempt,
    stop_after_delay,
    wait_random,
    before_log,
    after_log,
    before_sleep_log,
)
import sys as _sys
from pathlib import Path
from markitdown import MarkItDown


@retry(
    stop=stop_after_attempt(3) | stop_after_delay(60),
    wait=wait_random(min=1, max=2),
    before=before_log(logger, "DEBUG"),
    after=after_log(logger, "DEBUG"),
    before_sleep=before_sleep_log(logger, "DEBUG"),
)
def save_as_md(save_filepath, link):
    """Save web page as PDF and convert to Markdown
    
    Args:
        save_filepath (str): Path to save the PDF file
        link (str): URL of the web page to save
    """
    logger.info(f"Starting PDF save task; URL:{link}; Save path:{save_filepath}")
    _tab = browser.new_tab()
    _tab.get(link)
    try:
        # Save page as PDF
        _tab.save(path=save_filepath, as_pdf=True)
        logger.info(f"Saved URL {link} as PDF; Save path:{save_filepath}")
        
        # Convert PDF to Markdown
        md = MarkItDown(enable_plugins=False)  # Set to True to enable plugins
        md_filepath = os.path.splitext(save_filepath)[0] + '.md'
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(md.convert(save_filepath).text_content)
        
        # Remove the temporary PDF file
        os.remove(save_filepath)
    except Exception:
        import traceback
        traceback.print_exc()
    finally:
        _tab.close()


async def async_save_as_md(save_filepath, link, semaphore):
    """Asynchronous version of save_as_md with semaphore for concurrency control
    
    Args:
        save_filepath (str): Path to save the PDF file
        link (str): URL of the web page to save
        semaphore (asyncio.Semaphore): Semaphore for limiting concurrent tasks
    """
    async with semaphore:
        await asyncio.to_thread(save_as_md, save_filepath, link)



async def export_pdf_from_rss(rss_url, semaphore):
    """Fetch articles from RSS feed and save them as Markdown
    
    Args:
        rss_url (str): URL of the RSS feed
        semaphore (asyncio.Semaphore): Semaphore for limiting concurrent tasks
    
    Returns:
        List[asyncio.Task]: List of asynchronous save tasks
    """
    async with httpx.AsyncClient() as client:
        all_article = []
        response = await client.get(rss_url)
        rss = RSSParser.parse(response.text)
        lang = rss.channel.language.content
        rss_channel_name = rss.channel.title.content
        version = rss.version.content
        logger.info(
            f"Fetched: {rss_channel_name}({rss_url}); Language: {lang}; RSS Version: {version}"
        )
        
        # Process each item in the RSS feed
        for item in rss.channel.items:
            title = item.title.content
            description = item.description.content
            links = [i.content for i in item.links]
            time_create = date_parser.parser().parse(str(item.pub_date.content))
            date_create = f"{time_create:%Y%m%d%H%M%S}"
            
            # Filter articles by specified date
            if date_create.startswith(date_):
                all_article.extend(
                    [
                        (
                            f"{title}" + ("-{i}" if i != 0 else ""),
                            link,
                            date_create,
                            description,
                        )
                        for i, link in enumerate(links)
                    ]
                )
        
        # Create save tasks for each article
        tasks = []
        for title, link, date_create, description in all_article:
            save_filepath = os.path.join(
                save_path,
                (
                    sanitize_filename(
                        date_create + "_" + rss_channel_name + "_" + title
                    )
                    + ".pdf"
                ),
            )
            if not os.path.exists(save_filepath):
                tasks.append(
                    asyncio.create_task(
                        async_save_as_md(save_filepath, link, semaphore)
                    )
                )
        return tasks


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Save WeChat official account articles as Markdown from RSS feed")
    parser.add_argument("-u", "--url", required=True, help="URL of the we-mp-rss platform")
    parser.add_argument(
        "-d", "--date", required=True, help="Publication date of articles to save (e.g., 20260203)"
    )
    parser.add_argument("-o", "--output", required=True, help="Output directory path")
    args = parser.parse_args()
    
    # Initialize configuration
    rss_url = str(args.url).rstrip("/") + "/feed/all.rss"
    save_path = args.output
    os.makedirs(save_path, exist_ok=True)
    date_ = args.date
    
    # Configure logger
    logger.remove()
    logger.add(_sys.stderr, level="DEBUG")

    # Configure browser options
    co = (
        ChromiumOptions()
        .set_user_data_path("./browser_user_data")
        .mute(True)
        .no_imgs(False)
    )

    # Platform-specific browser configuration
    if platform.system() == "Linux":
        co.set_argument("--headless=new")
        co.set_argument("--no-sandbox")
        co.set_browser_path(shutil.which("chromium-browser"))
        co.set_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
    elif platform.system() == "Windows":
        # co.set_browser_path(
        #     (Path(__file__).parent.parent / "chromium_144" / "chrome.exe").__str__()
        # )
        co.set_argument("--start-maximized")

    # Initialize browser
    browser = Chromium(addr_or_opts=co)
    atexit.register(lambda: browser.quit(del_data=True))
    
    # Configure concurrency
    parallal = int(os.environ.get("parallal", 10))
    logger.info(f"Concurrency level: {parallal}")

    async def main():
        """Main asynchronous function to fetch and save articles"""
        tasks = []
        semaphore = asyncio.Semaphore(parallal)
        tasks.extend(await export_pdf_from_rss(rss_url, semaphore))
        await asyncio.gather(*tasks)

    asyncio.run(main())
