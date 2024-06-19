from db_managaer import DBManager
from rapid_manager import InstagramManager
from telegram_bot_manager import TelegramBotManager
from rapid_parser import RapidParser

# Create a new instance of the DBManager class
db_manager = DBManager("vika_jopka", "postgres", "secret")
db_manager.create_database()
db_manager.connect()
db_manager.create_table()
db_manager.create_users_table()

# Fetch data from Instagram
instagram_manager = InstagramManager()

# Run the Telegram bot in a separate thread
bot_manager = TelegramBotManager(token='7205301730:AAHS-QCbkdQhfkBPOLrDIa3qy-MVnOvJnpM', db_manager=db_manager, instagram_manager=instagram_manager)
bot_manager.run()