# Don't remove This Line From Here. Tg: @rohit_1888 | @Javpostr

import asyncio
import tempfile
import base64
import os
from datetime import datetime
from pyrogram import filters, Client, enums
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaDocument
)
from pyrogram.enums import ParseMode, ChatAction
from bot import Bot
from config import *
from database.database import *
from helper_func import *

DB_CHANNEL = CHANNEL_ID
FILE_SIZE_LIMIT = 1 * 1024 * 1024 * 1024  # 1GB limit

# Create a queue to hold incoming messages for processing
processing_queue = asyncio.Queue()
PROCESSED_MEDIA_GROUPS = set()



def encode(data: str) -> str:
    """Encodes the input data into a base64 format with stripped padding."""
    encoded = base64.urlsafe_b64encode(data.encode("utf-8")).decode("utf-8")
    return encoded.strip("=")  # Strip padding for cleaner URLs


async def decode(base64_string: str) -> list:
    """Decodes a base64 string and returns a list of message IDs."""
    base64_string = base64_string.strip("=")
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string = base64.urlsafe_b64decode(base64_bytes).decode("utf-8")

    # Parse the string to extract message IDs
    if string.startswith("get-"):
        ids = string[4:].split(",")
        return [int(msg_id) for msg_id in ids]  # Convert IDs back to integers
    return []


@Bot.on_message(filters.private & is_admin & ~filters.command([
    'start', 'users', 'broadcast', 'batch', 'genlink', 'stats', 'addpaid', 'removepaid', 'listpaid',
    'help', 'cmd', 'info', 'add_fsub', 'fsub_chnl', 'restart', 'del_fsub', 'add_admins', 'del_admins',
    'admin_list', 'cancel', 'auto_del', 'forcesub', 'files', 'add_banuser', 'token', 'del_banuser', 'banuser_list',
    'status', 'req_fsub', 'myplan', 'login', 'header', 'footer', 'save', 'caption', 'logout', 'short']))
async def message_handler(client: Client, message: Message):
    """Adds incoming messages to the processing queue."""
    await processing_queue.put(message)
    await message.reply_text("Your file has been added to the queue and will be processed shortly.")


async def process_message(client: Client, message: Message):
    """Processes forwarded files, media groups, and links."""

    # Handle direct file forwards and media groups
    if (message.media and not message.text) or (message.media_group_id and message.media_group_id not in PROCESSED_MEDIA_GROUPS):
        if message.media_group_id:
            media_group = await client.get_media_group(message.chat.id, message.id)
            db_messages = await client.copy_media_group(DB_CHANNEL, message.chat.id, media_group[0].id)
            message_ids = [msg.id for msg in db_messages]
            PROCESSED_MEDIA_GROUPS.add(message.media_group_id)
        else:
            db_message = await message.copy(DB_CHANNEL)
            message_ids = [db_message.id]

        # Generate link
        if len(message_ids) == 1:
            string = f"get-{message_ids[0] * abs(client.db_channel.id)}"
        else:
            string = f"get-{message_ids[0] * abs(client.db_channel.id)}-{message_ids[-1] * abs(client.db_channel.id)}"

        base64_string = encode(string)
        new_link = f"https.t.me/{client.username}?start={base64_string}"

        # Reply with the link
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Share Link", url=f'https://telegram.me/share/url?url={new_link}')]])
        await message.reply_text(f"<b>Your file has been saved successfully!</b>\n\n{new_link}", reply_markup=reply_markup, disable_web_page_preview=True)
        return

    # Fallback to handle links
    link = None
    if "https://t.me/" in (message.text or ""):
        link = next((word for word in message.text.split() if "https://t.me/" in word and "?start=" in word), None)
    elif "https://t.me/" in (message.caption or ""):
        link = next((word for word in message.caption.split() if "https://t.me/" in word and "?start=" in word), None)

    if link:
        try:
            link_parts = link.split("?start=")
            bot_username = link_parts[0].split("/")[-1]
            start_param = link_parts[1] if len(link_parts) > 1 else None

            user_session = await db.get_session(message.from_user.id)
            if not user_session:
                return await message.reply_text("You need to /login first to fetch content.")

            acc = Client("restricted_content", session_string=user_session, api_id=API_ID, api_hash=API_HASH)
            await acc.start()

            sent_message = await acc.send_message(bot_username, f"/start {start_param}" if start_param else "/start")
            await asyncio.sleep(10)

            messages_from_bot = []
            async for response in acc.get_chat_history(bot_username, limit=100):
                if response.date > sent_message.date:
                    messages_from_bot.append(response)

            if not messages_from_bot:
                return await message.reply_text("No new messages received after sending the link.")

            uploaded_links = []
            message_ids = []
            processed_media_groups_bot = set()

            for msg_from_bot in messages_from_bot:
                if msg_from_bot.media_group_id and msg_from_bot.media_group_id not in processed_media_groups_bot:
                    media_group = await acc.get_media_group(msg_from_bot.chat.id, msg_from_bot.id)
                    db_msgs = await acc.copy_media_group(DB_CHANNEL, msg_from_bot.chat.id, media_group[0].id)
                    for db_msg in db_msgs:
                        message_ids.append(db_msg.id)
                    processed_media_groups_bot.add(msg_from_bot.media_group_id)
                elif not msg_from_bot.media_group_id:
                    db_msg = await msg_from_bot.copy(DB_CHANNEL)
                    message_ids.append(db_msg.id)

            if message_ids:
                if len(message_ids) == 1:
                    string = f"get-{message_ids[0] * abs(client.db_channel.id)}"
                else:
                    string = f"get-{message_ids[0] * abs(client.db_channel.id)}-{message_ids[-1] * abs(client.db_channel.id)}"

                base64_string = encode(string)
                new_link = f"https.t.me/{client.username}?start={base64_string}"

                header = await db.get_header(message.from_user.id) or ""
                footer = await db.get_footer(message.from_user.id) or ""
                final_message = f"{header}\n\n<b>Your content has been processed successfully:</b>\n{new_link}\n\n{footer}"

                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Share Link", url=f'https://telegram.me/share/url?url={new_link}')]])
                await message.reply_text(final_message, reply_markup=reply_markup, disable_web_page_preview=True)

        except Exception as e:
            await message.reply_text(f"An error occurred: {e}")
        finally:
            if 'acc' in locals() and acc.is_connected:
                await acc.stop()


async def queue_worker(client: Client):
    """Monitors the queue and processes messages."""
    while True:
        message = await processing_queue.get()
        try:
            await process_message(client, message)
        except Exception as e:
            print(f"Error processing message from queue: {e}")
            await message.reply_text(f"Sorry, an error occurred while processing your file: {e}")
        finally:
            processing_queue.task_done()

def start_queue_worker(client: Client):
    """Creates and starts the background queue worker task."""
    asyncio.create_task(queue_worker(client))
