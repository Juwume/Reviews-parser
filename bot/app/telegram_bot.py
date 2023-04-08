import telebot
import datetime
import psycopg2
from contextlib import closing
from config import TOKEN, PG_HOST, PG_NAME, PG_USER, PG_PASSWORD


bot = telebot.TeleBot(TOKEN)

platform = ''
brend = ''
segment = ''
request_category = ''
chat_id = 0


@bot.message_handler(commands=['start'])
def start_message(message):
    global chat_id
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Words Cloud', 'Topics')
    keyboard.row('ALERTS subscribtion', 'User subscribtions')
    bot.send_message(message.chat.id, 'Hello!', reply_markup=keyboard)
    chat_id = message.chat.id

    cursor.execute('SELECT * FROM public."Users" LIMIT 10')
    records = cursor.fetchall()
    print(records)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Hi! This bot can help you to analyse reviews about products.')


@bot.message_handler(content_types=['text'])
def send_text(message):
    global request_category
    global chat_id
    chat_id = message.chat.id
    if message.text.lower() == 'user subscribtions':
        bot.send_message(message.chat.id, 'You are subscribed to:')
    elif message.text.lower() == 'words cloud' or message.text.lower() == 'alerts subscribtion' or\
    message.text.lower() == 'topics':
        request_category = message.text
        platform_choosing(message)


@bot.message_handler(content_types = ['text'])
def platform_choosing(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Wildberries', callback_data='Wildberries'))
    markup.add(telebot.types.InlineKeyboardButton(text='Yandex Market', callback_data='Yandex Market'))
    bot.send_message(message.chat.id, text="Please choose platform", reply_markup=markup)
    #bot.register_next_step_handler(message,segment_choosing)


def brend_choosing(message):
    global brend
    brend = bot.send_message(message.chat.id, 'Please enter brand (for example, Whiskas)')
    bot.register_next_step_handler(message, check_info)   


def check_info(message):
    global segment, brend, platform
    brend = message.text
    send_str = 'Your choice: \nPlatform - ' + platform +'\nSegment - ' + segment +'\nBrand - '+ brend
    bot.send_message(message.chat.id, send_str)
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Yes', callback_data='Yes'))
    markup.add(telebot.types.InlineKeyboardButton(text='No', callback_data='No'))
    bot.send_message(message.chat.id, text='Is it right?', reply_markup=markup)


def database_insert(subscribe):
    now = datetime.datetime.now()
    print('INSERT INTO public."Users" VALUES ('+ str(chat_id)+ ", '" + str(now)+ "', '" +str(platform)+"', '" +str(segment)+"', '" +str(brend)+ "','" + str(subscribe)+"', '" + str(request_category)+"')")
    with closing(psycopg2.connect(dbname=PG_NAME, user=PG_USER, password=PG_PASSWORD, host=PG_HOST)) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO public."Users" VALUES ('+ str(chat_id)+ ", '" + str(now)+ "', '" +str(platform)+"', '" +str(segment)+"', '" +str(brend)+ "','" + str(subscribe)+"', '" + str(request_category)+"')")


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Cats', callback_data='Cats'))
    markup.add(telebot.types.InlineKeyboardButton(text='Dogs', callback_data='Dogs'))
    
    #bot.answer_callback_query(callback_query_id=call.id, text='Спасибо за честный ответ!')
    answer = ''
    if call.data == 'Wildberries' or call.data == 'Yandex Market':
        global platform
        platform = call.data
        answer = 'Super!'
        bot.send_message(call.message.chat.id, text="Please choose segment", reply_markup=markup)
    elif call.data == 'Cats' or call.data == 'Dogs':
        global segment
        segment = call.data
        brend_choosing(call.message)
    elif call.data == 'Yes':
        bot.send_message(call.message.chat.id, "Great! Wait a little bit to get the result")
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text='Yes', callback_data='Yes_subscribtion'))
        markup.add(telebot.types.InlineKeyboardButton(text='No, not now', callback_data='No_subscribtion'))
        bot.send_message(call.message.chat.id, text="Do you want to subscribe to updates?", reply_markup=markup)
    elif call.data == 'No':
        bot.send_message(call.message.chat.id, "It's a pity! You can try it again")
        platform_choosing(call.message)
    elif call.data == 'Yes_subscribtion':
        bot.send_message(call.message.chat.id, "Great!")
        subscribe = 'TRUE'
        database_insert(subscribe)
    elif call.data == 'No_subscribtion':
        subscribe = 'FALSE'
        database_insert(subscribe)

    #bot.send_message(call.message.chat.id, 'You chose '+ call.data)
    #bot.send_message(call.message.chat.id, answer)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


bot.polling()



