import telebot
from telebot import types
import requests
import json

API_TOKEN = '7107117054:AAFjuZttOk1rfCOhodWhmbaR1_Z7l5owf4c'
url = "https://openapiv1.coinstats.app/coins/"

headers = {
    "accept": "application/json",
    "X-API-KEY": "bTLH6MwYNtnDZJEZwrVcr4KQuVG9oWXQDKKfEMXjDck="
}
response = requests.get(url, headers=headers).json()

all_currencies = []
# for currency in range(0,20):
    # all_currencies.append(response['result'][currency]['symbol'])
for currency in response['result']:
    all_currencies.append(currency["symbol"])


print(all_currencies)

# bot = telebot.TeleBot(API_TOKEN)

# @bot.message_handler(commands=['start'])
# def start(message):
#     markup = types.InlineKeyboardMarkup()
#     btn1 = types.InlineKeyboardButton("Избранные", callback_data='favorites')
#     btn2 = types.InlineKeyboardButton("Все криптовалюты", callback_data='all_crypto')
#     markup.add(btn1, btn2)
#     bot.send_message(message.chat.id, "Выберите раздел:", reply_markup=markup)

# @bot.callback_query_handler(func=lambda call: True)
# def callback_inline(call):
#     if call.data == 'favorites':
#         bot.send_message(call.message.chat.id, "Вы выбрали раздел 'Избранные'.")
#     elif call.data == 'all_crypto':
#         markup = types.InlineKeyboardMarkup()
#         for crypto in crypto_list:
#             btn = types.InlineKeyboardButton(crypto, callback_data=crypto)
#             markup.add(btn)
#         bot.send_message(call.message.chat.id, "Выберите криптовалюту:", reply_markup=markup)
#     elif call.data in crypto_list:
#         bot.send_message(call.message.chat.id, )

# bot.infinity_polling()
