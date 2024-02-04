import importlib
import logging 
from telegram import InputMediaPhoto
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultPhoto, InputTextMessageContent, InputMediaPhoto
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from itertools import groupby
from telegram import Update
from motor.motor_asyncio import AsyncIOMotorClient 
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, filters
from telegram.ext import InlineQueryHandler,CallbackQueryHandler, ChosenInlineResultHandler
from pymongo import MongoClient, ReturnDocument
import urllib.request
import random
from datetime import datetime, timedelta
from threading import Lock
import time
import re
import math
import html
from collections import Counter 
from shivu import db, collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection
from shivu import application, shivuu, LOGGER 
from shivu.modules import ALL_MODULES


locks = {}
message_counters = {}
spam_counters = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}
message_counts = {}
archived_characters = {}
ran_away_count = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("shivu.modules." + module_name)


last_user = {}
warned_users = {}
def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

async def ran_away(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    if chat_id in last_characters:
        if chat_id not in ran_away_count:
            ran_away_count[chat_id] = 0

        ran_away_count[chat_id] += 1

        character_data = last_characters[chat_id]
        character_name = character_data['name']

        # Check if 15 messages have been reached before running away
        if ran_away_count[chat_id] > 20:
            character_photo_url = character_data['img_url']
            rarity = character_data['rarity']
            char_id = character_data['id']

            if chat_id in first_correct_guesses:
                # Check if chat_id exists in ran_away_count before deletion
                if chat_id in ran_away_count:
                    del ran_away_count[chat_id]
            else:
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("More Details", callback_data='more_details')]])
                message_text = f"Ohh No!! Character `[{character_name}]` Has Been Ran Away From Your Chat Store His/Her Name For Next Time"
                await context.bot.send_message(chat_id=chat_id, text=message_text, reply_markup=reply_markup, parse_mode='MarkdownV2)

            archived_characters[chat_id] = character_data

            # Check if chat_id exists in ran_away_count before deletion
            if chat_id in ran_away_count:
                del ran_away_count[chat_id]
            del last_characters[chat_id]


async def more_details_callback(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    character_photo_url = archived_characters[chat_id]['img_url']
    character_name = archived_characters[chat_id]['name']
    rarity = archived_characters[chat_id]['rarity']
    char_id = archived_characters[chat_id]['id']
    anime_name = archived_characters[chat_id]['anime']

    
    user_mention = f"[{update.effective_user.first_name}](tg://user?id={update.effective_user.id})"
    
    details_message = f"""
**🎐OᴡO ! ᴄʜᴇᴄᴋ ᴏᴜᴛ ᴛʜɪs ᴄʜᴀʀᴀᴄᴛᴇʀ !**

**🫧 ɴᴀᴍᴇ** : `{character_name}`
🦄 **ᴀɴɪᴍᴇ** : `{anime_name}`
{rarity[0]} **ʀᴀʀɪᴛʏ** : `{rarity[2:]}`

❄️ **ᴄʜᴀʀᴀᴄᴛᴇʀ ɪᴅ:** `{char_id}`

**ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:** {user_mention}
"""


    await context.bot.send_photo(
        chat_id=chat_id,
        photo=character_photo_url,
        caption=details_message,
        parse_mode='MarkdownV2'
    )


async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id

    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:
        
        chat_frequency = await user_totals_collection.find_one({'chat_id': chat_id})
        if chat_frequency:
            message_frequency = chat_frequency.get('message_frequency', 100)
        else:
            message_frequency = 100

        
        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 10:
            
                if user_id in warned_users and time.time() - warned_users[user_id] < 600:
                    return
                else:
                    
                    await update.message.reply_text(f"⚠️ Don't Spam {update.effective_user.first_name}...\nyour messages will be ignored for 10 minutes...")
                    warned_users[user_id] = time.time()
                    return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}

    
        if chat_id in message_counts:
            message_counts[chat_id] += 1
        else:
            message_counts[chat_id] = 1

    
        if message_counts[chat_id] % message_frequency == 0:
            await send_image(update, context)
            
            message_counts[chat_id] = 0
            
async def send_image(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    
    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    all_characters = list(await collection.find({}).to_list(length=None))
    
    
    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    
    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    
    character = random.choice([c for c in all_characters if c['id'] not in sent_characters[chat_id]])

    
    sent_characters[chat_id].append(character['id'])
    last_characters[chat_id] = character

    

    
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=character['img_url'],
        caption=f"""{character['rarity'][0]} Gʀᴇᴀᴛ! ᴀ ɴᴇᴡ ʜᴜꜱʙᴀɴᴅᴏ ʜᴀs ᴊᴜsᴛ ᴀᴘᴘᴇᴀʀᴇᴅ ᴜsᴇ /guess [ɴᴀᴍᴇ]""",
        parse_mode='Markdown')
    
async def guess(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id not in last_characters:
        return

    if chat_id in first_correct_guesses:
        await update.message.reply_text(f'❌️ Already guessed by Someone..So Try Next Time Bruhh')
        return

    guess = ' '.join(context.args).lower() if context.args else ''
    
    if "()" in guess or "&" in guess.lower():
        await update.message.reply_text("You can't use '&' in your guess.")
        return
        
    
    name_parts = last_characters[chat_id]['name'].lower().split()

    if sorted(name_parts) == sorted(guess.split()) or any(part == guess for part in name_parts):

    
        first_correct_guesses[chat_id] = user_id
        
        user = await user_collection.find_one({'id': user_id})
        if user:
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != user.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != user.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await user_collection.update_one({'id': user_id}, {'$set': update_fields})
            
            await user_collection.update_one({'id': user_id}, {'$push': {'characters': last_characters[chat_id]}})
      
        elif hasattr(update.effective_user, 'username'):
            await user_collection.insert_one({
                'id': user_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'characters': [last_characters[chat_id]],
            })

        
        group_user_total = await group_user_totals_collection.find_one({'user_id': user_id, 'group_id': chat_id})
        if group_user_total:
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != group_user_total.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != group_user_total.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await group_user_totals_collection.update_one({'user_id': user_id, 'group_id': chat_id}, {'$set': update_fields})
            
            await group_user_totals_collection.update_one({'user_id': user_id, 'group_id': chat_id}, {'$inc': {'count': 1}})
      
        else:
            await group_user_totals_collection.insert_one({
                'user_id': user_id,
                'group_id': chat_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'count': 1,
            })


    
        group_info = await top_global_groups_collection.find_one({'group_id': chat_id})
        if group_info:
            update_fields = {}
            if update.effective_chat.title != group_info.get('group_name'):
                update_fields['group_name'] = update.effective_chat.title
            if update_fields:
                await top_global_groups_collection.update_one({'group_id': chat_id}, {'$set': update_fields})
            
            await top_global_groups_collection.update_one({'group_id': chat_id}, {'$inc': {'count': 1}})
      
        else:
            await top_global_groups_collection.insert_one({
                'group_id': chat_id,
                'group_name': update.effective_chat.title,
                'count': 1,
            })


        await update.message.reply_text(f'<b><a href="tg://user?id={user_id}">{update.effective_user.first_name}</a></b> You Got New Character ✅️ \n\nCharacter name: <b>{last_characters[chat_id]["name"]}</b> \nAnime: <b>{last_characters[chat_id]["anime"]}</b> \nRairty: <b>{last_characters[chat_id]["rarity"]}</b>\n\nThis character has been added to your harem now do /hharem to check your new character', parse_mode='HTML')

    else:
        await update.message.reply_text('Incorrect Name.. ❌️')
   
async def fav(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    
    if not context.args:
        await update.message.reply_text('Please provide a character ID.')
        return

    character_id = context.args[0]

    
    user = await user_collection.find_one({'id': user_id})
    if not user:
        await update.message.reply_text('ʏᴏᴜ ʜᴀᴠᴇ ɴᴏᴛ ɢᴜᴇssᴇᴅ ᴀɴʏ ᴄʜᴀʀᴀᴄᴛᴇʀs ʏᴇᴛ..')
        return

    
    character = next((c for c in user['characters'] if c['id'] == character_id), None)
    if not character:
        await update.message.reply_text('This character is not in your collection.')
        return

    
    user['favorites'] = [character_id]

    
    await user_collection.update_one({'id': user_id}, {'$set': {'favorites': user['favorites']}})

    await update.message.reply_text(f'Character {character["name"]} has been added to your favorites.')
    

def main() -> None:
    """Run bot."""
    
    
    application.add_handler(CommandHandler(["guess"], guess, block=False))
    application.add_handler(CommandHandler("hfav", fav, block=False))
    application.add_handler(MessageHandler(filters.ALL, message_counter, block=False))
    application.run_polling(drop_pending_updates=True)
    
if __name__ == "__main__":
    shivuu.start()
    main()
    
