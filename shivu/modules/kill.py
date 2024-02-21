from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from shivu import collection, user_collection, application
import asyncio
from telegram.ext import CommandHandler, MessageHandler, filters

DEV_LIST = [1643054031, 5670095072, 5904139276]


async def add_all_characters_for_user(user_id):
    user = await user_collection.find_one({'id': user_id})

    if user:
        all_characters_cursor = collection.find({})
        all_characters = await all_characters_cursor.to_list(length=None)

        existing_character_ids = {character['id'] for character in user['characters']}
        new_characters = [character for character in all_characters if character['id'] not in existing_character_ids]

        if new_characters:
            await user_collection.update_one(
                {'id': user_id},
                {'$push': {'characters': {'$each': new_characters}}}
            )

            return f"Successfully added characters for user {user_id}"
        else:
            return f"No new characters to add for user {user_id}"
    else:
        return f"User with ID {user_id} not found."

async def add(update: Update, context: CallbackContext) -> None:
    message = update.effective_message
    if not message.reply_to_message:
        await message.reply_text("You need to reply to a user's message to give a character!")
        return
    user_id_to_add_characters_for = message.reply_to_message.from_user.id
    result_message = await add_all_characters_for_user(user_id_to_add_characters_for)
    await message.reply_text(result_message)


async def kill_character(receiver_id, character_id):
    character = await collection.find_one({'id': character_id})

    if character:
        try:
            await user_collection.update_one(
                {'id': receiver_id},
                {'$pull': {'characters': {'id': character_id}}}
            )

            return f"Successfully removed character {character_id} from user {receiver_id}"
        except Exception as e:
            print(f"Error updating user: {e}")
            raise
    else:
        raise ValueError("Character not found.")

async def kill(update: Update, context: CallbackContext) -> None:
    message = update.effective_message
    try:
        character_id = str(message.text.split()[1])
        receiver_id = message.reply_to_message.from_user.id

        result_message = await kill_character(receiver_id, character_id)

        await message.reply_text(result_message)
    except (IndexError, ValueError) as e:
        await message.reply_text(str(e))
    except Exception as e:
        print(f"Error in remove_character_command: {e}")
        await message.reply_text("An error occurred while processing the command.")


application.add_handler(CommandHandler("add", add, filters.User(DEV_LIST), block=False))
application.add_handler(CommandHandler("hkill", kill, filters.User(DEV_LIST), block=False))
