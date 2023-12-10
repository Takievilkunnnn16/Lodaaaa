import logging  
from pyrogram import Client 

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
LOGGER = logging.getLogger(name)

OWNER_ID = 1643054031
sudo_users = ["6384296585", "1643054031"]
GROUP_ID = -1002134049876
TOKEN = "6883098627:AAG9_BgUgaaRhXO0oUmYabqj_pJNcsxoGpQ"
mongo_url = "mongodb+srv://Takievil:takievil098@takievil.uallkel.mongodb.net/?retryWrites=true&w=majority"
PHOTO_URL = ["https://telegra.ph/file/6ed59e57f91d40ef48444.jpg", "https://telegra.ph/file/a216bfefa4b2c1bd9b600.jpg"]
SUPPORT_CHAT = "Catch_Your_waifu"
UPDATE_CHAT = "CATCH_YOUR_WAIFU_UPDATES"
BOT_USERNAME = "Catch_Your_Waifu_Bot"
CHARA_CHANNEL_ID = -1002124773371
api_id = 29593257
api_hash = "e9a3897c961f8dce2a0a88ab8d3dd843"


application = Application.builder().token(TOKEN).build()
shivuu = Client("Shivu", api_id, api_hash, bot_token=TOKEN)
client = AsyncIOMotorClient(mongo_url)
db = client['Character_catcher']
collection = db['anime_characters']
user_totals_collection = db['user_totals']
user_collection = db["user_collection"]
group_user_totals_collection = db['group_user_total']
top_global_groups_collection = db['top_global_groups']
pm_users = db['total_pm_users']
