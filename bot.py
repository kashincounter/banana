import cryptocompare
import telebot
from telebot import types
import requests
import json
import threading
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io

# from db import get_user_favorites, add_to_favorites

API_TOKEN = '7107117054:AAFjuZttOk1rfCOhodWhmbaR1_Z7l5owf4c'
COIN_STATS_API_KEY = "bTLH6MwYNtnDZJEZwrVcr4KQuVG9oWXQDKKfEMXjDck="
CRYPTO_COMPARE_API_KEY = "bdf10bc646e114efccaf134bf6c5a9e36e8c10aa73ca28dbc0303645af16f0e6"
cryptocompare.cryptocompare._set_api_key_parameter(CRYPTO_COMPARE_API_KEY)

coins_url = "https://openapiv1.coinstats.app/coins/"

headers = {
    "accept": "application/json",
    "X-API-KEY": COIN_STATS_API_KEY
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

def handler_message(message):
    text = message.text
    data_url = f"https://openapiv1.coinstats.app/coins/{text}"
    response = requests.get(data_url, headers=headers).json()
    bot.send_message(message.chat.id, text=f'1 {response['symbol']} -> {round(response['price'], 4)} USDT')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'favorites':
        markup = types.InlineKeyboardMarkup(row_width=2)
        for i in range(0, len(favourite_coins), 2):
            btn1 = types.InlineKeyboardButton(favourite_coins[i], callback_data=favourite_coins[i])
            if i + 1 < len(favourite_coins):
                btn2 = types.InlineKeyboardButton(favourite_coins[i + 1], callback_data=favourite_coins[i + 1])
                markup.add(btn1,btn2)
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
        search_btn = types.InlineKeyboardButton('Ввести криптовалюту', callback_data='search_crypto')
        markup.add(search_btn)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Выберите криптовалюту:", reply_markup=markup)     
    
    elif call.data == 'search_crypto':
        bot.send_message(call.message.chat.id, text='Введите название криптовалюты:')     
        bot.register_next_step_handler(call.message, handler_message)

    elif call.data in all_currencies or call.data in favourite_coins:
        markup = types.InlineKeyboardMarkup(row_width=1)
        crypto_id = currencies_id[call.data]
        cryptocurrency = call.data
        price = get_price_id(crypto_id)
        chart_image = generate_price_chart(crypto_id, cryptocurrency)

        back_btn = types.InlineKeyboardButton('<-Назад', callback_data='get_back')
        fav_btn = types.InlineKeyboardButton("Добавить в избранное ★",
                                             callback_data=f'add_to_favourite_{cryptocurrency}')
        markup.add(back_btn, fav_btn)
        if chart_image:
            bot.send_photo(call.message.chat.id, chart_image, caption=f'1 {cryptocurrency} -> {round(price, 4)} USDT',
                           reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, f'1 {cryptocurrency} -> {round(price, 4)} USDT', reply_markup=markup)

    elif call.data.startswith('add_to_favourite_'):
        # username = call.from_user.username
        # cryptocurrency = call.data.split('_')[-1]
        # if cryptocurrency not in favourite_coins:
        #     favourite_coins.append(cryptocurrency)
        # add_to_favorites(username, cryptocurrency)
        cryptocurrency = call.data.split('_')[-1]
        if cryptocurrency not in favourite_coins:
            favourite_coins.append(cryptocurrency)

        bot.answer_callback_query(call.id, text=f"{cryptocurrency} добавлен в избранное!")

    elif call.data == 'get_back':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Избранные", callback_data='favorites')
        btn2 = types.InlineKeyboardButton("Все криптовалюты", callback_data='all_crypto')
        markup.add(btn1, btn2)
        bot.send_message(chat_id=call.message.chat.id, text="Выберите раздел:", reply_markup=markup)   
        

def get_data_crypto(text):
    data_url = f"https://openapiv1.coinstats.app/coins/{text}"
    response = requests.get(data_url, headers=headers).json()
    print(response)

def get_price_id(crypto_id):
    try:
        price_url = f"https://openapiv1.coinstats.app/coins/{crypto_id}"
        print(price_url)
        response = requests.get(price_url, headers=headers).json()

        return response['price']

    except Exception as e:
        print(f"{e}")
        return None

def generate_price_chart(crypto_id, cryptocurrency):
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=3)  # Последние 3 часа

        # Получение исторических данных за последние 3 часа
        historical_data = cryptocompare.get_historical_price_minute(
            cryptocurrency, currency='USD', limit=3*60, toTs=int(end_time.timestamp())
        )

        if not historical_data:
            print("Error fetching historical data.")
            return None

        # Подготовка данных для графика
        times = [datetime.fromtimestamp(data['time']) for data in historical_data]
        values = [data['close'] for data in historical_data]

        # Построение графика
        plt.figure(figsize=(10, 5))
        plt.plot(times, values, marker='o', linestyle='-', color='b')  # Линия с маркерами

        # Добавление аннотации с последней ценой
        last_time = times[-1]
        last_value = values[-1]
        plt.annotate(f'{last_value:.2f} USD', xy=(last_time, last_value), 
                     xytext=(last_time + timedelta(minutes=15), last_value),
                     arrowprops=dict(facecolor='black', arrowstyle='->'),
                     bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))

        plt.xlabel('Time')
        plt.ylabel('Price (USD)')
        plt.title(f'{cryptocurrency} Price (Last 3 Hours)')
        plt.grid(True)  # Включение сетки для лучшей читаемости
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Сохранение графика в поток байтов
        image_stream = io.BytesIO()
        plt.savefig(image_stream, format='png')
        plt.close()
        image_stream.seek(0)

        return image_stream

    except Exception as e:
        print(f"Error generating chart: {e}")
        return None


bot.infinity_polling()
