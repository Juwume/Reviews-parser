# from bs4 import BeautifulSoup
# import aiohttp
# import asyncio
# from fake_useragent import UserAgent
# import json
# import pandas as pd
#
#
# def ids_to_str(ids):
#     if type(ids) is list:
#         return ','.join([str(id) for id in ids])
#     else:
#         return str(ids)
#
#
# async def download_petshop_products(queries: list) -> list:
#     # Список задач (страницы товаров)
#     tasks = []
#
#     # Словарь для хранения информации о товаре
#     product_dict = dict.fromkeys([
#         'id_product',
#         'id_similar_products',
#         'name',
#         'brand',
#         'price',
#         'price_old',
#         'url',
#         'price_regional',
#         'description',
#         'is_available',
#         'category_id',
#         'category_name'
#     ])
#
#     # Массив для словарей
#     result = []
#
#     # Открытие сессии
#     async with aiohttp.ClientSession() as session:
#         headers = {
#             'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#             'user_agent': UserAgent()['google_chrome'],
#             'cookie': 'GA1.1.209467062.1650350987'
#         }
#         for query in queries:
#             # Получение страницы с товарами по нашему запросу
#             async with session.get(
#                     url='https://www.petshop.ru/search/?q=' + query + '#ps=100',
#                     headers=headers) as response:
#                 response_text = await response.text()
#
#                 soup = BeautifulSoup(response_text, 'html.parser')
#                 # Поиск всех товаров на странице
#                 pages = soup.find_all('a', class_='j_product-link image')
#
#                 for note in pages:
#                     print(note['href'])
#                     print('---------------------')
#                     # Добавление всех товаров с список задач
#                     tasks.append(note['href'])
#             # Cтрока с куском кода где лежит информация о продукте
#             string_to_find = '$(window).trigger("onProductView", '
#
#             for task in tasks:
#                 print('im on ' + task)
#                 url_to_visit = 'https://www.petshop.ru' + task
#                 async with session.get(url=url_to_visit, headers=headers) as response:
#                     response_text = await response.text()
#                     response_text = response_text[
#                                     response_text.find(string_to_find) + len(
#                                         string_to_find):]
#                     response_text = response_text[:response_text.find(');')]
#                     json_obj = json.loads(response_text)
#
#                     product_dict['id_product'] = json_obj['product']['id']
#                     product_dict['id_similar_products'] = ids_to_str(
#                         json_obj['product']['ids'])
#                     product_dict['name'] = json_obj['product']['name']
#                     product_dict['brand'] = json_obj['product']['brand']
#                     product_dict['price'] = json_obj['product']['price']
#                     product_dict['price_old'] = json_obj['product']['price_old']
#                     product_dict['url'] = json_obj['product']['url']
#                     product_dict['price_regional'] = json_obj['product'][
#                         'price_regional']
#                     product_dict['description'] = json_obj['product']['description']
#                     product_dict['is_available'] = json_obj['product']['isAvailable']
#                     product_dict['category_id'] = json_obj['category']['id']
#                     product_dict['category_name'] = json_obj['category']['name']
#                     # print(product_dict)
#                     result.append(product_dict.copy())
#             tasks = []
#             pd.DataFrame(result, index=False).to_csv('products_petshop.csv')
#
#
# async def download_petshop_comments():
#     # Датафрейм в который складываем результат для выгрузки
#     comment_df = pd.DataFrame(columns=
#     [
#         'id_product',
#         'date',
#         'author',
#         'avatar',
#         'city',
#         'rating',
#         'capture',
#         'advantages',
#         'disadvantages',
#         'comment',
#     ]
#     )
#
#     # Открытие сессии
#     async with aiohttp.ClientSession() as session:
#         headers = {
#             'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#             'user_agent': UserAgent()['google_chrome'],
#             'cookie': 'GA1.1.209467062.1650350987'
#         }
#
#         # По каждому товару ищется его комментарий
#         # Добавить чтобы поиск был по id_product из product_df
#         for id in range(7100, 7600):
#             print(id)
#             # Иногда сохраняем текущий результат
#             if id % 200 == 0:
#                 comment_df.to_csv('result_of_parsing_petshop_api_from_7100.csv')
#
#             # Запрос комментария
#             async with session.get(
#                     url='https://www.petshop.ru/api/v2/site/product/' + str(
#                             id) + '/reviews/?offset=0&limit=200',
#                     headers=headers) as response:
#                 response_text = await response.text()
#                 try:
#                     json_obj = json.loads(response_text)
#                     if 'message' in json_obj:
#                         continue
#                     elif 'comments' in json_obj:
#                         for comment in json_obj['comments']:
#                             comment.pop('adminFeature', None)
#                             comment['id_product'] = str(id)
#                             # print(comment)
#                             # print(pd.DataFrame(comment))
#                             comment_df = comment_df.append(comment, ignore_index=True)
#                 except:
#                     pass
#         print(result_data)
#         result_data.to_csv('result_of_parsing_petshop_api_from_7100.csv')
#
#
# brand_list = [item[0] for item in pd.read_excel('brand_list.xlsx').values]
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# asyncio.run(get_product_info(brand_list))
#
