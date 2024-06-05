from telegram.ext import CommandHandler
from telegram.constants import ParseMode
import random
import string
import datetime
from shivu import application, user_collection, collection

# Dictionary to store user last usage time for daily_code command
last_usage_time = {}

# Dictionary to store generated waifus and their details
generated_waifus = {}

# Sudo user IDs
sudo_user_ids = ["1643054031", "6384296585"]

# Sudo user ID to send logs
log_sudo_user_ids = ["1643054031", "6384296585"]

# Function to generate a random string of length 5 composed of random letters
def generate_random_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

# Function to handle the waifugen command
async def waifugen(update, context):
    if str(update.effective_user.id) not in sudo_user_ids:
        await update.message.reply_text("You are not authorized to generate waifus.")
        return
    
    try:
        waifu_id = context.args[0]  # Get the waifu ID from the command
        quantity = int(context.args[1])  # Get the quantity from the command
    except (IndexError, ValueError):
        await update.message.reply_text("Invalid usage. Usage: /pgen <waifu_id> <quantity>")
        return

    # Find the waifu by ID
    waifu = await collection.find_one({'_id': waifu_id})
    if not waifu:
        await update.message.reply_text("Failed to find waifu with the provided ID.")
        return

    code = generate_random_code()
    
    # Store the generated waifu and its details
    generated_waifus[code] = {'waifu': waifu, 'quantity': quantity}
    
    response_text = (
        f"Generated Husbando:\n`\n{code}\n```\n"
        f"Name: {waifu['name']}\nRarity: {waifu['rarity']}\nQuantity: {quantity}"
    )
    
    await update.message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)
    
    # Log the waifu generation
    log_text = (
        f"Husbando generated by user {update.effective_user.id}:\n"
        f"Code: {code}\nName: {waifu['name']}\nRarity: {waifu['rarity']}\nQuantity: {quantity}"
    )
    for log_user_id in log_sudo_user_ids:
        await context.bot.send_message(chat_id=log_user_id, text=log_text)

# Function to claim a generated waifu
async def claimwaifu(update, context):
    code = " ".join(context.args)  # Get the code from the command
    user_id = update.effective_user.id
    user_mention = f"[{update.effective_user.first_name}](tg://user?id={user_id})"

    if code in generated_waifus:
        details = generated_waifus[code]
        
        if details['quantity'] > 0:
            waifu = details['waifu']
            
            # Update the user's characters collection
            await user_collection.update_one(
                {'id': user_id},
                {'$push': {'characters': waifu}}
            )
            
            # Decrement the remaining quantity
            details['quantity'] -= 1
            
            # Remove the code if its quantity is 0
            if details['quantity'] == 0:
                del generated_waifus[code]
            
            response_text = (
                  f"**Congratulations**  {mention}!\n\n**Your redeem Prize is:**\n**❄️ Name:** {character['name']}\n**🍂 Anime:** {character['anime']}\n\n**"""
           )
            await update.message.reply_photo(photo=waifu['img_url'], caption=response_text, parse_mode=ParseMode.MARKDOWN)
            
            # Log the waifu claim
            log_text = (
                f"Husbando redeem by user {user_id}:\n"
                f"Code: {code}\nName: {waifu['name']}\nRarity: {waifu['rarity']}\nRemaining quantity: {details['quantity']}"
            )
            for log_user_id in log_sudo_user_ids:
                await context.bot.send_message(chat_id=log_user_id, text=log_text)
        else:
            await update.message.reply_text("This code is already been claimed the maximum number of times.")
    else:
        await update.message.reply_text("Invalid code.")

# Add command handlers to the bot
application.add_handler(CommandHandler("gen", waifugen))
application.add_handler(CommandHandler("redeem", claimwaifu))
