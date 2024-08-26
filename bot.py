import cryptocompare
import telebot
from telebot import types
import requests
import threading
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io
from db import get_user_favorites, add_to_favorites, add_user_if_not_exists

API_TOKEN = '7215405334:AAF3eZ8ok-u_iJso6i-7K9t_Ni0tJ7SSrLY'
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
    username = message.chat.username

    add_user_if_not_exists(username)

    favourite_coins.extend(get_user_favorites(username))

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Избранные", callback_data='favorites')
    btn2 = types.InlineKeyboardButton("Все криптовалюты", callback_data='all_crypto')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Выберите раздел:", reply_markup=markup)


@bot.message_handler(commands=['stop'])
def stop(message):
    bot.is_running = False
    bot.send_message(message.chat.id, 'До скорой встречи!')
    bot.stop_polling()


def handler_message(message):
    text = message.text.lower()
    data_url = f"https://openapiv1.coinstats.app/coins/{text}"
    response = requests.get(data_url, headers=headers).json()

    cryptocurrency = response["symbol"]
    price = round(response["price"], 4)
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=3)  # Последние 3 часа    

    historical_data = cryptocompare.get_historical_price_minute(
        cryptocurrency, currency='USD', limit=3*60, toTs=int(end_time.timestamp())
    )

    if not historical_data:
        bot.send_message(message.chat.id, "Не удалось получить данные для этой криптовалюты.")
        return

    values = [data['close'] for data in historical_data]    
    last_value = values[-1]

    # Получаем данные за последние 30 минут
    start_30_min = end_time - timedelta(minutes=30)
    historical_data_30_min = cryptocompare.get_historical_price_minute(
        cryptocurrency, currency='USD', limit=30, toTs=int(end_time.timestamp())
    )

    start_value = historical_data_30_min[0]['close']
    percent_change = ((last_value - start_value) / start_value) * 100

    markup = types.InlineKeyboardMarkup(row_width=1)
    back_btn = types.InlineKeyboardButton('<-Назад', callback_data='get_back')
    fav_btn = types.InlineKeyboardButton("Добавить в избранное ★", callback_data=f'add_to_favourite_{cryptocurrency}')
    markup.add(back_btn, fav_btn)

    chart_image = generate_price_chart(cryptocurrency)

    if chart_image:
        if percent_change > 0:
            bot.send_photo(message.chat.id, chart_image, 
                       caption=f'1 {cryptocurrency} -> {round(last_value, 4)} USDT\nЗа 30 минут: 🠕{percent_change:.2f}%', 
                       reply_markup=markup)
        elif percent_change < 0:
            bot.send_photo(message.chat.id, chart_image, 
                       caption=f'1 {cryptocurrency} -> {round(last_value, 4)} USDT\nЗа 30 минут: 🠗{percent_change:.2f}%', 
                       reply_markup=markup)            
    else:
        if percent_change > 0:
            bot.send_message(message.chat.id,text=f'1 {cryptocurrency} -> {round(last_value, 4)} USDT\nЗа 30 минут: 🠕{percent_change:.2f}%', 
                            reply_markup=markup)
        elif percent_change < 0:
            bot.send_message(message.chat.id,text=f'1 {cryptocurrency} -> {round(last_value, 4)} USDT\nЗа 30 минут: 🠗{percent_change:.2f}%', 
                            reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    username = call.message.chat.username
    favourite_coins = []

    if call.data == 'favorites':
        favourite_coins = get_user_favorites(username)

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
        threading.Thread(target=handle_crypto_selection, args=(call,)).start()


    elif call.data.startswith('add_to_favourite_'):
        cryptocurrency = call.data.split('_')[-1]
        add_to_favorites(username, cryptocurrency)

        bot.answer_callback_query(call.id, text=f"{cryptocurrency} добавлен в избранное!")
    elif call.data == 'get_back':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Избранные", callback_data='favorites')
        btn2 = types.InlineKeyboardButton("Все криптовалюты", callback_data='all_crypto')
        markup.add(btn1, btn2)
        bot.send_message(chat_id=call.message.chat.id, text="Выберите раздел:", reply_markup=markup)


def handle_crypto_selection(call):
    cryptocurrency = call.data
    end_time = datetime.now()
    
    # Получаем данные за последние 3 часа
    historical_data = cryptocompare.get_historical_price_minute(
        cryptocurrency, currency='USD', limit=3*60, toTs=int(end_time.timestamp())
    )
    
    if not historical_data:
        bot.send_message(call.message.chat.id, "Не удалось получить данные для этой криптовалюты.")
        return

    # Последнее значение цены
    last_value = historical_data[-1]['close']

    # Получаем данные за последние 30 минут
    historical_data_30_min = cryptocompare.get_historical_price_minute(
        cryptocurrency, currency='USD', limit=30, toTs=int(end_time.timestamp())
    )
    
    if not historical_data_30_min:
        bot.send_message(call.message.chat.id, "Не удалось получить данные за последние 30 минут.")
        return

    # Цена 30 минут назад
    start_value = historical_data_30_min[0]['close']
    
    # Рассчитываем процентное изменение
    percent_change = ((last_value - start_value) / start_value) * 100

    # Генерация графика
    chart_image = generate_price_chart(cryptocurrency)
    
    # Создание разметки с кнопками
    markup = types.InlineKeyboardMarkup(row_width=1)
    back_btn = types.InlineKeyboardButton('<-Назад', callback_data='get_back')
    fav_btn = types.InlineKeyboardButton("Добавить в избранное ★", callback_data=f'add_to_favourite_{cryptocurrency}')
    markup.add(back_btn, fav_btn)
    
    # Отправка сообщения с графиком или текстом
    if percent_change > 0:
        caption = f'1 {cryptocurrency} -> {round(last_value, 4)} USDT\nЗа 30 минут: 🠕{percent_change:.2f}%'
    elif percent_change < 0:
        caption = f'1 {cryptocurrency} -> {round(last_value, 4)} USDT\nЗа 30 минут: 🠗{percent_change:.2f}%'

    if chart_image:
        bot.send_photo(call.message.chat.id, chart_image, caption=caption, reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, caption, reply_markup=markup)

def generate_price_chart(cryptocurrency):
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=3)  # Последние 3 часа

        historical_data = cryptocompare.get_historical_price_minute(
            cryptocurrency, currency='USD', limit=3*60, toTs=int(end_time.timestamp())
        )

        if not historical_data:
            print("Error fetching historical data.")
            return None

        times = [datetime.fromtimestamp(data['time']) for data in historical_data]
        values = [data['close'] for data in historical_data]

        plt.figure(figsize=(10, 5))
        plt.plot(times, values, marker='o', linestyle='-', color='b')

        last_time = times[-1]
        last_value = values[-1]
        plt.annotate(f'{last_value:.2f} USD', xy=(last_time, last_value), 
                     xytext=(last_time + timedelta(minutes=15), last_value),
                     arrowprops=dict(facecolor='black', arrowstyle='->'),
                     bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))

        plt.xlabel('Time')
        plt.ylabel('Price (USD)')
        plt.title(f'{cryptocurrency} Price (Last 3 Hours)')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()

        image_stream = io.BytesIO()
        plt.savefig(image_stream, format='png')
        plt.close()
        image_stream.seek(0)

        return image_stream

    except Exception as e:
        print(f"Error generating chart: {e}")
        return None


bot.infinity_polling()