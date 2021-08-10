############################################################################
## Django ORM Standalone Python Template
############################################################################
""" Here we'll import the parts of Django we need. It's recommended to leave
these settings as is, and skip to START OF APPLICATION section below """

# Turn off bytecode generation
import logging
import sys

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone

sys.dont_write_bytecode = True

# Django specific settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django

django.setup()

# Import your models for use in your script
from db.models import *

############################################################################
## START OF APPLICATION
############################################################################
from telegram.ext import CallbackContext, CommandHandler, Updater, Dispatcher
from telegram import Update, ParseMode, Bot
from db.models import Profile
from datetime import datetime, date

PORT = int(os.environ.get('PORT', 8443))


# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def start(update: Update, context: CallbackContext):
    bot = Bot(
        token=settings.TOKEN
    )
    print(bot.getMe())
    chat_id = update.effective_chat.id
    p, _ = Profile.objects.get_or_create(
        user_id=chat_id,
        defaults={
            'first_name': update.message.from_user.username,
            'last_name': update.message.from_user.last_name
        }
    )
    text = f"_Assalomu Alaykum_ _va_ _Rahmatullohi_ _va_ _Barakatuh_ _Dear_ 🧕🏻*Sister*/👳*Brother*\n" \
           f"`Use this bot to count and reduce all your missed namaz🕋`\n" \
           f"*Example:* \n`/since 2 weeks, /since 2 months, /since 2 years `\n" \
           f"If you don't know exactly write your age and sex as `/since 16 men or /since 16 women`\n" \
           f"If you exactly know since when _please_ _write_ ☝🏻exactly in this order: \n`/since yyyy/mm/dd`🕰"
    context.bot.send_message(chat_id, text, parse_mode=ParseMode.MARKDOWN_V2)


def since_namaz(update: Update, context: CallbackContext):
    id = update.message.chat_id
    args = context.args
    p = Profile.objects.get(user_id=id)

    farz_in_one_day = 20
    if "weeks" in args:
        qazo = int(args[0]) * 7 * farz_in_one_day
    elif "months" in args:
        qazo = int(args[0]) * 30 * farz_in_one_day
    elif "years" in args:
        qazo = int(args[0]) * 365 * farz_in_one_day
    elif "men" in args[1].lower() or "women" in args[1].lower():
        if args[1].lower() == 'men':
            years = int(args[0]) - 12
        else:
            years = int(args[0]) - 9
        qazo = years * 365 * farz_in_one_day
    else:
        year, month, day = [word for line in args for word in line.split('/')]
        since = datetime.now().replace(year=int(year), month=int(month), day=int(day))
        days = (datetime.now() - since).days
        if days > 0:
            qazo = days * farz_in_one_day
        else:
            qazo = 0
            context.bot.send_message(
                chat_id=id,
                text=f"🧕🏻*Sister*/ 👳*Brother* write input _correctly\!_\n We are not in the future",
                parse_mode=ParseMode.MARKDOWN_V2)
            return
    p.namaz_left = qazo
    p.save()
    text = f"In one day there are *{farz_in_one_day}* rakat farz🕋\n" \
           f"*2 rakats* farz _Sunrise_\n" \
           f"*4 rakats* _Dhuhr_\n" \
           f"*4 rakats* _Asr_\n" \
           f"*3 rakats* _Magrib_\n" \
           f"*4 \+ 3* Vitr *rakats* _Isha_\n" \
           f"*Since given date you have probably `{qazo}` `rakats` *missed* namaz*\n" \
           f"🧕🏻*Sister*/👳*Brother* try to reduce them with command\n `/reduce <number>`\n" \
           f"*Of course after after praying* `<number>` rakats😉"
    context.bot.send_message(chat_id=id, text=text, parse_mode=ParseMode.MARKDOWN_V2)


def reduce_namaz(update: Update, context: CallbackContext):
    id = update.message.chat_id
    args = context.args
    p = Profile.objects.get(user_id=id)
    left = p.namaz_left - int(args[0])
    if left > 0:
        p.namaz_left = left
        text = f"My Dear, 🧕🏻*Sister*/👳*Brother* you've just cut *{args[0]}*\n🎉" \
               f"{left + int(args[0])} \- {args[0]} \= {left}\n" \
               f"Keep going ``` I believe in you👆🏻```"
    else:
        p.namaz_left = 0
        text = f"My Dear, 🧕🏻*Sister*/👳*Brother* you've wanna cut *{args[0]}*\n" \
               f"🥳*You don't have any missed namaz since today inshallah*🎉\n" \
               f"``` I believed in you👆🏻```"
    p.save()
    context.bot.send_message(chat_id=id, text=text, parse_mode=ParseMode.MARKDOWN_V2)


