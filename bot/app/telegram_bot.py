import telebot
import datetime
import psycopg2
from contextlib import closing
from config import TOKEN, PG_HOST, PG_NAME, PG_USER, PG_PASSWORD




bot = telebot.TeleBot(TOKEN)
UserRequests = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Облако слов', 'Topics')
    keyboard.row('ALERTS subscribtion', 'User subscribtions')
    bot.send_message(message.chat.id, 'Приветствую!', reply_markup=keyboard)

    #conn = psycopg2.connect(dbname="Users_for_reviews", user="postgres", password="admin", host='postgres')
    #cursor = conn.cursor()
    #cursor.execute('SELECT * FROM public."Users" LIMIT 10')
    #records = cursor.fetchall()
    #print(records)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Добрый день! Этот бот может помочь проанализировать отзывы на продукты.')


@bot.message_handler(content_types=['text'])
def send_text(message):
    chat_id = message.chat.id
    if message.text.lower() == 'облако слов' or message.text.lower() == 'alerts subscribtion' or\
                                                  message.text.lower() == 'topics':
        request_category = message.text
        UserRequests[chat_id] = {"id": chat_id, "request_category": request_category,
                                 "platform": None, "segment": None, "brand": None}
        platform_choosing(message)


@bot.message_handler(content_types = ['text'])
def platform_choosing(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Wildberries', callback_data='Wildberries'))
    markup.add(telebot.types.InlineKeyboardButton(text='Pet Shop', callback_data='Pet Shop'))
    markup.add(telebot.types.InlineKeyboardButton(text='Мир корма', callback_data='Мир корма'))
    bot.send_message(message.chat.id, text="Выберете платформу", reply_markup=markup)
    #bot.register_next_step_handler(message,segment_choosing)


def brand_choosing(message):
    brand = bot.send_message(message.chat.id, 'Введите бренд (например, Whiskas)')
    bot.register_next_step_handler(message, check_info)


def check_info(message):
    chat_id = message.chat.id
    brand = message.text
    try:
        UserRequests[chat_id]['brand'] = brand
        send_str = 'Ваш выбор: \nПлатформа - ' + UserRequests[chat_id]['platform'] +\
                    '\nСегмент - ' + UserRequests[chat_id]['segment'] +\
                    '\nБренд - '+ UserRequests[chat_id]['brand']
        bot.send_message(message.chat.id, send_str)
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text='Да', callback_data='Yes'))
        markup.add(telebot.types.InlineKeyboardButton(text='Нет', callback_data='No'))
        bot.send_message(message.chat.id, text='Все ли верно?', reply_markup=markup)
    except:
        bot.send_message(message.chat.id, 'Пожалуйста, начните с начала и выберите категорию из меню')


def database_insert(chat_id):
    now = datetime.datetime.now()
    print('INSERT INTO public."Users" VALUES ('+ str(chat_id)+
          ", '" + str(now)+ "', '" +str(UserRequests[chat_id]['platform'])+"', '" +
          str(UserRequests[chat_id]['segment'])+"', '" +str(UserRequests[chat_id]['brand'])+ "','" + str(False)+"', '" +
          str(UserRequests[chat_id]['request_category'])+"')")
    with closing(psycopg2.connect(dbname=PG_NAME, user=PG_USER, password=PG_PASSWORD, host=PG_HOST)) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO public.'Users' VALUES ("+ str(chat_id)+
                ", '" + str(now)+ "', '" +str(UserRequests[chat_id]['platform'])+"', '" +
                str(UserRequests[chat_id]['segment'])+"', '" +str(UserRequests[chat_id]['brand'])+ "','"
                + str(False)+"', '" +str(UserRequests[chat_id]['request_category'])+"');")



@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Кошки', callback_data='Cats'))
    markup.add(telebot.types.InlineKeyboardButton(text='Собаки', callback_data='Dogs'))
    
    #bot.answer_callback_query(callback_query_id=call.id, text='Спасибо за честный ответ!')
    answer = ''
    if call.data == 'Wildberries' or call.data == 'Pet Shop' or call.data == 'Мир корма':
        #global platform
        platform = call.data
        try:
            UserRequests[call.message.chat.id]['platform'] = platform
            answer = 'Супер!'
            bot.send_message(call.message.chat.id, text="Выберите сегмент", reply_markup=markup)
        except:
            bot.send_message(call.message.chat.id, 'Пожалуйста, начните с начала и выберите категорию из меню')
    elif call.data == 'Cats' or call.data == 'Dogs':
        #global segment
        segment = call.data
        try:
            UserRequests[call.message.chat.id]['segment'] = segment
            brand_choosing(call.message)
        except:
            bot.send_message(call.message.chat.id, 'Пожалуйста, начните с начала и выберите категорию из меню')
    elif call.data == 'Yes':
        bot.send_message(call.message.chat.id, "Отлично! Подождите немного пока расчитывается результат")
        markup = telebot.types.InlineKeyboardMarkup()
        database_insert(call.message.chat.id)
    elif call.data == 'No':
        bot.send_message(call.message.chat.id, "Нам очень жаль! Попробуйте еще раз")
        platform_choosing(call.message)


    #bot.send_message(call.message.chat.id, 'You chose '+ call.data)
    #bot.send_message(call.message.chat.id, answer)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


bot.polling()



