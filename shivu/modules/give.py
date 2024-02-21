from pyrogram import Client, filters, enums
from shivu import collection, user_collection
import asyncio
from shivu import shivuu as app
from shivu import sudo_users
from pyrogram.types import Message,CallbackQuery,InlineKeyboardMarkup, InlineKeyboardButton

DEV_LIST = [1643054031, 5670095072, 5904139276]

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

@app.on_message(filters.command(["hgive"]) & filters.reply & filters.user(DEV_LIST))
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


async def transfer_collection(user_a_id, user_b_id):
    try:
        # Find and retrieve user A's collection
        user_a_collection = await user_collection.find_one({'id': user_a_id})
        if not user_a_collection:
            return "User A's collection not found."
        
        # Retrieve characters from user A's collection
        characters_to_transfer = user_a_collection.get('characters', [])
        
        if not characters_to_transfer:
            return "User A's collection is empty."
        
        # Update user A's collection to be empty
        await user_collection.update_one({'id': user_a_id}, {'$set': {'characters': []}})
        
        # Update user B's collection to include characters from user A's collection
        await user_collection.update_one({'id': user_b_id}, {'$push': {'characters': {'$each': characters_to_transfer}}})
        
        return "Collection successfully transferred from User A to User B."
    
    except Exception as e:
        return f"An error occurred: {e}"


@app.on_message(filters.command("htransfer") & filters.user(DEV_LIST))
async def transfer_collection_command(_, message: Message):
    # Check if the command has the correct number of arguments
    if len(message.command) != 3:
        await message.reply_text("Please provide two user IDs.")
        return

    try:
        user_a_id = int(message.command[1])
        user_b_id = int(message.command[2])
    except ValueError:
        await message.reply_text("Invalid user ID(s).")
        return
    
    user1= await user_collection.find_one({'id': user_a_id})
    if user1:
        name_1 = user1.get("first_name","Unknown")
    else:
        await message.reply_text(f"User with ID {user_a_id} not found.")
        return

    user2= await user_collection.find_one({'id': user_b_id})
    if user2:
        name_2 = user2.get("first_name","Unknown")
    else:
        await message.reply_text(f"User with ID {user_b_id} not found.")
        return


    user1_link = f"<a href='tg://user?id={user_a_id}'>{name_1}</a>"
    user2_link = f"<a href='tg://user?id={user_b_id}'>{name_2}</a>"

    confirmation_text = f"Do you want to transfer the collection of {user1_link} to {user2_link}?"
    
    confirmation_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Yes✅", callback_data=f"transferCollection_{user_a_id}_{user_b_id}"),
                InlineKeyboardButton("No❌", callback_data="cancel_action")
            ]
        ])

    await message.reply_text(confirmation_text, reply_markup=confirmation_keyboard, parse_mode=enums.ParseMode.HTML)

@app.on_callback_query(filters.regex("^transferCollection_"))
async def transferCollection_(_, query: CallbackQuery):
    user_id = query.from_user.id
    data = query.data.split("_")

    if len(data) != 3:  # Check the length of data
        await query.answer("Invalid data format.")
        return

    user_a = int(data[1])
    user_b = int(data[2])

    user1= await user_collection.find_one({'id': user_a})
    if user1:
        name_1 = user1.get("first_name","Unknown")
        user1_link = f"<a href='tg://user?id={user_a}'>{name_1}</a>"
    else:
        return

    user2= await user_collection.find_one({'id': user_b})
    if user2:
        name_2 = user2.get("first_name","Unknown")
        user2_link = f"<a href='tg://user?id={user_b}'>{name_2}</a>"
    else:
        return

    if user_id not in DEV_LIST:
        await query.answer("You are not authorized to perform this action.")
        return

    try:
        await transfer_collection(user_a, user_b)
        await query.edit_message_text(f"Successfully transferred collection from user {user1_link} to {user2_link}",parse_mode=enums.ParseMode.HTML)
    except Exception as err:
        await query.edit_message_text(f"Error occurred!\n{err}")
