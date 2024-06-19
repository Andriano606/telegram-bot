import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from rapid_manager import InstagramManager
from telegram_bot_manager import TelegramBotManager
from rapid_parser import RapidParser
from db_managaer import DBManager

# Database manager initialization
db_manager = DBManager("vika_jopka", "postgres", "secret")
db_manager.create_database()
db_manager.connect()
db_manager.create_table()
db_manager.create_users_table()

# Instagram and Telegram manager initialization
instagram_manager = InstagramManager()
bot_manager = TelegramBotManager(token='7205301730:AAHS-QCbkdQhfkBPOLrDIa3qy-MVnOvJnpM', db_manager=db_manager, instagram_manager=instagram_manager)

async def send_messages():
    print('send_messages')

    users = db_manager.get_all_users()
    for user in users:
        user_id = user[0]
        instagram_channels = user[1]
        for channel in instagram_channels:
            data = instagram_manager.fetch_posts(channel)
            rapid_parser = RapidParser(data)
            await bot_manager.send_posts(user_id, rapid_parser, channel)

async def on_startup():
    # Initialize scheduler
    scheduler = AsyncIOScheduler()

    # Schedule the send_messages task to run every hour
    scheduler.add_job(send_messages, 'cron', minute=0)

    # Start the scheduler
    scheduler.start()

    # Keep the script running
    while True:
        await asyncio.sleep(3600)

async def main():
    await on_startup()

if __name__ == '__main__':
    asyncio.run(main())
