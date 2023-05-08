
import re
import pandas as pd
import random
import numpy as np
from PIL import Image
from wordcloud import WordCloud
import pymorphy2




def get_words_cloud_picture(chat_id, bot,  dict_comments, brand):
	joined_lemmatization = preprocessing_comments(dict_comments)
	data = pd.DataFrame([joined_lemmatization], columns=['text_cleaned'])
	data['brand'] = str(brand)

	img_names_cat = ['cat_sit', 'cat_stratch', 'cat_walk']
	img_name = print_word_cloud(data, img_name=img_names_cat[random.randint(0, len(img_names_cat) - 1)],
					 brand=str(brand),
					 background_color="white", contour_color='purple', contour_width=4, max_words=1000)
	bot.send_message(chat_id, 'Полученное облако слов')
	with open(img_name, "rb") as img:
		bot.send_photo(chat_id, img)





def preprocessing_comments(dict_comments):
	coments_good = ''
	for row in dict_comments:
		for com in row['comments']:
			coments_good += (com['comment'] + " ")
	# выполнеяем препроцессинг - приводим к нижнему регистру и убираем лишние символы
	processed_text = coments_good.lower()
	processed_text = re.sub('[^a-zA-Zа-яА-Я1-9]', ' ', processed_text)
	processed_text = re.sub(r'\s+', ' ', processed_text)
	# получаем стоп слова из файла
	stop_words = get_stop_words()
	split_text = processed_text.split(" ")
	# фильтруем стоп слова
	filtered_tokens = []
	for word in split_text:
		if word not in stop_words and word != '':
			filtered_tokens.append(word)
	# производим лемматизацию - приведение слова к начальной форме
	morph = pymorphy2.MorphAnalyzer()
	data_lemmatization = []
	for word in filtered_tokens:
		data_lemmatization.append(morph.parse(word)[0].normal_form)
	return  ' '.join(data_lemmatization)





def get_stop_words():
	with open("./materials/stop_words.txt", "r", encoding="utf-8") as f:
		stop_w = f.readlines()
	return stop_w[0].split(" ")





def transform_image_mask(img_name='cat_sit'):
	mask = np.array(Image.open('./materials/' + img_name + '.png'))
	initial_font_number = mask[0][0][0]
	transformed = np.ndarray((mask.shape[0], mask.shape[1]), np.int32)

	for x in range(len(mask)):
		transformed[x] = [255 - i + initial_font_number for i in mask[x].T[1]]

	return transformed


def print_word_cloud(dataframe, img_name='cat_sit', brand='Whiskas',
					 background_color="white", contour_color='purple', contour_width=2, max_words=1000):
	mask  = transform_image_mask(img_name)

	wc = WordCloud(background_color=background_color, max_words=max_words, mask=mask,
				   contour_width=contour_width, contour_color=contour_color)
	text = dataframe.loc[(dataframe.brand == brand), 'text_cleaned'].values[0]
	wc.generate(text)

	file_name = brand + '_wordcloud' + '.png'
	wc.to_file('./materials/' + file_name)
	return  ('./materials/' + file_name)

