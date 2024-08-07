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
    # if call.data == 'favorites' or call.data == 'all_crypto':
    if call.data == 'favorites':
        markup = types.InlineKeyboardMarkup(row_width=2)
        for i in range(0, len(favourite_coins), 2):
            btn1 = types.InlineKeyboardButton(favourite_coins[i], callback_data=favourite_coins[i])
            if i + 1 < len(favourite_coins):
                btn2 = types.InlineKeyboardButton(favourite_coins[i + 1], callback_data=favourite_coins[i + 1])
                markup.add(btn1, btn2)
            else:
                markup.add(btn1)

        back_btn = types.InlineKeyboardButton('<-Назад', callback_data='get_back')
        markup.add(back_btn)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Избранные криптовалюты:", reply_markup=markup)

    elif call.data == 'all_crypto':
        markup = types.InlineKeyboardMarkup(row_width=2)
        for i in range(0, len(all_currencies), 2):
            btn1 = types.InlineKeyboardButton(all_currencies[i], callback_data=all_currencies[i])
            if i + 1 < len(all_currencies):
                btn2 = types.InlineKeyboardButton(all_currencies[i + 1], callback_data=all_currencies[i + 1])
                markup.add(btn1, btn2)
            else:
                markup.add(btn1)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Выберите криптовалюту:", reply_markup=markup)

    elif call.data in all_currencies or call.data in favourite_coins:
        markup = types.InlineKeyboardMarkup(row_width=1)
        crypto_id = currencies_id[call.data]
        cryptocurrency = call.data
        price = get_price_id(crypto_id)
        back_btn = types.InlineKeyboardButton('<-Назад', callback_data='get_back')
        fav_btn = types.InlineKeyboardButton("Добавить в избранное ★",
                                             callback_data=f'add_to_favourite_{cryptocurrency}')
        markup.add(back_btn, fav_btn)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'1 {cryptocurrency} -> {round(price, 4)} USDT', reply_markup=markup)

    elif call.data.startswith('add_to_favourite_'):
        cryptocurrency = call.data.split('_')[-1]
        if cryptocurrency not in favourite_coins:
            favourite_coins.append(cryptocurrency)
        bot.answer_callback_query(call.id, text=f"{cryptocurrency} добавлен в избранное!")

    elif call.data == 'get_back':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Избранные", callback_data='favorites')
        btn2 = types.InlineKeyboardButton("Все криптовалюты", callback_data='all_crypto')
        markup.add(btn1, btn2)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Выберите раздел:", reply_markup=markup)


def get_price_id(crypto_id):
    price_url = f"https://openapiv1.coinstats.app/coins/{crypto_id}"
    response = requests.get(price_url, headers=headers).json()

    return response['price']


bot.infinity_polling()
