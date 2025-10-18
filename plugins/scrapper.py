import asyncio
from pyrogram import filters
from pyrogram.types import Message
from bot import Bot
from Database.database import db
from config import API_ID, API_HASH, OWNER_ID
from pyrogram import Client
from helper_func import is_admin

async def process_scrape_task(client, task):
    """
    Processes a scrape task from the queue.
    """
    client.LOGGER(__name__).info(f"Processing scrape task: {task}")
    try:
        message = task
        # Use the owner's session to fetch the content
        if not client.scraper_client:
            client.LOGGER(__name__).warning("Scraper client not available. Skipping task.")
            return

        # Upload the message to the DB channel
        db_msg = await message.copy(chat_id=client.db_channel.id)

        # Add the file to the scraped_files collection
        file_name = ""
        if message.document:
            file_name = message.document.file_name
        elif message.video:
            file_name = message.video.file_name

        await db.add_scraped_file(file_name, db_msg.id, message.caption)

        client.LOGGER(__name__).info(f"Successfully scraped and stored message: {db_msg.id}")

    except Exception as e:
        client.LOGGER(__name__).error(f"Error processing scrape task: {e}")


@Bot.on_message(filters.private & filters.forwarded & is_admin)
async def automatic_scrape(client: Bot, message: Message):
    """
    Adds a forwarded message to the scrape queue.
    """
    await client.scrape_queue.put(message)
    await message.reply_text("Added to the scrape queue.")
