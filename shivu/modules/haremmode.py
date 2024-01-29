from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from html import escape 
from shivu import user_collection, shivuu
class HaremManager:
    def __init__(self):
        self.harem = []
        self.mode = "common"  # Default mode

    def add_to_harem(self, character):
        self.harem.append(character)

    def change_mode(self, new_mode):
        self.mode = new_mode

    def get_harem_in_current_mode(self):
        return [character for character in self.harem if character['rarity'] == self.mode]

# Example usage:
harem_manager = HaremManager()

# Add characters to the harem
harem_manager.add_to_harem({'name': 'Character1', 'rarity': 'common'})
harem_manager.add_to_harem({'name': 'Character2', 'rarity': 'legendary'})
# Add more characters as needed

# Change mode
harem_manager.change_mode("legendary")

# Get harem in the current mode
current_mode_harem = harem_manager.get_harem_in_current_mode()
print(current_mode_harem)

application.add_handler(CommandHandler(["haremmode"], haremmode, block=False))
    application.add_handler(CommandHandler("changeharem", changeharem, block=False))
    application.add_handler(MessageHandler(filters.ALL, message_counter, block=False))
    application.run_polling(drop_pending_updates=True)
