import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from shivu import collection, user_collection
from shivu import shivuu as app

async def find_character(character_id):
    character = await collection.find_one({'id': character_id})

    if character:
        details = (
            f"ℹ️ Information for character with ID {character_id}:\n"
            f" ✅ Rarity: {character.get('rarity', 'Unknown')}\n"
            f"🫂 Anime: {character.get('anime', 'Unknown')}\n"
            f"💕 Name: {character.get('name', 'Unknown')}\n"
            f"🍿 ID: {character_id}"
        )

        photo_url = character.get('img_url', None)
        return details, photo_url
    else:
        return f"Character with ID '{character_id}' not found.", None

async def get_member_user_ids(chat_id):
    member_user_ids = []
    async for member in app.get_chat_members(chat_id):
        member_user_ids.append(member.user.id)
    return member_user_ids

@app.on_message(filters.command(["find_bela"]))
async def find_trade_command(client, message):
    try:
        character_id = message.text.split(maxsplit=1)[1]

        details, photo_url = await find_character(character_id)

        if photo_url:
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Who Collected?", callback_data=f"who_collected_{character_id}")]])
            await message.reply_photo(photo=photo_url, caption=details, reply_markup=keyboard)
        else:
            await message.reply_text(details)
    except IndexError:
        await message.reply_text("Please provide a character ID to search for.")
    except Exception as e:
        print(f"Error in find_trade_command: {e}")
        await message.reply_text("An error occurred while processing the command.")

@app.on_callback_query(filters.regex(r'^who_collected_'))
async def who_collected_callback(_, callback_query):
    try:
        character_id = callback_query.data.split('_')[1]

        chat_id = callback_query.message.chat.id
        user_ids = await get_member_user_ids(chat_id)

        user_collected = {}
        for user_id in user_ids:
            sender = await user_collection.find_one({'id': user_id})
            if sender and 'characters' in sender:
                quantity = sum(1 for char in sender['characters'] if char.get('id') == character_id)
                if quantity > 0:
                    user_collected[user_id] = quantity

        if user_collected:
            text = "\n".join(f"- User {user_id}: {quantity} characters" for user_id, quantity in user_collected.items())
            await callback_query.message.edit_text(f"Users who collected character {character_id}:\n{text}")
        else:
            await callback_query.message.edit_text("No one has collected this character in this group.")
    except Exception as e:
        print(f"Error in who_collected_callback: {e}")
        await callback_query.message.reply_text(f"An error occurred while processing the request {e}")
