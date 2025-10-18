import asyncio
from bot import Bot
import pyrogram.utils

async def main():
    pyrogram.utils.MIN_CHANNEL_ID = -1009147483647
    await Bot().start()
    await asyncio.Event().wait()  # Keep the event loop running

if __name__ == "__main__":
    asyncio.run(main())
