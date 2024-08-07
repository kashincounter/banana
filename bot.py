import telebot
from telebot import types
import requests
import json

API_TOKEN = '7107117054:AAFjuZttOk1rfCOhodWhmbaR1_Z7l5owf4c'
coins_url = "https://openapiv1.coinstats.app/coins/"

headers = {
    "accept": "application/json",
    "X-API-KEY": "bTLH6MwYNtnDZJEZwrVcr4KQuVG9oWXQDKKfEMXjDck="
}
response = requests.get(coins_url, headers=headers).json()

favourite_coins = []
all_currencies = [currency["symbol"] for currency in response['result']]
currencies_id = {currency["symbol"]: currency["id"] for currency in response['result']}

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Избранные", callback_data='favorites')
    btn2 = types.InlineKeyboardButton("Все криптовалюты", callback_data='all_crypto')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Выберите раздел:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'favorites':
        bot.send_message(call.message.chat.id, "Вы выбрали раздел 'Избранные'.")
    elif call.data == 'all_crypto':
        markup = types.InlineKeyboardMarkup(row_width=2)
        for crypto in range(0,len(all_currencies),2):
            btn1 = types.InlineKeyboardButton(all_currencies[crypto], callback_data=all_currencies[crypto])
            btn2 = types.InlineKeyboardButton(all_currencies[crypto + 1], callback_data=all_currencies[crypto + 1])
            markup.add(btn1,btn2)
        bot.send_message(call.message.chat.id, "Выберите криптовалюту:", reply_markup=markup)
    elif call.data in all_currencies:
        crypto_id = currencies_id[call.data]
        price = get_price_id(crypto_id)
        bot.send_message(call.message.chat.id, f'1 {call.data} -> {round(price, 4)} USDT')

def get_price_id(crypto_id):
    price_url = f"https://openapiv1.coinstats.app/coins/{crypto_id}"
    response = requests.get(price_url, headers=headers).json()
    return response['price']


bot.infinity_polling()
