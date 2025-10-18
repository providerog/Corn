#Javpostr | @rohit_1888 on Tg
import asyncio
from aiohttp import web
#from plugins import web_server

import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime, timedelta
import pytz  # For Indian Standard Time (IST)

from config import *
from dotenv import load_dotenv
from database.db_premium import remove_expired_users
from database.database import db

from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv(".env")

def get_indian_time():
    """Returns the current time in IST."""
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist)


from aiohttp import web
#from .route import routes


async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("CodeXBotz")

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=API_ID,
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def scrape_worker(self):
        """Processes scrape tasks from the queue."""
        while True:
            task = await self.scrape_queue.get()
            if task is None:  # Sentinel value to stop the worker
                break
            try:
                from plugins.scrapper import process_scrape_task
                await process_scrape_task(self, task)
            except Exception as e:
                self.LOGGER(__name__).error(f"Error processing scrape task: {e}")
            finally:
                self.scrape_queue.task_done()

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = get_indian_time()  # Use IST for uptime tracking
        self.scrape_queue = asyncio.Queue()
        self.scrape_worker_task = asyncio.create_task(self.scrape_worker())

        # Create a single scraper client
        user_session = await db.get_session(OWNER_ID)
        if user_session:
            self.scraper_client = Client("scraper_session", session_string=user_session, api_id=API_ID, api_hash=API_HASH)
            await self.scraper_client.start()
        else:
            self.scraper_client = None
            self.LOGGER(__name__).warning("Owner is not logged in. Scraping will not work.")


        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(
                f"Make Sure bot is Admin in DB Channel, and Double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}"
            )
            self.LOGGER(__name__).info("\nBot Stopped. @rohit_1888 for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.username = usr_bot_me.username
        self.LOGGER(__name__).info(f"Bot Running..! Made by @provider_og")

        # Start Web Server
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()


        try: await self.send_message(OWNER_ID, text = f"<b><blockquote>🤖 Bᴏᴛ Rᴇsᴛᴀʀᴛᴇᴅ by @rohit_1888</blockquote></b>")
        except: pass

    async def stop(self, *args):
        # Gracefully stop the worker
        self.scrape_queue.put_nowait(None)
        await self.scrape_worker_task
        if self.scraper_client:
            await self.scraper_client.stop()
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")
