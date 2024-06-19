import logging
import signal
from telegram import Update, Bot
from telegram.ext import filters, ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext, MessageHandler
from rapid_parser import RapidParser

class TelegramBotManager:
    def __init__(self, token, db_manager, instagram_manager):
        self.token = token
        # self.bot = Bot(token=token)
        self.application = ApplicationBuilder().token(self.token).build()
        self.db_manager = db_manager
        self.instagram_manager = instagram_manager

        # Configure logging
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

    def command_wrapper(self, command_name):
        def decorator(command_handler):
            async def wrapper(update: Update, context: CallbackContext):
                user = update.effective_user
                print(f'User {user.username} ({user.id}) is executing command {command_name}')

                # Add the user to the database
                self.db_manager.add_user(user.id)

                # Store the last command used
                context.user_data['last_command'] = command_name

                return await command_handler(update, context)
            return wrapper
        return decorator
    
    async def add_new_instagram_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
      await update.message.reply_text("Please send the name of the Instagram channel you want to subscribe to.")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        description = (
            "Welcome! This bot checks for new posts on Instagram channels every hour. "  
        )
        await update.message.reply_text(description, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_message = update.message.text

        if context.user_data['last_command'] == 'add_new_instagram_channel':
            exist = await self.check_if_instagram_channel_exist_and_subscribe(user_message, update)

            if exist:
              data = self.instagram_manager.fetch_posts(user_message)
              rapid_parser = RapidParser(data)

              for i in range(rapid_parser.data.count):
                new_post = self.db_manager.add_post(rapid_parser.data.items[i].id, update.effective_user.id, user_message)

                # if new_post:
                # await self.send_posts(update.effective_chat.id, rapid_parser, user_message)

        # Reset last command
        context.user_data['last_command'] = ''

    async def send_message_to_user(self, user_id: int, message: str) -> None:
        await self.application.bot.send_message(chat_id=user_id, text=message)
        
    async def send_posts(self, user_id, rapid_parser, channel) -> None:
      for i in range(rapid_parser.data.count):
        new_post = self.db_manager.add_post(rapid_parser.data.items[i].id, user_id, channel)

        if new_post:
          # Create a caption based on rapid_parser data
          caption = "Channel: " + rapid_parser.data.user.username + "\n\n"
          caption += f"{rapid_parser.data.items[i].caption.text}\n"

          # Send the photo with the caption
          await self.application.bot.send_photo(chat_id=user_id, photo=rapid_parser.data.items[i].image_urls[0], caption=caption)

    async def check_if_instagram_channel_exist_and_subscribe(self, channel_name, update) -> None:
      exist = self.instagram_manager.check_channel_exists(channel_name)

      if exist:
        self.db_manager.add_new_instagram_channel(channel_name, update.effective_user.id)
        await update.message.reply_text(f"Channel {channel_name} has been successfully added.")
      else:
        await update.message.reply_text(f"Channel {channel_name} does not exist.")

      return exist

    def run(self):
        # Add the command handler
        self.application.add_handler(CommandHandler("start", self.command_wrapper("start")(self.start)))
        self.application.add_handler(CommandHandler("add_new_instagram_channel", self.command_wrapper("add_new_instagram_channel")(self.add_new_instagram_channel)))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Start the bot
        self.application.run_polling()