import asyncio
from datetime import datetime, timedelta
from pyrogram import filters, Client, types as t
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from shivu import shivuu as bot
from shivu import user_collection, collection

DEVS = (1643054031) # Devloper user IDs

async def get_unique_characters(receiver_id, target_rarities=['🟢 Common', '🟣 Rare', '🟡 Legendary']):
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

# Dictionary to store last claim time for each user
last_claim_time = {}

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

async def is_user_subscribed(user_id):
    try:
        user = await bot.get_chat_member("@CATCH_YOUR_WH_UPDATES", user_id)
        if user.status in ["member", "administrator", "creator"]:
            return True
    except:
        return False
    return False

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
    if chat_id != -1002134049876:  # Change this to your group's chat ID
        return await message.reply_text("Command can only be used here: @Catch_Your_WH_Group")
    
    mention = message.from_user.mention
    user_id = message.from_user.id

    # Check if the user is banned
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
            return await message.reply_text(f"", quote=True)

    # Check if the user is subscribed
    if not await is_user_subscribed(user_id):
        keyboard = [
            [
                InlineKeyboardButton("Join Channel", url="https://t.me/CATCH_YOUR_WH_UPDATES"),
                InlineKeyboardButton("Join Group", url="https://t.me/Catch_Your_WH_Group")
            ],
            [InlineKeyboardButton("Try Again", callback_data="try_again")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text("To claim characters, please join our channel and group:", reply_markup=reply_markup)
        return

    # Update the last claim time for the user
    last_claim_time[user_id] = now
    await add_claim_user(user_id)

    receiver_id = message.from_user.id
    unique_characters = await get_unique_characters(receiver_id)
    try:
        await user_collection.update_one({'id': receiver_id}, {'$push': {'characters': {'$each': unique_characters}}})
        img_urls = [character['img_url'] for character in unique_characters]
        captions = [
            f"𝑪𝒐𝒏𝒈𝒓𝒂𝒕𝒖𝒍𝒂𝒕𝒊𝒐𝒏𝒔 🎊 {mention}!Your today's reward is:\n"
            f"🎀 𝑵𝑨𝑴𝑬: {character['name']}\n"
            f"💓 𝑨𝑵𝑰𝑴𝑬: {character['anime']}\n"
            
            f"𝑪𝒐𝒎𝒆 𝒂𝒈𝒂𝒊𝒏 𝑻𝒐𝒎𝒐𝒓𝒓𝒐𝒘 𝒇𝒐𝒓 𝒚𝒐𝒖𝒓 𝒏𝒆𝒙𝒕 𝒄𝒍𝒂𝒊𝒎 🍀\n"
            for character in unique_characters
        ]
        for img_url, caption in zip(img_urls, captions):
            await message.reply_photo(photo=img_url, caption=caption)
    except Exception as e:
        print(e)

@bot.on_message(filters.command(["find"]))
async def find(_, message: t.Message):
    if len(message.command) < 2:
        return await message.reply_text("𝑷𝒍𝒆𝒂𝒔𝒆 𝒑𝒓𝒐𝒗𝒊𝒅𝒆 𝒕𝒉𝒆 𝒘𝒂𝒊𝒇𝒖 𝑰𝑫 ☘️", quote=True)

    waifu_id = message.command[1]
    waifu = await collection.find_one({'id': waifu_id})

    if not waifu:
        return await message.reply_text(" 𝑵𝒐 𝒘𝒂𝒊𝒇𝒖 𝒇𝒐𝒖𝒏𝒅 𝒘𝒊𝒕𝒉 𝒕𝒉𝒂𝒕 𝑰𝑫 ❌", quote=True)

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
        user_id = user_info['_id']
        try:
            user = await bot.get_users(user_id)
            usernames.append(user.username if user.username else f"➥ {user_id}")
        except Exception as e:
            print(e)
            usernames.append(f"➥ {user_id}")

    # Construct the caption
    caption = (
        f"🧩 𝑾𝒂𝒊𝒇𝒖 𝑰𝑫: {waifu_id}\n"
        f"🎀 𝑵𝒂𝒎𝒆: {waifu['name']}\n"
        f"⚕️ 𝑹𝒂𝒓𝒊𝒕𝒚: {waifu['rarity']}\n"
        f"⚜️ 𝑨𝒏𝒊𝒎𝒆: {waifu['anime']}\n"
        f"🪅 𝑰𝑫: {waifu['id']}\n\n"
        f"✳️ 𝑯𝒆𝒓𝒆 𝒊𝒔 𝒕𝒉𝒆 𝒍𝒊𝒔𝒕 𝒐𝒇 𝒖𝒔𝒆𝒓𝒔 𝒘𝒉𝒐 𝒉𝒂𝒗𝒆 𝒕𝒉𝒊𝒔 𝒄𝒉𝒂𝒓𝒂𝒄𝒕𝒆𝒓 〽️:\n\n"
    )
    for i, user_info in enumerate(top_users):
        count = user_info['count']
        username = usernames[i]
        caption += f"{i + 1}. {username} x{count}\n"

    # Reply with the waifu information and top users
    await message.reply_photo(photo=waifu['img_url'], caption=caption)

@bot.on_message(filters.command(["cfind"]))
async def cfind(_, message: t.Message):
    if len(message.command) < 2:
        return await message.reply_text("𝑷𝒍𝒆𝒂𝒔𝒆 𝒑𝒓𝒐𝒗𝒊𝒅𝒆 𝒕𝒉𝒆 𝒂𝒏𝒊𝒎𝒆 𝒏𝒂𝒎𝒆✨", quote=True)

    anime_name = " ".join(message.command[1:])
    characters = await collection.find({'anime': anime_name}).to_list(length=None)

    if not characters:
        return await message.reply_text(f"𝑵𝒐 𝒄𝒉𝒂𝒓𝒂𝒄𝒕𝒆𝒓𝒔 𝒇𝒐𝒖𝒏𝒅 𝒇𝒓𝒐𝒎 𝒕𝒉𝒆 𝒂𝒏𝒊𝒎𝒆 ❎ {anime_name}.", quote=True)

    captions = [
        f"🎏 𝑵𝒂𝒎𝒆: {char['name']}\n🪅 𝑰𝑫: {char['id']}\n🧩 𝑹𝒂𝒓𝒊𝒕𝒚: {char['rarity']}\n"
        for char in characters
    ]
    response = "\n".join(captions)
    await message.reply_text(f"🍁 𝑪𝒉𝒂𝒓𝒂𝒄𝒕𝒆𝒓𝒔 𝒇𝒓𝒐𝒎 {anime_name}:\n\n{response}", quote=True)

# Handling the try again button press to delete the join message
@bot.on_callback_query(filters.regex("try_again"))
async def try_again_callback(_, callback_query: t.CallbackQuery):
    await callback_query.message.delete()

