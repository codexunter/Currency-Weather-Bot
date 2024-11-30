import telebot
import requests
from telebot import types
from currency_converter import CurrencyConverter
bot=telebot.TeleBot('6341173336:AAEUdApdyQak5F6xeaUbE0RlD04rZOSeReU')
api='2b58d756e4e1f70b62a161ddac18c84a'
conversion=CurrencyConverter()
amount=0
def main_panel():
    menu=types.InlineKeyboardMarkup(row_width=2)
    weather=types.InlineKeyboardButton('Погода',callback_data='menu1:weather')
    rate=types.InlineKeyboardButton('Конвертация',callback_data='menu1:rate')
    menu.add(weather,rate)
    return menu
def sub_panel():
    menu=types.InlineKeyboardMarkup(row_width=2)
    btn1=types.InlineKeyboardButton('USD/THB',callback_data='menu2:usd/thb')
    btn2=types.InlineKeyboardButton('THB/USD',callback_data='menu2:thb/usd')
    btn3=types.InlineKeyboardButton('USD/CNY',callback_data='menu2:usd/cny')
    btn4=types.InlineKeyboardButton('CNY/USD',callback_data='menu2:cny/usd')
    btn5=types.InlineKeyboardButton('Свой вариант',callback_data='menu2:other')
    menu.add(btn1,btn2,btn3,btn4,btn5)
    return menu
@bot.message_handler(commands=['start'])
def start(message):
    menu=main_panel()
    bot.send_message(message.chat.id,f'<em>Здравствуйте <b>{message.from_user.first_name} {message.from_user.last_name}</b> 🙂\nВыберите опцию</em>',reply_markup=menu,parse_mode='html')
@bot.callback_query_handler(func=lambda call: call.data.split(':')[0]=='menu1')
def choice(call):
    if call.data.split(':')[1]=='weather':
        bot.send_message(call.message.chat.id,'<em>Напишите название города</em>',parse_mode='html')
        bot.register_next_step_handler(call.message,show)
    else:
        bot.send_message(call.message.chat.id,'<em>Напишите сумму</em>',parse_mode='html')
        bot.register_next_step_handler(call.message,summa)
def summa(message):
    global amount
    amount=message.text
    try:
        int(amount)
    except ValueError:
        bot.send_message(message.chat.id,'<em>Это не число. Напишите сумму</em>',parse_mode='html')
        bot.register_next_step_handler(message,summa)
        return
    if int(amount)<0:
        bot.send_message(message.chat.id,'<em>Это отрицательное число. Напишите сумму</em>',parse_mode='html')
        bot.register_next_step_handler(message,summa)
    else:
        menu=sub_panel()
        bot.send_message(message.chat.id,'<em>Выберите валютную пару</em>',reply_markup=menu,parse_mode='html')
@bot.callback_query_handler(func=lambda call: call.data.split(':')[0]=='menu2')
def see(call):
    if call.data.split(':')[1]!='other':
        data=call.data.split(':')[1]
        first=data.split('/')[0].upper()
        second=data.split('/')[1].upper()
        result=conversion.convert(amount,first,second)
        bot.send_message(call.message.chat.id,f'<b>{amount} {first} = {round(result,2)} {second}</b>',parse_mode='html')
        menu=main_panel()
        bot.send_message(call.message.chat.id,f'<em>Выберите опцию</em>',reply_markup=menu,parse_mode='html')
    else:
        bot.send_message(call.message.chat.id,'<em>Напишите свою пару валют через слеш</em>',parse_mode='html')
        bot.register_next_step_handler(call.message,pair)
def pair(message):
    try:
        result=conversion.convert(amount,message.text.split('/')[0].upper(),message.text.split('/')[1].upper())
    except Exception:
        menu=sub_panel()
        bot.send_message(message.chat.id,'<em>Такой валютной пары нет. Напишите другую</em>',reply_markup=menu,parse_mode='html')
        return
    first=message.text.split('/')[0].upper()
    second=message.text.split('/')[1].upper()
    bot.send_message(message.chat.id,f'<b>{amount} {first} = {round(result,2)} {second}</b>',parse_mode='html')
    menu=main_panel()
    bot.send_message(message.chat.id,f'<em>Выберите опцию</em>',reply_markup=menu,parse_mode='html')
def show(message):
    place=message.text.strip().lower()
    response=requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={place}&appid={api}&units=metric')
    if response.status_code==200:
        data=response.json()
        bot.send_message(message.chat.id,f'<b>Температура: {data["main"]["temp"]} (чувствуется как {data["main"]["feels_like"]}), влажность: {data["main"]["humidity"]}%</b>\n\n',parse_mode='html')
        menu=main_panel()
        bot.send_message(message.chat.id,'<em>Выберите опцию</em>',reply_markup=menu,parse_mode='html')
    else:
        bot.send_message(message.chat.id,'<em>Неудачный запрос🙁 Напишите другой город</em>',parse_mode='html')
        bot.register_next_step_handler(message,show)
        return
bot.polling(none_stop=True)
