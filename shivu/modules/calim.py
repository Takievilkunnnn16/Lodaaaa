import asyncio
from datetime import datetime
from pyrogram import filters, Client, types as t
from pyrogram import InlineKeyboardButton, InlineKeyboardMarkup
from shivu import shivuu as bot
from shivu import user_collection, collection

DEVS = [1643054031]  

async def get_unique_characters(receiver_id, target_rarities=['🟢 Medium','🟣 Rare','⚪️ Common','🟡 Legendary','💮 Exclusive','🫧 Special','🔮 Mythical']):
    try:
        pipeline = [
            {'$match': {'rarity': {'$in': target_rarities}, 'id': {'$nin': [char['id'] for char in (await user_collection.find_one({'id': receiver_id}, {'characters': 1}))['characters']]}}},
            {'$sample': {'size': 1}}  
        ]

        cursor = collection.aggregate(pipeline)
        characters = await cursor.to_list(length=None)
        return characters
    except Exception as e:
        return []

async def claim_toggle(claim_state):
    try:
        await collection.update_one({}, {"$set": {"claim": claim_state}}, upsert=True)
    except Exception as e:
        print(e)

async def get_claim_state():
    try:
        doc = await collection.find_one({})
        return doc.get("claim", "False")
    except Exception as e:
        print(e)
        return "False"

async def add_claim_user(user_id):
    try:
        await user_collection.update_one({"id": user_id}, {"$set": {"claim": True}}, upsert=True)
    except Exception as e:
        print(e)

async def del_all_claim_user():
    try:
        await user_collection.update_many({}, {"$unset": {"claim": ""}})
    except Exception as e:
        print(e)

async def get_claim_of_user(user_id):
    try:
        doc = await user_collection.find_one({"id": user_id})
        return doc.get("claim", False)
    except Exception as e:
        print(e)
        return False

@bot.on_message(filters.command(["startclaim"]) & filters.user(DEVS))
async def start_claim(_: bot, message: t.Message):
    await claim_toggle("True")
    await message.reply_text("Claiming feature enabled!")

@bot.on_message(filters.command(["stopclaim"]) & filters.user(DEVS))
async def stop_claim(_: bot, message: t.Message):
    await claim_toggle("False")
    await message.reply_text("Claiming feature disabled!")
    
@bot.on_message(filters.command(["claim"]))
async def claim(_: bot, message: t.Message):
    chat_id = message.chat.id
    if chat_id != -1002134049876:  # Change this to your group's chat ID
        return await message.reply_text("Command can only be used here: @Catch_Your_WH_Group")
        

@bot.on_message(filters.command(["claim"]))
async def claim(_: bot, message: t.Message):
    # Check if the claiming feature is enabled
    claim_state = await get_claim_state()
    if claim_state == "False":
        return await message.reply_text("Claiming feature is currently disabled.")

    user_id = message.from_user.id
    
    # Check if the user has already claimed today
    claimed_date = await get_claim_of_user(user_id)
    if claimed_date:
        return await message.reply_text("You've already claimed today! Come back tomorrow.")
        receiver_id = message.from_user.id

    # Send subscription options
    keyboard = [
        [
            InlineKeyboardButton("Join Channel", url="https://t.me/CATCH_YOUR_WH_UPDATES"),
            InlineKeyboardButton("Join Group", url="https://t.me/Catch_Your_WH_Group")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send subscription options as a reply
    await message.reply_text("To claim characters, please Join to our channel and group:", 'reply_markup=reply_mark up')

    
    
    # Fetch unique characters for the user
    unique_characters = await get_unique_characters(receiver_id)
    
    try:
        await add_claim_user(user_id)
        img_urls = [character['img_url'] for character in unique_characters]
        captions = [
            f"Congratulations! You Got a new character!\n"
            f"Name: {character['name']}\n"
            f"Rarity: {character['rarity']}\n"
            f"Anime: {character['anime']}\n"
            for character in unique_characters
        ]
        
        # Send characters as output
        for img_url, caption in zip(img_urls, captions):
            await message.reply_photo(photo=img_url, caption=caption)
    except Exception as e:
        print(e)

@bot.on_message(filters.command(["resetclaims"]) & filters.user(DEVS))
async def reset_claims(_: bot, message: t.Message):
    await del_all_claim_user()
    await message.reply_text("All claim records have been reset!")
