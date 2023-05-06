import telebot
import datetime
import psycopg2
from contextlib import closing
from config import TOKEN, PG_HOST, PG_NAME, PG_USER, PG_PASSWORD
from datetime import datetime as dtm
import requests



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
                                 "platform": None, "start_date": None,"end_date": None, "brand": None}
        platform_choosing(message)


@bot.message_handler(content_types = ['text'])
def platform_choosing(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Wildberries', callback_data='Wildberries'))
    markup.add(telebot.types.InlineKeyboardButton(text='Pet Shop', callback_data='Pet Shop'))
    markup.add(telebot.types.InlineKeyboardButton(text='Мир корма', callback_data='Мир корма'))
    bot.send_message(message.chat.id, text="Выберете платформу", reply_markup=markup)


def check_date(date):
    date_format = "%Y-%m-%d"
    try:
        res = bool(dtm.strptime(date, date_format))
    except ValueError:
        res = False
    return res


def dates_interval_choosing(message):
    start_date = bot.send_message(message.chat.id, "Введите начальную дату в формате '2023-01-20'")
    bot.register_next_step_handler(message, start_date_check)


def start_date_check(message):
    start_date = message.text
    res = check_date(start_date)
    if res:
        dates_end_choosing(message, start_date)
    else:
        error = bot.send_message(message.chat.id, "Неверный формат")
        dates_interval_choosing(message)


def dates_end_choosing(message, start_date):
    end_date = bot.send_message(message.chat.id, "Введите конечную дату в формате '2023-01-20'")
    bot.register_next_step_handler(message, dates_prepare,start_date)


def dates_prepare(message, start_date):
    end_date = message.text
    res = check_date(end_date)
    if res:
        if start_date <= end_date:
            dates_interval_set(message, start_date, end_date)
        else:
            error = bot.send_message(message.chat.id, "Дата начала больше конечной даты, попробуйте заново. " +
                                    "Например, допустимый промежуток - от 2023-01-01 до 2023-01-05.")
            dates_end_choosing(message, start_date)
    else:
        error = bot.send_message(message.chat.id, "Неверный формат")
        dates_end_choosing(message, start_date)




def dates_interval_set(message, start_date, end_date):
    try:
        UserRequests[message.chat.id]['start_date'] = start_date
        UserRequests[message.chat.id]['end_date'] = end_date
        brand_choosing(message)
    except:
        bot.send_message(message.chat.id, 'Пожалуйста, начните с начала и выберите категорию из меню')


def brand_choosing(message):
    brand = bot.send_message(message.chat.id, 'Введите бренд (например, Whiskas)')
    bot.register_next_step_handler(message, check_info)


def check_info(message):
    chat_id = message.chat.id
    brand = message.text
    try:
        UserRequests[chat_id]['brand'] = brand
        send_str = 'Ваш выбор: \nПлатформа - ' + UserRequests[chat_id]['platform'] +\
                    '\nДата начала - ' + UserRequests[chat_id]['start_date'] + \
                   '\nДата конца - ' + UserRequests[chat_id]['end_date'] + \
                   '\nБренд - '+ UserRequests[chat_id]['brand']
        bot.send_message(message.chat.id, send_str)
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text='Да', callback_data='Yes'))
        markup.add(telebot.types.InlineKeyboardButton(text='Нет', callback_data='No'))
        bot.send_message(message.chat.id, text='Все ли верно?', reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, 'Пожалуйста, начните с начала и выберите категорию из меню')


def database_insert(chat_id):
    now = datetime.datetime.now()
    with closing(psycopg2.connect(dbname=PG_NAME, user=PG_USER, password=PG_PASSWORD, host=PG_HOST)) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO public."Users" VALUES ('+ str(chat_id)+
                ", '" + str(now)+ "', '" +str(UserRequests[chat_id]['platform'])+"', '" +
                str(UserRequests[chat_id]['start_date'])+"', '" +
                str(UserRequests[chat_id]['end_date'])+"', '" +str(UserRequests[chat_id]['brand'])+ "','"
                +str(UserRequests[chat_id]['request_category'])+"');")
    get_comments(chat_id)

def get_comments(chat_id):
    r = requests.get('http://backend-flask:5000/api/petshop/whiskas', timeout=100)
    print(r.json)


def get_standart_date_interval(weeks_num):
    now = datetime.datetime.now()
    start_date = str(now.date() - datetime.timedelta(weeks=weeks_num))
    end_date = str(now.date())
    return start_date, end_date



@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Последняя неделя', callback_data='last_week'))
    markup.add(telebot.types.InlineKeyboardButton(text='Последний месяц', callback_data='last_month'))
    markup.add(telebot.types.InlineKeyboardButton(text='Последний год', callback_data='last_year'))
    markup.add(telebot.types.InlineKeyboardButton(text='Свой вариант', callback_data='other_interval'))
    
    #bot.answer_callback_query(callback_query_id=call.id, text='Спасибо за честный ответ!')
    answer = ''
    if call.data == 'Wildberries' or call.data == 'Pet Shop' or call.data == 'Мир корма':
        platform = call.data
        try:
            UserRequests[call.message.chat.id]['platform'] = platform
            answer = 'Супер!'
            bot.send_message(call.message.chat.id, text="Выберите сегмент", reply_markup=markup)
        except:
            bot.send_message(call.message.chat.id, 'Пожалуйста, начните с начала и выберите категорию из меню')


    elif call.data == 'last_week':
        start_date,end_date = get_standart_date_interval(1)
        dates_interval_set(call.message, start_date, end_date)
    elif call.data == 'last_month':
        start_date, end_date = get_standart_date_interval(4)
        dates_interval_set(call.message, start_date, end_date)
    elif call.data == 'last_year':
        start_date, end_date = get_standart_date_interval(52)
        dates_interval_set(call.message, start_date, end_date)
    elif call.data == 'other_interval':
        dates_interval_choosing(call.message)



    elif call.data == 'Yes':
        bot.send_message(call.message.chat.id, "Отлично! Подождите немного пока расчитывается результат")
        markup = telebot.types.InlineKeyboardMarkup()
        database_insert(call.message.chat.id)

    elif call.data == 'No':
        bot.send_message(call.message.chat.id, "Нам очень жаль! Попробуйте еще раз")
        platform_choosing(call.message)


    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


bot.polling()



