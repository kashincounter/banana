import telebot
from telebot import types
import requests

API_TOKEN = '7107117054:AAFjuZttOk1rfCOhodWhmbaR1_Z7l5owf4c'
COINMARKETCAP_API_KEY = 'd3646ae5-77ca-4ff5-8fbf-aeb74fe051eb'
COINMARKETCAP_API_URL = 'https://pro-api.coinmarketcap.com/v1/c>'

bot = telebot.TeleBot(API_TOKEN)

# Список сокращений криптовалют
crypto_list = ['BTC', 'ETH', 'LTC', 'XRP', 'BCH']

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Избранные", callback_data='favourites')
    btn2 = types.InlineKeyboardButton("Все криптовалюты", callback_data='all currencies')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Выберите раздел:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'favorites':
        bot.send_message(call.message.chat.id, "Вы выбрали раздел: Избранное")
    elif call.data == 'all_crypto':
        markup = types.InlineKeyboardMarkup()
        for crypto in crypto_list:
            btn = types.InlineKeyboardButton(crypto, callback_data=crypto)
            markup.add(btn)
        bot.send_message(call.message.chat.id, "Выберите криптовалюту")

bot.infinity_polling()
