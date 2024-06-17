from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import re
from pyrogram import Client, filters, types, enums
import asyncio
import time
from html import escape
from cachetools import TTLCache
from pymongo import MongoClient, ASCENDING
from shivu import shivuu as app
from shivu import user_collection, collection, db

# MongoDB indexes
db.characters.create_index([('id', ASCENDING)])
db.characters.create_index([('anime', ASCENDING)])
db.characters.create_index([('img_url', ASCENDING)])

db.user_collection.create_index([('characters.id', ASCENDING)])
db.user_collection.create_index([('characters.name', ASCENDING)])
db.user_collection.create_index([('characters.img_url', ASCENDING)])

all_characters_cache = TTLCache(maxsize=10000, ttl=36000)
user_collection_cache = TTLCache(maxsize=10000, ttl=60)

@app.on_inline_query()
async def inlinequery(client: Client, query: types.InlineQuery):
    offset = int(query.offset) if query.offset else 0

    if query.query.startswith('collection.'):
        user_id, *search_terms = query.query.split(' ')[0].split('.')[1], ' '.join(query.query.split(' ')[1:])
        if user_id.isdigit():
            if user_id in user_collection_cache:
                user = user_collection_cache[user_id]
            else:
                user = await user_collection.find_one({'id': int(user_id)})
                user_collection_cache[user_id] = user

            if user:
                all_characters = list({v['id']:v for v in user['characters']}.values())
                if search_terms:
                    regex = re.compile(' '.join(search_terms), re.IGNORECASE)
                    all_characters = [character for character in all_characters if regex.search(character['name']) or regex.search(character['rarity']) or regex.search(character['id']) or regex.search(character['anime'])]
            else:
                all_characters = []
        else:
            all_characters = []
    else:
        if query.query:
            regex = re.compile(query.query, re.IGNORECASE)
            all_characters = list(await collection.find({"$or": [{"name": regex}, {"rarity": regex}, {"id": regex}, {"anime": regex}]}).to_list(length=None))
        else:
            if 'all_characters' in all_characters_cache:
                all_characters = all_characters_cache['all_characters']
            else:
                all_characters = list(await collection.find({}).to_list(length=None))
                all_characters_cache['all_characters'] = all_characters

    characters = all_characters[offset:offset+50]
    if len(characters) > 50:
        characters = characters[:50]
        next_offset = str(offset + 50)
    else:
        next_offset = str(offset + len(characters))

    results = []
    for character in characters:
        global_count = await user_collection.count_documents({'characters.id': character['id']})
        anime_characters = await collection.count_documents({'anime': character['anime']})
        total_characters = len(all_characters)
        title = str(total_characters)
        if query.query.startswith('collection.'):
            user_character_count = sum(c['id'] == character['id'] for c in user['characters'])
            user_anime_characters = sum(c['anime'] == character['anime'] for c in user['characters'])
            caption = f"<b>Lᴏᴏᴋ Aᴛ <a href='tg://user?id={user['id']}'>{(escape(user.get('first_name', user['id'])))}</a>'s Wᴀɪғᴜ....!!</b>\n\n <b>{character['id']}:</b> {character['name']} x{user_character_count}\n<b>{character['anime']}</b> {user_anime_characters}/{anime_characters}\n﹙<b>{character['rarity'][0]} 𝙍𝘼𝙍𝙄𝙏𝙔:</b> {character['rarity'][2:]}﹚\n"
        else:
            caption = f"<b>Lᴏᴏᴋ Aᴛ Tʜɪs Wᴀɪғᴜ....!!</b>\n\n<b>{character['id']}:</b> {character['name']}\n <b>{character['anime']}</b>\n﹙<b>{character['rarity'][0]} 𝙍𝘼𝙍𝙄𝙏𝙔:</b> {character['rarity'][2:]}﹚\n\n<b>Gʟᴏʙᴀʟʟʏ Gʀᴀʙ {global_count} Times...</b>\n\n✳️ 𝖧𝖾𝗋𝖾 𝗂𝗌 𝗍𝗁𝖾 𝗅𝗂𝗌𝗍 𝗈𝖿 𝗎𝗌𝖾𝗋𝗌 𝗐𝗁𝗈 𝗁𝖺𝗏𝖾 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗋𝖺𝖼𝗍𝖾𝗋\n"
        results.append(
            types.InlineQueryResultPhoto(
                title=title,
                thumb_url=character['img_url'],
                photo_url=character['img_url'],
                caption=caption,
                parse_mode=enums.ParseMode.HTML
            )
        )

    await client.answer_inline_query(query.id, results, next_offset=next_offset, cache_time=5, is_gallery=True)
