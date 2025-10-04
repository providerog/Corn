# Don't remove This Line From Here. Tg: @rohit_1888 | @Javpostr

import asyncio
import tempfile
import base64
import os
from datetime import datetime
from pyrogram import filters, Client, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode, ChatAction
from bot import Bot
from config import *
from Database.database import *
from helper_func import *

DB_CHANNEL = CHANNEL_ID
FILE_SIZE_LIMIT = 1 * 1024 * 1024 * 1024  # 1GB limit


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



async def fetch_and_upload_content(client: Client, message: Message):
    """Fetches restricted content, processes it, and uploads it with header and footer."""
    # Extract the link from text or caption
    link = None
    if "https://t.me/" in (message.text or ""):
        link = next((word for word in message.text.split() if "https://t.me/" in word and "?start=" in word), None)
    elif "https://t.me/" in (message.caption or ""):
        link = next((word for word in message.caption.split() if "https://t.me/" in word and "?start=" in word), None)

    if not link:
        return  # Ignore messages without valid links

    try:
        # Parse the link
        link_parts = link.split("?start=")
        bot_username = link_parts[0].split("/")[-1]
        start_param = link_parts[1] if len(link_parts) > 1 else None

        # Retrieve session
        user_session = await db.get_session(message.from_user.id)
        if not user_session:
            return await message.reply_text("You need to /login first to fetch content.")

        # Start client session
        acc = Client("restricted_content", session_string=user_session, api_id=API_ID, api_hash=API_HASH)
        await acc.start()

        # Send /start command
        sent_message = await acc.send_message(bot_username, f"/start {start_param}" if start_param else "/start")

        # Wait and fetch the latest messages
        await asyncio.sleep(10)
        messages = []
        async for response in acc.get_chat_history(bot_username, limit=100):
            if response.date > sent_message.date:
                msg_type = get_message_type(response)
                if msg_type:
                    messages.append((msg_type, response))

        if not messages:
            return await message.reply_text("No new messages received after sending the link.")

        # Process and upload messages
        uploaded_links = []
        message_ids = []
        for msg_type, response in messages:
            db_msg = await process_and_upload(client, acc, msg_type, response)
            if db_msg:
                uploaded_links.append(f"https://t.me/c/{str(abs(DB_CHANNEL))}/{db_msg.id}")
                message_ids.append(db_msg.id)

        # Generate encoded link
        if uploaded_links:
            if len(message_ids) == 1:
                converted_id = message_ids[0] * abs(client.db_channel.id)
                string = f"get-{converted_id}"
            else:
                f_msg_id = message_ids[0] * abs(client.db_channel.id)
                s_msg_id = message_ids[-1] * abs(client.db_channel.id) if len(message_ids) > 1 else 0
                string = f"get-{f_msg_id}-{s_msg_id}"

            base64_string = encode(string)
            new_link = f"https://t.me/{client.username}?start={base64_string}"

            # Fetch header and footer from the database
            header = await db.get_header(message.from_user.id) or ""
            footer = await db.get_footer(message.from_user.id) or ""

            # Get the caption state (whether it's enabled or not)
            caption_enabled = await db.get_caption_state(message.from_user.id) or ""

            # Combine header, link, and footer
            final_message = f"{header}\n\n<b>Your content has been processed successfully:</b>\n{new_link}\n\n{footer}"

            # Replace only the link in the caption
            if message.caption and caption_enabled:  # For photo messages with captions and captions enabled
                updated_caption = f"{header}\n\n{message.caption.replace(link, new_link)}\n\n{footer}"
                await message.reply_photo(
                    photo=message.photo.file_id,
                    caption=updated_caption,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔗 Share Link", url=f'https://telegram.me/share/url?url={new_link}')]
                    ])
                )
            else:  # For text messages or captions without a photo, or if captions are disabled
                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 Share Link", url=f'https://telegram.me/share/url?url={new_link}')]
                ])
                await message.reply_text(
                    final_message,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                )
        else:  # No uploaded links; handle with header and footer
            header = await db.get_header(message.from_user.id) or ""
            footer = await db.get_footer(message.from_user.id) or ""
            no_content_message = f"{header}\n\n<b>No new content was fetched after processing your link.</b>\n\n{footer}"
            await message.reply_text(no_content_message)

    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

    finally:
        # Ensure to stop the client session if it was started
        if 'acc' in locals():
            await acc.stop()

async def process_and_upload(client, acc, msg_type, response):
    """Processes and uploads a single message to the database channel."""
    temp_file_path = None
    db_msg = None
    try:
        if msg_type in ["Document", "Video", "Photo", "Audio", "Animation"]:
            # Use the original file name for media, ensuring proper file extension
            if msg_type == "Photo":
                temp_file_path = await acc.download_media(response.photo, file_name=f"{response.photo.file_id}.jpg")
                db_msg = await client.send_photo(DB_CHANNEL, temp_file_path, caption=response.caption)

            elif msg_type == "Video":
                temp_file_path = await acc.download_media(response.video, file_name=f"{response.video.file_id}.mp4")
                db_msg = await client.send_video(
                    DB_CHANNEL,
                    temp_file_path,
                    caption=response.caption,
                    duration=response.video.duration,  # Pass the duration
                    width=response.video.width,  # Pass width and height
                    height=response.video.height
                )

            elif msg_type == "Audio":
                temp_file_path = await acc.download_media(response.audio, file_name=f"{response.audio.file_id}.mp3")
                db_msg = await client.send_audio(
                    DB_CHANNEL,
                    temp_file_path,
                    caption=response.caption,
                    duration=response.audio.duration,  # Pass the duration
                    performer=response.audio.performer,  # Optional: Retain performer
                    title=response.audio.title  # Optional: Retain title
                )

            elif msg_type == "Document":
                temp_file_path = await acc.download_media(response.document, file_name=response.document.file_name)
                db_msg = await client.send_document(DB_CHANNEL, temp_file_path, caption=response.caption)

            elif msg_type == "Animation":
                temp_file_path = await acc.download_media(response.animation, file_name=f"{response.animation.file_id}.gif")
                db_msg = await client.send_animation(DB_CHANNEL, temp_file_path, caption=response.caption)

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    return db_msg  # Return the uploaded message object

async def upload_to_db(client, msg_type, file_path, caption):
    """Uploads media to the database channel."""
    if msg_type == "Photo":
        return await client.send_photo(DB_CHANNEL, file_path, caption=caption, parse_mode=enums.ParseMode.HTML)
    elif msg_type == "Video":
        return await client.send_video(DB_CHANNEL, file_path, caption=caption, parse_mode=enums.ParseMode.HTML)
    elif msg_type == "Audio":
        return await client.send_audio(DB_CHANNEL, file_path, caption=caption, parse_mode=enums.ParseMode.HTML)
    elif msg_type == "Document":
        return await client.send_document(DB_CHANNEL, file_path, caption=caption, parse_mode=enums.ParseMode.HTML)
    elif msg_type == "Animation":
        return await client.send_animation(DB_CHANNEL, file_path, caption=caption, parse_mode=enums.ParseMode.HTML)


def get_message_type(msg):
    """Identifies the type of the message."""
    if msg.document: return "Document"
    if msg.video: return "Video"
    if msg.animation: return "Animation"
    if msg.audio: return "Audio"
    if msg.photo: return "Photo"
    if msg.text: return "Text"
    return None