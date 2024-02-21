from pyrogram import Client, filters, enums
from shivu import event_collection as collection, user_collection
import asyncio
from shivu import shivuu as app
from shivu import sudo_users

DEV_LIST = [1643054031, 5904139276]

async def give_character(receiver_id, character_id, message):
    character = await collection.find_one({'id': character_id})

    if character:
        try:
            await user_collection.update_one(
                {'id': receiver_id},
                {'$push': {'characters': character}}
            )

            user_mention = message.reply_to_message.from_user.mention if message.reply_to_message else "Unknown User"
            caption = (
                f"Successfully Given To {user_mention}\n"
                f"Name: {character['name']}"
            )

            return caption
        except Exception as e:
            print(f"Error updating user: {e}")
            raise
    else:
        raise ValueError(f"Character not found. {character_id}")

@app.on_message(filters.command(["egive"]) & filters.reply & filters.user(DEV_LIST))
async def give_character_command(client, message):
    if not message.reply_to_message:
        await message.reply_text("You need to reply to a user's message to give a character!")
        return
    try:
        if len(message.command) < 2:
            raise ValueError("Please provide the ID of the character.")

        character_id = str(message.command[1])

        receiver_id = message.reply_to_message.from_user.id if message.reply_to_message else None

        if receiver_id:
            result = await give_character(receiver_id, character_id, message)
            caption = result if result else "An error occurred while processing the command."
        else:
            caption = "Unknown user to give the character."

        await message.reply_text(text=caption, parse_mode=enums.ParseMode.HTML)
    except (ValueError, IndexError):
        await message.reply_text("Dear pros, please provide the ID of the character")
    except Exception:
        await message.reply_text("An error occurred while processing the command. Report @ikaris0_0")
