import re
import time
from html import escape
from cachetools import TTLCache
from pymongo import ASCENDING
from telegram import Update, InlineQueryResultPhoto, InlineQueryResultVideo
from telegram.ext import InlineQueryHandler, CallbackContext

from shivu import user_collection, application, db,collection

# MongoDB indexes
db.characters.create_index([('id', ASCENDING)])
db.characters.create_index([('anime', ASCENDING)])
db.characters.create_index([('img_url', ASCENDING)])

db.user_collection.create_index([('characters.id', ASCENDING)])
db.user_collection.create_index([('characters.name', ASCENDING)])
db.user_collection.create_index([('characters.img_url', ASCENDING)])

all_characters_cache = TTLCache(maxsize=10000, ttl=36000)
user_collection_cache = TTLCache(maxsize=10000, ttl=60)

async def get_user(user_id):
    if user_id in user_collection_cache:
        return user_collection_cache[user_id]
    else:
        user = await user_collection.find_one({'id': int(user_id)})
        user_collection_cache[user_id] = user
        return user

async def inlinequery(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    offset = int(update.inline_query.offset) if update.inline_query.offset else 0


    if query.startswith('collection.'):
        user_id, *search_terms = query.split(' ')[0].split('.')[1], ' '.join(query.split(' ')[1:])
        if user_id.isdigit():
            user = await get_user(user_id)
            if user:
                all_characters = list({v['id']: v for v in user.get('characters', [])}.values())
                if search_terms:
                    regex = re.compile(' '.join(search_terms), re.IGNORECASE)
                    all_characters = [character for character in all_characters if
                                        regex.search(character['name']) or regex.search(character['anime'])]
            else:
                all_characters = []
        else:
            all_characters = []
    else:
        if query:
            regex = re.compile(query, re.IGNORECASE)
            all_characters = list(await collection.find({"$or": [{"name": regex}, {"rarity": regex}, {"anime": regex}]}).to_list(length=None))
        else:
            if 'all_characters' in all_characters_cache:
                all_characters = all_characters_cache['all_characters']
            else:
                all_characters = list(await collection.find({}).to_list(length=None))
                all_characters_cache['all_characters'] = all_characters

    characters = all_characters[offset:offset + 20]

    if len(characters) > 20:
        characters = characters[:20]
        next_offset = str(offset + 20)
    else:
        next_offset = str(offset + len(characters))

    results = []
    for character in characters:
        global_count = await user_collection.count_documents({'characters.id': character['id']})
        anime_characters = await collection.count_documents({'anime': character['anime']})

        if query.startswith('collection.'):
            user_character_count = sum(c['id'] == character['id'] for c in user.get('characters', []))
            user_anime_characters = sum(c['anime'] == character['anime'] for c in user.get('characters', []))
            caption =f"""<b> OwO! Check out <a href='tg://user?id={user['id']}'>{(escape(user.get('first_name', user['id'])))}</a>'s waifu</b>

<b>{character['anime']} ({user_anime_characters}/{anime_characters})</b>
<b>{character['id']}:</b>{character['name']} (x{user_character_count})

<b>({character['rarity'][0]} 𝙍𝘼𝙍𝙄𝙏𝙔:{character['rarity'][2:]})</b>
"""
    else:
            caption =f"""<b> OwO! Check out Character !!</b>
            
<b>{character['anime']}</b>
<b>{character['id']}:</b>{character['name']}

<b>({character['rarity'][0]} 𝙍𝘼𝙍𝙄𝙏𝙔: {character['rarity'][2:]})</b>
            
<b>Globally catches {global_count} Times...</b>
"""
   results.append(
            InlineQueryResultPhoto(
                thumbnail_url=character['img_url'],
                id=f"{character['id']}_{time.time()}",
                photo_url=character['img_url'],
                caption=caption,
                parse_mode='HTML'
            )
        )

    await update.inline_query.answer(results, next_offset=next_offset, cache_time=5)

application.add_handler(InlineQueryHandler(inlinequery, block=False))
