from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from html import escape 
from shivu import user_collection, shivuu, collection
import random  

DEV_USERS = [6845325416,1643054031]

@shivuu.on_message(filters.command("give"))
async def give(client,message):
   if message.from_user.id not in DEV_USERS:
        return await message.reply_text("Dev's restricted command") 
   else:
        receiver_id = message.reply_to_message.from_user.id
        all_characters = list(await collection.find({}).to_list(length=None))
        random_characters = random.sample(all_characters, 5)
        for character in random_characters:
      
      await user_collection.update_one({'id': receiver_id},{'$push': {'characters': character}})
      await message.reply_text("Done")
