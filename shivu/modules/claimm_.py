import asyncio
from pyrogram import filters, Client, types as t
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from shivu import shivuu as bot
from shivu import user_collection, collection
from datetime import datetime, timedelta
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant


DEVS =  (1643054031) # Devloper user IDs
SUPPORT_CHAT_ID = -1002134049876  # Change this to your group's chat ID

keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Join Chat To Use Me", url="https://t.me/Catch_Your_WH_Group")],
    [InlineKeyboardButton("Join Chat To Use Me", url="https://t.me/CATCH_YOUR_WH_UPDATES")]
])

async def force_sub(chat_id, user_id):
        try:
            member = await bot.get_chat_member(-1002134049876, user_id)
            members = await bot.get_chat_member(-1001746346532, user_id)
            if member and members:
                pass
        except UserNotParticipant:
            await message.reply_text("**You need to join the chat to use this feature.**", reply_markup=keyboard)
            return 

# Functions from the second code
async def claim_toggle(claim_state):
    try:
        await collection.update_one({}, {"$set": {"claim": claim_state}}, upsert=True)
    except Exception as e:
        print(f"Error in claim_toggle: {e}")

async def get_claim_state():
    try:
        doc = await collection.find_one({})
        return doc.get("claim", "False")
    except Exception as e:
        print(f"Error in get_claim_state: {e}")
        return "False"

async def add_claim_user(user_id):
    try:
        await user_collection.update_one({"id": user_id}, {"$set": {"claim": True}}, upsert=True)
    except Exception as e:
        print(f"Error in add_claim_user: {e}")

async def del_all_claim_user():
    try:
        await user_collection.update_many({}, {"$unset": {"claim": ""}})
    except Exception as e:
        print(f"Error in del_all_claim_user: {e}")

async def get_claim_of_user(user_id):
    try:
        doc = await user_collection.find_one({"id": user_id})
        return doc.get("claim", False)
    except Exception as e:
        print(f"Error in get_claim_of_user: {e}")
        return False

async def get_unique_characters(receiver_id, target_rarities=['(⚪️ Common', '🟣 Rare', '🟡 Legendary', '🟢 Medium']):
    try:
        pipeline = [
            {'$match': {'rarity': {'$in': target_rarities}, 'id': {'$nin': [char['id'] for char in (await user_collection.find_one({'id': receiver_id}, {'characters': 1}))['characters']]}}},
            {'$sample': {'size': 1}}  # Adjust Num
        ]

        cursor = collection.aggregate(pipeline)
        characters = await cursor.to_list(length=None)
        return characters
    except Exception as e:
        return []

# Dictionary to store last claim time for each user
last_claim_time = {}

@bot.on_message(filters.command(["startclaim"]) & filters.user(DEVS))
async def start_claim(_, message: t.Message):
    await claim_toggle("True")
    await message.reply_text("Claiming feature enabled!")

@bot.on_message(filters.command(["stopclaim"]) & filters.user(DEVS))
async def stop_claim(_, message: t.Message):
    await claim_toggle("False")
    await message.reply_text("Claiming feature disabled!")

@bot.on_message(filters.command(["claim"]))
async def claim(_, message: t.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await force_sub(SUPPORT_CHAT_ID, user_id)
    
    if chat_id != SUPPORT_CHAT_ID:
        return await message.reply_text("Command can only be used here: @Catch_Your_WH_Group")

    mention = message.from_user.mention
    

    # Check if the user is bannedd
    if user_id == 7162166061:
        return await message.reply_text(f"Sorry {mention}, you are banned from using this command.")

    # Check if the claiming feature is enabled
    claim_state = await get_claim_state()
    if claim_state == "False":
        return await message.reply_text("Claiming feature is currently disabled.")

    # Check if the user has already claimed a waifu today
    now = datetime.now()
    if user_id in last_claim_time:
        last_claim_date = last_claim_time[user_id]
        if last_claim_date.date() == now.date():
            next_claim_time = (last_claim_date + timedelta(days=1)).strftime("%H:%M:%S")
            return await message.reply_text(f"You've already claimed your daily reward today.", quote=True)

    # Update the last claim time for the user
    last_claim_time[user_id] = now
    await add_claim_user(user_id)

    receiver_id = message.from_user.id
    unique_characters = await get_unique_characters(receiver_id)
    try:
        await user_collection.update_one({'id': receiver_id}, {'$push': {'characters': {'$each': unique_characters}}})
        img_urls = [character['img_url'] for character in unique_characters]
        captions = [
            f"Congratulations  {mention}!\n"
            
            f"Your Prize is:\n",
            f"✨ Name: {character['name']}\n"
            f"💓 Anime: {character['anime']}\n"
            
            f"Come back tomorrow 🍀\n"
            for character in unique_characters
        ]
        for img_url, caption in zip(img_urls, captions):
            await message.reply_photo(photo=img_url, caption=caption)
    except Exception as e:
        print(e)

@bot.on_message(filters.command(["hfind"]))
async def hfind(_, message: t.Message):
    if len(message.command) < 2:
        return await message.reply_text("Please provide the Husbando ID ☘️", quote=True)

    waifu_id = message.command[1]
    waifu = await collection.find_one({'id': waifu_id})

    if not waifu:
        return await message.reply_text(" No husbando find with that ID ❌", quote=True)

    # Get the top 10 users with the most of this waifu in the current chat
    top_users = await user_collection.aggregate([
        {'$match': {'characters.id': waifu_id}},
        {'$unwind': '$characters'},
        {'$match': {'characters.id': waifu_id}},
        {'$group': {'_id': '$id', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 10}
    ]).to_list(length=10)

    # Get the usernames of the top users
    usernames = []
    for user_info in top_users:
        user_id = user_info['user_id']
        try:
            user = await bot.get_users(user_id)
            usernames.append(f"<a href='tg://user?id={user_id}'>{user.username or user_id}</a>")
        except Exception as e:
            print(e)
            usernames.append(f"<a href='tg://user?id={user_id}'>{user_id}</a>")

    # Construct the caption
    caption = (
        f" Waifu Information:\n"
        
        f" Name: {waifu['name']}\n"
        f" Rarity: {waifu['rarity']}\n"
        f" Anime: {waifu['anime']}\n"
        f" ID: {waifu['id']}\n\n"
        
        f" Here the list of user's who have this character :\n\n"
    )
    for i, user_info in enumerate(top_users):
        count = user_info['count']
        username = usernames[i]
        caption += f"{i + 1}. {username} x{count}\n"

    # Reply with the waifu information and top users
    await message.reply_photo(photo=waifu['img_url'], caption=caption, parse_mode="HTML")

@bot.on_message(filters.command(["cfind"]))
async def cfind(_, message: t.Message):
    if len(message.command) < 2:
        return await message.reply_text("Please provide the anime name ✨", quote=True)

    anime_name = " ".join(message.command[1:])
    characters = await collection.find({'anime': anime_name}).to_list(length=None)

    if not characters:
        return await message.reply_text(f"No character found from anime ❎ {anime_name}.", quote=True)

    captions = [
        f" Name : {char['name']}\n ID: {char['id']}\n Rarity: {char['rarity']}\n"
        for char in characters
    ]
    response = "\n".join(captions)
    await message.reply_text(f"🍁 Character from {anime_name}:\n\n{response}", quote=True)
