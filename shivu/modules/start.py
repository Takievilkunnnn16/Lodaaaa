import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler
from telegram.ext import MessageHandler, filters
from telegram.ext import CommandHandler
from shivu import application 
from shivu import db, GROUP_ID, OWNER_ID 
from shivu import PHOTO_URL, SUPPORT_CHAT, UPDATE_CHAT, BOT_USERNAME 
import random
collection = db['total_pm_users']


async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username

    user_data = await collection.find_one({"_id": user_id})

    if user_data is None:
        
        await collection.insert_one({"_id": user_id, "first_name": first_name, "username": username})
        
        await context.bot.send_message(chat_id=GROUP_ID, text=f"<a href='tg://user?id={user_id}'>{first_name}</a> STARTED THE BOT", parse_mode='HTML')
    else:
        
        if user_data['first_name'] != first_name or user_data['username'] != username:
            
            await collection.update_one({"_id": user_id}, {"$set": {"first_name": first_name, "username": username}})

    

    if update.effective_chat.type== "private":
        
        
        caption = f"""
        ***🎐 ʜᴇʏ ᴛʜᴇʀᴇ...!  {update.effective_user.first_name} *
              
***◎ ─━──━─❖─━──━─ ◎
⍟ ɪ ᴀᴍ ᴄᴀᴛᴄʜ ʏᴏᴜʀ ʜᴜꜱʙᴀɴᴅᴏ ʙᴏᴛ,
ɪ sᴘᴀᴡɴ ᴀɴɪᴍᴇ ᴄʜᴀʀᴀᴄᴛᴇʀs ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘs, ᴀɴᴅ ʟᴇᴛ ᴜsᴇʀs ᴄᴏʟʟᴇᴄᴛ ᴛʜᴇᴍ.
⍟ sᴏ ᴡʜᴀᴛ ᴀʀᴇ ʏᴏᴜ ᴡᴀɪᴛɪɴɢ ғᴏʀ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ʙʏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ.
◎ ─━──━─❖─━──━─ ◎

ʜɪᴛ help ᴛᴏ ғɪɴᴅ ᴏᴜᴛ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ.***
               """
        keyboard = [
            [InlineKeyboardButton("✦ ᴀᴅᴅ ᴍᴇ ✦", url=f'http://t.me/Catch_Your_Waifu_Bot?startgroup=new')],
            [InlineKeyboardButton("¤ ʜᴇʟᴘ ¤", callback_data='help'),
             InlineKeyboardButton("⌬ sᴜᴘᴘᴏʀᴛ ⌬", url=f'https://t.me/{SUPPORT_CHAT}')],
            [InlineKeyboardButton("⍟ ᴜᴘᴅᴀᴛᴇs ⍟", url=f'https://t.me/{UPDATE_CHAT}')],
            
  ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        photo_url = random.choice(PHOTO_URL)

        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption=caption, reply_markup=reply_markup, parse_mode='markdown')

    else:
        photo_url = random.choice(PHOTO_URL)
        keyboard = [
            
            [InlineKeyboardButton("¤ ʜᴇʟᴘ ¤", callback_data='¤ ʜᴇʟᴘ ¤'),
             InlineKeyboardButton("⌬ sᴜᴘᴘᴏʀᴛ ⌬", url=f'https://t.me/{SUPPORT_CHAT}')],
            
  ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption="I am alive",reply_markup=reply_markup )

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        help_text = """
    ***Help Section :***
    
***/guess: To Guess character (only works in group)***
***/hfav: Add Your fav***
***/htrade : To trade Characters***
***/hgift: Give any Character from Your Collection to another user.. (only works in groups)***
***/hharem: To see Your harem list***
***/topgroups : See Top Groups.. Ppl Guesses Most in that Groups***
***/top: Too See Top Users***
***/ctop : Your ChatTop***
***/changetime: Change Character appear time (only works in Groups)***
   """
        help_keyboard = [[InlineKeyboardButton("Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(help_keyboard)
        
        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=help_text, reply_markup=reply_markup, parse_mode='markdown')

    elif query.data == 'back':

        caption = f"""
        ***🎐 ʜᴇʏ ᴛʜᴇʀᴇ...! {update.effective_user.first_name} *
              
***◎ ─━──━─❖─━──━─ ◎
⍟ ɪ ᴀᴍ ᴄᴀᴛᴄʜ ʏᴏᴜʀ ʜᴜꜱʙᴀɴᴅᴏ ᴡᴀɪғᴜ ʙᴏᴛ,
ɪ sᴘᴀᴡɴ ᴀɴɪᴍᴇ ᴄʜᴀʀᴀᴄᴛᴇʀs ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘs, ᴀɴᴅ ʟᴇᴛ ᴜsᴇʀs ᴄᴏʟʟᴇᴄᴛ ᴛʜᴇᴍ.
⍟ sᴏ ᴡʜᴀᴛ ᴀʀᴇ ʏᴏᴜ ᴡᴀɪᴛɪɴɢ ғᴏʀ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ʙʏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ.
◎ ─━──━─❖─━──━─ ◎

ʜɪᴛ help ᴛᴏ ғɪɴᴅ ᴏᴜᴛ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ.***
        """
        keyboard = [
            [InlineKeyboardButton("✦ ᴀᴅᴅ ᴍᴇ ✦", url=f'http://t.me/Catch_Your_Waifu_Bot?startgroup=new')],
            [InlineKeyboardButton("¤ ʜᴇʟᴘ ¤", callback_data='¤ ʜᴇʟᴘ ¤'),
             InlineKeyboardButton("⌬ sᴜᴘᴘᴏʀᴛ ⌬", url=f'https://t.me/{SUPPORT_CHAT}')],
            [InlineKeyboardButton("⍟ ᴜᴘᴅᴀᴛᴇs ⍟", url=f'https://t.me/{UPDATE_CHAT}')],
            
]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=caption, reply_markup=reply_markup, parse_mode='markdown')

application.add_handler(CallbackQueryHandler(button, pattern='^help$|^back$', block=False))
start_handler = CommandHandler('start', start, block=False)
application.add_handler(start_handler)
