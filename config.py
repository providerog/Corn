
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

def get_env_var(name, is_int=False):
    """Gets an environment variable or raises an error."""
    value = os.environ.get(name)
    if value is None:
        raise ValueError(f"Environment variable {name} not set!")
    if is_int:
        return int(value)
    return value

TG_BOT_TOKEN = get_env_var("TG_BOT_TOKEN")

#Your API ID from my.telegram.org
API_ID = get_env_var("API_ID", is_int=True)

#Your API Hash from my.telegram.org
API_HASH = get_env_var("API_HASH")

#Your db channel Id
CHANNEL_ID = get_env_var("CHANNEL_ID", is_int=True)

#OWNER ID
OWNER_ID = get_env_var("OWNER_ID", is_int=True)

#Port
PORT = get_env_var("PORT")

DB_URI = get_env_var("DATABASE_URL")
DB_NAME = get_env_var("DATABASE_NAME")




IS_VERIFY = get_env_var("IS_VERIFY")
TUT_VID = get_env_var("TUT_VID")



TG_BOT_WORKERS = get_env_var("TG_BOT_WORKERS", is_int=True)

START_PIC = get_env_var("START_PIC")
FORCE_PIC = get_env_var("FORCE_PIC")

QR_PIC = get_env_var("QR_PIC")




#set your Custom Caption here, Keep None for Disable Custom Caption
CUSTOM_CAPTION = get_env_var("CUSTOM_CAPTION")

#Collection of pics for Bot // #Optional but atleast one pic link should be replaced if you don't want predefined links
PICS = (get_env_var("PICS")).split() #Required



#==========================(BUY PREMIUM)====================#

PREMIUM_BUTTON = reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Remove Ads In One Click", callback_data="buy_prem")]]
)

PREMIUM_BUTTON2 = reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Remove Ads In One Click", callback_data="buy_prem")]]
)

OWNER_TAG = get_env_var("OWNER_TAG")

#UPI ID
UPI_ID = get_env_var("UPI_ID")

#UPI QR CODE IMAGE
UPI_IMAGE_URL = get_env_var("UPI_IMAGE_URL")

#SCREENSHOT URL of ADMIN for verification of payments
SCREENSHOT_URL = get_env_var("SCREENSHOT_URL")



#Time and its price

#7 Days
PRICE1 = get_env_var("PRICE1")

#1 Month
PRICE2 = get_env_var("PRICE2")

#3 Month
PRICE3 = get_env_var("PRICE3")

#6 Month
PRICE4 = get_env_var("PRICE4")

#1 Year
PRICE5 = get_env_var("PRICE5")


#===================(END)========================#


#Set true if you want Disable your Channel Posts Share button
DISABLE_CHANNEL_BUTTON = os.environ.get("True", True) == 'True'

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "â ŒDon't send me messages directly I'm only File Sharing Bot!"




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
