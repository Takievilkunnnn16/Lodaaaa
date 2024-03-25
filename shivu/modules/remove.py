from pyrogram import Client, filters
from shivu import db, collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection
import asyncio
from shivu import shivuu as app

DEV_LIST = [1643054031]

async def remove_all_characters_for_user(user_id):
    user = await user_collection.find_one({'id': user_id})

    if user:
        await user_collection.update_one(
            {'id': user_id},
            {'$set': {'characters': []}}
        )

        return f"Successfully removed all characters for user {user_id}"
    else:
        return f"User with ID {user_id} not found."

@app.on_message(filters.command(["hremove"]) & filters.user(DEV_LIST))
async def remove_characters_command(client, message):
    if len(message.command) == 2:
        try:
            user_id_to_remove_characters_for = int(message.command[1])
            result_message = await remove_all_characters_for_user(user_id_to_remove_characters_for)
            await message.reply_text(result_message)
        except ValueError:
            await message.reply_text("Invalid User Id/ User Not Found")
    else:
        await message.reply_text("Use Like This Sor /remove {id}")
