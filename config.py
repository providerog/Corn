
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "8171217557:AAHblES_Ve2lCOZGtq4Jxw2kL_6Fv_JnuZQ")

#Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", "21816206"))

#Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "0a82243f31819a62df76947196fdaa0a")

#Your db channel Id
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002213113260"))

#OWNER ID
OWNER_ID = int(os.environ.get("OWNER_ID", "7645440087"))

#Port
PORT = os.environ.get("PORT", "6548")

DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://sunitverma080:mg0Pd4Pdf0UD0Ou8@merabot1.dcduprk.mongodb.net/?retryWrites=true&w=majority&appName=merabot1")
DB_NAME = os.environ.get("DATABASE_NAME", "corning")




IS_VERIFY = os.environ.get("IS_VERIFY", "True")
TUT_VID = os.environ.get("TUT_VID", "https://t.me/team_g_shit")



TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "100"))

START_PIC = os.environ.get("START_PIC", "https://iili.io/38QhYsS.md.jpg")
FORCE_PIC = os.environ.get("FORCE_PIC", "https://iili.io/38QjNj4.md.jpg")

QR_PIC = os.environ.get("QR_PIC", "https://t.me/filtered_team/6")




#set your Custom Caption here, Keep None for Disable Custom Caption
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "<b>@DD_FREE_DISHH</b>")

#Collection of pics for Bot // #Optional but atleast one pic link should be replaced if you don't want predefined links
PICS = (os.environ.get("PICS", "https://envs.sh/4Iq.jpg https://envs.sh/4IW.jpg https://envs.sh/4IB.jpg https://envs.sh/4In.jpg")).split() #Required



#==========================(BUY PREMIUM)====================#

PREMIUM_BUTTON = reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Remove Ads In One Click", callback_data="buy_prem")]]
)

PREMIUM_BUTTON2 = reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Remove Ads In One Click", callback_data="buy_prem")]]
) 

OWNER_TAG = os.environ.get("OWNER_TAG", "Provider_og")

#UPI ID
UPI_ID = os.environ.get("UPI_ID", "PROVIDERJI@AXL")

#UPI QR CODE IMAGE
UPI_IMAGE_URL = os.environ.get("UPI_IMAGE_URL", "https://iili.io/38QN0gt.md.jpg")

#SCREENSHOT URL of ADMIN for verification of payments
SCREENSHOT_URL = os.environ.get("SCREENSHOT_URL", f"t.me/Provider_og")



#Time and its price

#7 Days
PRICE1 = os.environ.get("PRICE1", "40 rs")

#1 Month
PRICE2 = os.environ.get("PRICE2", "80 rs")

#3 Month
PRICE3 = os.environ.get("PRICE3", "240 rs")

#6 Month
PRICE4 = os.environ.get("PRICE4", "480 rs")

#1 Year
PRICE5 = os.environ.get("PRICE5", "960 rs")


#===================(END)========================#


#Set true if you want Disable your Channel Posts Share button
DISABLE_CHANNEL_BUTTON = os.environ.get("True", True) == 'True'

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "âŒDon't send me messages directly I'm only File Sharing Bot!"




LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
