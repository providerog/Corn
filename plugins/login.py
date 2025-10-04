import traceback
from bot import Bot
from pyrogram.types import Message
from pyrogram import Client, filters
from asyncio.exceptions import TimeoutError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from config import *
from helper_func import*
from database.database import *
from plugins.query import *

SESSION_STRING_SIZE = 351

@Bot.on_message(filters.private & is_admin & filters.command('logout'))
async def logout(client, message):
    user_data = await db.get_session(message.from_user.id)  
    if user_data is None:
        return 
    await db.set_session(message.from_user.id, session=None)  
    await message.reply("**Logout Successfully** ♦")

@Bot.on_message(filters.private & is_admin & filters.command('login'))
async def main(bot: Client, message: Message):
    user_data = await db.get_session(message.from_user.id)
    if user_data is not None:
        await message.reply("**Your Are Already Logged In. First /logout Your Old Session. Then Do Login.**")
        return 
    user_id = int(message.from_user.id)
    phone_number_msg = await bot.ask(chat_id=user_id, text="<b>Please send your phone number which includes country code</b>\n<b>Example:</b> <code>+13124562345, +9171828181889</code>")
    if phone_number_msg.text=='/cancel':
        return await phone_number_msg.reply('<b>process cancelled !</b>')
    phone_number = phone_number_msg.text
    client = Client(":memory:", API_ID, API_HASH)
    await client.connect()
    await phone_number_msg.reply("Sending OTP...")
    try:
        code = await client.send_code(phone_number)
        phone_code_msg = await bot.ask(user_id, "Please check for an OTP in official telegram account. If you got it, send OTP here after reading the below format. \n\nIf OTP is `12345`, **please send it as** `1 2 3 4 5`.\n\n**Enter /cancel to cancel The Procces**", filters=filters.text, timeout=600)
    except PhoneNumberInvalid:
        await phone_number_msg.reply('`PHONE_NUMBER` **is invalid.**')
        return
    if phone_code_msg.text=='/cancel':
        return await phone_code_msg.reply('<b>process cancelled !</b>')
    try:
        phone_code = phone_code_msg.text.replace(" ", "")
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        await phone_code_msg.reply('**OTP is invalid.**')
        return
    except PhoneCodeExpired:
        await phone_code_msg.reply('**OTP is expired.**')
        return
    except SessionPasswordNeeded:
        two_step_msg = await bot.ask(user_id, '**Your account has enabled two-step verification. Please provide the password.\n\nEnter /cancel to cancel The Procces**', filters=filters.text, timeout=300)
        if two_step_msg.text=='/cancel':
            return await two_step_msg.reply('<b>process cancelled !</b>')
        try:
            password = two_step_msg.text
            await client.check_password(password=password)
        except PasswordHashInvalid:
            await two_step_msg.reply('**Invalid Password Provided**')
            return
    string_session = await client.export_session_string()
    await client.disconnect()
    if len(string_session) < SESSION_STRING_SIZE:
        return await message.reply('<b>invalid session sring</b>')
    try:
        user_data = await db.get_session(message.from_user.id)
        if user_data is None:
            uclient = Client(":memory:", session_string=string_session, api_id=API_ID, api_hash=API_HASH)
            await uclient.connect()
            await db.set_session(message.from_user.id, session=string_session)
    except Exception as e:
        return await message.reply_text(f"<b>ERROR IN LOGIN:</b> `{e}`")
    await bot.send_message(message.from_user.id, "<b>Account Login Successfully.\n\nIf You Get Any Error Then /logout first and /login again</b>")


@Bot.on_message(filters.command('header') & filters.private & is_admin)
async def set_header(client, message):
    await message.reply_chat_action(ChatAction.TYPING)

    try:
        # Fetch header status and text from the database
        header_text = await db.get_header(message.from_user.id)
        if header_text:
            header_status = "Enabled ✅"
            mode_button = InlineKeyboardButton('Disable Header ❌', callback_data='disable_header')
        else:
            header_status = "Disabled ❌"
            mode_button = InlineKeyboardButton('Enable Header ✅', callback_data='set_header')

        # Send the settings message with options
        caption = f"🔖 **Header Settings**\n\n**Header Status:** {header_status}\n\nUse the options below to configure the header."

        if header_text:
            caption += f"\n\n**Current Header Text:**\n{header_text}"

        await message.reply_photo(
            photo=START_PIC,
            caption=caption,
            reply_markup=InlineKeyboardMarkup([
                [mode_button],
                [InlineKeyboardButton('Set Header', callback_data='set_header')],
                [InlineKeyboardButton('Close ✖️', callback_data='close')]
            ])
        )
    except Exception as e:
        # Log and send error
        logging.error(f"Error in set_header command: {e}")
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Close ✖️", callback_data="close")]])
        await message.reply(
            (
                f"❌ **Error Occurred:**\n\n"
                f"**Reason:** {e}\n\n"
                f"📩 Contact developer: [Rohit](https://t.me/rohit_1888)"
            ),
            reply_markup=reply_markup
        )

@Bot.on_message(filters.command('footer') & filters.private & is_admin)
async def set_footer(client, message):
    await message.reply_chat_action(ChatAction.TYPING)

    try:
        # Fetch footer status and text from the database
        footer_text = await db.get_footer(message.from_user.id)
        if footer_text:
            footer_status = "Enabled ✅"
            mode_button = InlineKeyboardButton('Disable Footer ❌', callback_data='disable_footer')
        else:
            footer_status = "Disabled ❌"
            mode_button = InlineKeyboardButton('Enable Footer ✅', callback_data='set_footer')

        # Send the settings message with options
        caption = f"📄 **Footer Settings**\n\n**Footer Status:** {footer_status}\n\nUse the options below to configure the footer."

        if footer_text:
            caption += f"\n\n**Current Footer Text:**\n{footer_text}"

        await message.reply_photo(
            photo=FORCE_PIC,
            caption=caption,
            reply_markup=InlineKeyboardMarkup([
                [mode_button],
                [InlineKeyboardButton('Set Footer', callback_data='set_footer')],
                [InlineKeyboardButton('Close ✖️', callback_data='close')]
            ])
        )
    except Exception as e:
        # Log and send error
        logging.error(f"Error in set_footer command: {e}")
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Close ✖️", callback_data="close")]])
        await message.reply(
            (
                f"❌ **Error Occurred:**\n\n"
                f"**Reason:** {e}\n\n"
                f"📩 Contact developer: [Rohit](https://t.me/rohit_1888)"
            ),
            reply_markup=reply_markup
        )



@Bot.on_message(filters.command('caption') & filters.private & is_admin)
async def toggle_caption(client: Client, message: Message):
    await message.reply_chat_action(ChatAction.TYPING)
    
    # Check the current caption state (enabled or disabled)
    current_state = await db.get_caption_state(message.from_user.id)

    # Toggle the state
    new_state = not current_state
    await db.set_caption_state(message.from_user.id, new_state)

    # Create buttons for ✅ and ❌ based on the new state
    caption_button = InlineKeyboardButton(
        text="✅ Captions Enabled" if new_state else "❌ Captions Disabled", 
        callback_data="toggle_caption"
    )

    # Send a message with the toggle button
    await message.reply_text(
        f"Captions are now {'enabled' if new_state else 'disabled'}.",
        reply_markup=InlineKeyboardMarkup([
            [caption_button]
        ])
    )

