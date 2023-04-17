import logging
from html import escape
from uuid import uuid4

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import *
from telegram.constants import ParseMode
from telegram.ext import *
import openai
import random

from serpapi import GoogleSearch
import requests
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")
# serpi_api_key = os.getenv("SERP_API_KEY") 
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Hello! I'm @Django_telbot, your virtual assistant..\nAsk anything or type @Django_telbot to search images.")

async def inline_query(update:Update, context: CallbackContext):
    try:
        query = update.inline_query.query
        if query == "":
            return

        endpoint = 'https://api.unsplash.com/search/photos'
        params = {
            'per_page' : 55,
            'query': query,
            'client_id': UNSPLASH_ACCESS_KEY
        }
        # Send GET request to the API
        response = requests.get(endpoint, params=params)
        response.raise_for_status() # Raise exception if response is not successful
        data = response.json()

        # Extract image URLs from the API response
        image_urls = [result['urls']['regular'] for result in data['results']]
        result = []        
        for idx, image_url in enumerate(image_urls):
                photo_result = InlineQueryResultPhoto(
                    id=idx,
                    photo_url=image_url,
                    thumbnail_url=image_url,
                    photo_height=100,
                    photo_width=100
                )
                result.append(photo_result)
        await context.bot.answer_inline_query(update.inline_query.id, result)
    except Exception as e:
        return

    # try:
    #     images = []
    #     query = update.inline_query.query
    #     if query == "":
    #         return
    #     response = openai.Image.create(
    #     prompt=query,
    #     n=10,
    #     size="1024x1024"
    #     ) 
    #     for i in response['data']:
    #         url = i['url']
    #         images.append(url)
    #     result = []        
    #     for idx, image_url in enumerate(image_urls):
    #             photo_result = InlineQueryResultPhoto(
    #                 id=idx,
    #                 photo_url=image_url,
    #                 thumbnail_url=image_url,
    #                 photo_height=100,
    #                 photo_width=100
    #             )
    #             result.append(photo_result)
    #     await context.bot.answer_inline_query(update.inline_query.id, result)
    # except Exception as e:
    #     return

async def handle_message(update: Update, context):
    user_input = update.message.text
    response = gpt3_response(user_input)
    await update.message.reply_text(response)

def gpt3_response(user_input):
    try:
        response = openai.Completion.create(
        model="text-davinci-003",
        prompt=user_input,
        temperature=0,
        max_tokens=255,
        )  
        print(response)
        response = response.choices[0].text
        return response
    except:
        response = "Sorry i am temporarily unavailable"
        return response

def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(InlineQueryHandler(inline_query))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    application.run_polling()
    updater.idle()

if __name__ == "__main__":
    main()