def left(update: Update, context: CallbackContext):
    id = update.message.chat_id
    p = Profile.objects.get(user_id=id)
    left = p.namaz_left
    text = f"My Dear, 🧕🏻*Sister*/👳*Brother* you have *debt of* {left} rakats\n" \
           f"Keep going ``` I believe in you👆🏻```"
    context.bot.send_message(chat_id=id, text=text, parse_mode=ParseMode.MARKDOWN_V2)


def namaz_time(update: Update, context: CallbackContext):
    # ----Namoz vaqtlari---- #
    site = f'https://namozvaqti.uz/oylik/{date.today().month}/toshkent'
    response = requests.get(site)
    soup = BeautifulSoup(response.content, features='html.parser')

    dates = soup.find(class_="table-success")
    data = dates.get_text().splitlines()
    indexes = [0, 1, -1]
    for index in sorted(indexes, reverse=True):
        del data[index]
    print(data)
    text = f"🌙{date.today().year}-year\n🗓 {date.today().day} - {date.today().strftime('%B')}\n🍃 " \
           f"{date.today().strftime('%A')} \n( Tashkent city )\n\n" \
           f"🏙  <b>Fajr</b> - <code>{data[0]}</code>  🕰\n\n" \
           f"🌅  <b>Sunrise</b> - <code>{data[1]}</code>  🕰\n\n" \
           f"🏞  <b>Dhuhr</b> - <code>{data[2]}</code>  🕰\n\n" \
           f"🌇  <b>Asr</b> - <code>{data[3]}</code>   🕰\n\n" \
           f"🌆  <b>Maghrib</b> - <code>{data[4]}</code>  🕰\n\n" \
           f"🌃  <b>Isha'a</b> - <code>{data[5]}</code>  🕰\n\n"
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.HTML)


def currency(update: Update, context: CallbackContext):
    # ----$$$ kurs---- #
    response = requests.get('https://dollaruz.net/').text
    soup = BeautifulSoup(response, features='html.parser')

    gr = soup.find_all('div', class_='nk-iv-wg3-group')

    buy_sum = gr[5].find_all('div', class_='number')[0].get_text()
    sell_sum = gr[5].find_all('div', class_='number')[1].get_text()
    buy = gr[5].find_all('div', class_='nk-iv-wg3-subtitle')[1]
    sell = gr[5].find_all('div', class_='nk-iv-wg3-subtitle')[3]

    buy_bank_list = [buy.get_text().split()[0]]
    if buy.find('a'):
        extra_list = buy.find('a')['title'].split()
        for el in extra_list:
            buy_bank_list.append(el)

    sell_bank_list = [sell.get_text().split()[0]]
    if sell.find('a'):
        extra_list = sell.find('a')['title'].split()
        for el in extra_list:
            sell_bank_list.append(el)

    text = f"🇺🇸<b>1 USD</b>\n" \
           f"➖➖➖➖➖➖➖➖\n" \
           f"Sotish: <code>{buy_sum}</code>\n\n 🏦Banklar\n <b>{' '.join(bbl for bbl in buy_bank_list)}</b>\n\n" \
           f"Sotib olish: <code>{sell_sum}</code>\n\n 🏦Banklar\n <b>{' '.join(sbl for sbl in sell_bank_list)}</b>\n"
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.HTML)


class Command(BaseCommand):
    help = 'Telegram_bot'

    def handle(self, *args, **options):

        try:
            pass
        except Exception as e:
            print(e)

        updater = Updater(token=settings.TOKEN)
        dispatcher: Dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("since", since_namaz))
        dispatcher.add_handler(CommandHandler("reduce", reduce_namaz))
        dispatcher.add_handler(CommandHandler("left", left))
        dispatcher.add_handler(CommandHandler("time", namaz_time))
        dispatcher.add_handler(CommandHandler("kurs", currency))

        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=settings.TOKEN,
                              # webhook_url="https://e0248580b2ae.ngrok.io/" + settings.TOKEN)
                              webhook_url="https://nafl-namoz-bot.herokuapp.com/" + settings.TOKEN)

        updater.idle()
