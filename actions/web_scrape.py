"""Web scraping module."""
from __future__ import annotations

import requests
import asyncio
from pathlib import Path

from fastapi import WebSocket

import processing.text as summary

from config import Config

from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

FILE_DIR = Path(__file__).parent.parent
CFG = Config()


async def async_browse(url: str, question: str, websocket: WebSocket) -> str:
    """Browse a website and return the answer and links to the user

    Args:
        url (str): The url of the website to browse
        question (str): The question asked by the user
        websocket (WebSocketManager): The websocket manager

    Returns:
        str: The answer and links to the user
    """
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=8)

    print(f"Scraping url {url} with question {question}")
    await websocket.send_json(
        {"type": "logs", "output": f"🔎 Browsing the {url} for relevant about: {question}..."})

    try:
        text = await loop.run_in_executor(executor, get_text, url)
        summary_text = await loop.run_in_executor(executor, summary.summarize_text, url, text, question)

        await websocket.send_json(
            {"type": "logs", "output": f"📝 Information gathered from url {url}: {summary_text}"})

        return f"Information gathered from url {url}: {summary_text}"
    except Exception as e:
        print(f"An error occurred while processing the url {url}: {e}")
        return f"Error processing the url {url}: {e}"



def get_text(url: str) -> str:
    return requests.get("http://0.0.0.0:8080/text?url=" + url).text
