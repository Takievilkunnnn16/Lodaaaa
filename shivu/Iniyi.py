import os
import telegram.ext as tg
from pyrogram import Client
import logging  
from telegram.ext import Application
from motor.motor_asyncio import AsyncIOMotorClient
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger("pyrate_limiter").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

OWNER_ID = Config.OWNER_ID
sudo_users = Config.SUDO_USERS
GROUP_ID = Config.GROUP_ID
TOKEN = Config.TOKEN
mongo_url = Config.MONGO_URL
PHOTO_URL = Config.PHOTO_URL
SUPPORT_CHAT = Config.SUPPORT_CHAT
CHARA_CHANNEL_ID = Config.CHARA_CHANNEL_ID
API_HASH = Config.API_HASH
API_ID = Config.API_ID
UPDATE_CHAT = Config.UPDATE_CHAT
BOT_USERNAME = Config.BOT_USERNAME


application = Application.builder().token(TOKEN).build()
shivuu = Client(
    "lmao",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    
    
)
client = AsyncIOMotorClient(mongo_url)
db = client['Character_catche']
collection = db['anime_characters_lol']
event_collection = db['Event_Characters']
user_totals_collection = db['user_totals_lmaoooo']
user_collection = db["user_collection_lmaoooo"]
group_user_totals_collection = db['group_user_totalsssssss']
top_global_groups_collection = db['top_global_groups']
settings_collection = db["settings"]
