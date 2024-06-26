from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, UserProfilePhotos
from telegram.ext import CommandHandler, CallbackQueryHandler, filters, MessageHandler, Updater
from shivu import collection, user_collection, event_collection, application
import os
import random


def generate_progress_bar(percent):
    filled_blocks = int(percent / 5)
    empty_blocks = 20 - filled_blocks
    return "■" * filled_blocks + "□" * empty_blocks



async def get_user_favorite_character_img_url(user_id: int) -> int:
    user = await user_collection.find_one({'id': user_id})
    if user and 'favorites' in user:
        favorite_id = user['favorites'][0]  # Assuming only one favorite character for simplicity
        favorite_character = next((c for c in user['characters'] if c['id'] == favorite_id), None)
        if favorite_character:
            return favorite_character['img_url']
    
    
    all_characters = user.get('characters', [])
    if all_characters:
        random_character = random.choice(all_characters)
        return random_character['img_url']
    
    return None
    



async def get_global_rank(username: str) -> int:
    pipeline = [
        {"$project": {"username": 1, "first_name": 1, "character_count": {"$size": "$characters"}}},
        {"$sort": {"character_count": -1}}
    ]

    cursor = user_collection.aggregate(pipeline)
    leaderboard_data = await cursor.to_list(length=None)

    for i, user in enumerate(leaderboard_data, start=1):
        if user.get('username') == username:
            return i

    return 0


async def get_user_async(user):
    pass

async def get_user_info(user, already=False, update=None):
    if not already:
        # Assuming you have an async method to get users from the ID in the shivu library
        user = await get_user_async(user)
    if not update.effective_user.first_name:
        return ["Deleted account", None]
    user_id = update.effective_user.id
    
    
    username = update.effective_user.username
    first_name = update.effective_user.first_name
    userr = await user_collection.find_one({'id': user_id})
    if not userr:
        caught_characters = "Haven't caught any character"
        info_text = "Start Me And Catch Some Character's First"
    else:
        harem_user = await user_collection.find_one({'id': user_id})
        unique_characters = set()
        total_count = sum(1 for char in harem_user['characters'] if char.get('rarity') != '⛄️ Winters[S]' and (char_id := char.get('id')) not in unique_characters and not unique_characters.add(char_id))
        global_count = await collection.count_documents({})
        total_percentage = min((total_count / global_count) * 100, 100)
        Rounded_total_percentage = round(total_percentage, 2)
        progress_bar = generate_progress_bar(Rounded_total_percentage)
        caught_characters = [f"{total_count}/{global_count}[{Rounded_total_percentage}%]"]
        global_rank = await get_global_rank(username)
        total_users = await user_collection.count_documents({})
        global_rank_ratio = f"{global_rank}/{total_users}"
        
        info_text = (
            f"<b>📊 𝗨𝘀𝗲𝗿'𝘀 𝗣𝗿𝗼𝗳𝗶𝗹𝗲</b> ▰▱▰▱▰▱▰▱▰▱▰▱▰\n\n"
            f"<b>🆔 ɪᴅ:</b> {user_id}\n"
            f"<b>📑 ɴᴀᴍᴇ:</b> {first_name}\n"
            f"<b>🔖 ᴜꜱᴇʀɴᴀᴍᴇ:</b> @{username}\n"
            f"<b>⛩️ ᴄʜᴀʀᴀᴄᴛᴇʀꜱ ᴄᴀᴜɢʜᴛ:</b> {caught_characters[0]}\n"
            f"<b>📈 ᴘʀᴏɢʀᴇꜱꜱ ʙᴀʀ:</b> {progress_bar}\n"
            f"<b>🌐 ɢʟᴏʙᴀʟ ʀᴀɴᴋ:</b> {global_rank_ratio}\n"     
        )
     
    return info_text

async def profile(update, context):
    bot = context.bot
    
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user.id
        user_id = update.message.reply_to_message.from_user.id
    elif len(context.args) == 1:
        user = context.args[0]
        user_id = context.args[0]
    else:
        user = update.message.from_user.id
        user_id = update.effective_user.id
        
    m = await update.message.reply_text("Collecting User Data...")  # Use 'await' here
    
    try:
        info_text = await get_user_info(user, update=update)  # Use 'await' here
        fav_character_img_url = await get_user_favorite_character_img_url(user_id)
    except Exception as e:
        print(f"Something Went Wrong {e}")
        return await m.edit_text("Sorry something Went Wrong Report At @Catch_Your_WH_Group")  # Use 'await' here

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("sᴇᴇ ᴄᴏʟʟᴇᴄᴛɪᴏɴ", switch_inline_query_current_chat=f"collection.{user}")],
        [InlineKeyboardButton("🚮", callback_data="delete_message")]
    ])

    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Start Me", url=f"https://t.me/{context.bot.username}?start=True")]
        ]
    )

    if info_text == "Start Me And Catch Some Character's First":
        return await m.edit_text(info_text, reply_markup=reply_markup)  # Use 'await' here
        
    if fav_character_img_url:
        await update.message.reply_photo(photo=fav_character_img_url, caption=info_text, parse_mode='HTML', reply_markup=keyboard)  # Use 'await' here
    else:
        await update.message.reply_text(info_text, parse_mode='HTML', reply_markup=keyboard, disable_web_page_preview=True)



async def callback_handler(update, context):
    if update.callback_query.data == "delete_message":
        await update.callback_query.message.delete()

application.add_handler(CommandHandler('profile', profile, block=False))
application.add_handler(CallbackQueryHandler(callback_handler, pattern='^delete_message', block=False))
