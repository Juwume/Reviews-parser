# from bs4 import BeautifulSoup
# import aiohttp
# import asyncio
# from fake_useragent import UserAgent
# import json
#
#
#
# def ids_to_str(ids):
#     if type(ids) is list:
#         return ','.join([str(id) for id in ids])
#     else:
#         return str(ids)
#
#
# async def download_mirkorma_products(queries):
#     # Массив для словарей
#     result = []
#
#     product_dict = dict.fromkeys([
#         'id_product',
#         'name',
#         'brand',
#         'price',
#         'price_old',
#         'url',
#         'is_available',
#         'category_id',
#         'category_name'
#     ])
#
#     async with aiohttp.ClientSession() as session:
#         headers = {
#             'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#             'user_agent': UserAgent()['google_chrome'],
#             'cookie': 'GA1.1.209467062.1650350987'
#         }
#     for query in queries:
#         async with session.get(
#                 url='https://autocomplete.diginetica.net/autocomplete?st=' + str(
#                         query) + '&apiKey=78S47CE5V2&shuffle=true&strategy=vectors_extended,zero_queries&productsSize=24&regionId=global&forIs=true&showUnavailable=false&withContent=false&withSku=false',
#                 headers=headers) as response:
#             response_text = await response.text()
#         json_obj = json.loads(response_text)
#         for product in json_obj['products']:
#             product_dict['id_product'] = product['id']
#             product_dict['name'] = product['name']
#             product_dict['brand'] = product['brand']
#             product_dict['price'] = product['price']
#         # Не у всех товаров есть старая цена
#     try:
#         product_dict['price_old'] = product['oldPrice']
#         except:
#         pass
#         product_dict['url'] = 'https://www.mirkorma.ru/' + product['link_url']
#         product_dict['is_available'] = product['available']
#         product_dict['category_id'] = product['categories'][0]['id']
#         product_dict['category_name'] = product['categories'][0]['name']
#         print(product_dict)
#         result.append(product_dict.copy())
#     pd.DataFrame(result, index=False).to_csv('products_mirkorma.csv')
#
#
# async def download_mirkorma_comments(id_to_search: list):
#     # Словарь для хранения информации о товаре
#     comment_dict = dict.fromkeys([
#         'id_product',
#         'date',
#         'author',
#         'city',
#         'rating',
#         'advantages',
#         'disadvantages',
#         'comment',
#         'usage_frequency',
#         'usage_period'
#     ])
#     # Массив для словарей
#     result = []
#
#     async with aiohttp.ClientSession() as session:
#         headers = {
#             'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#             'user_agent': UserAgent()['google_chrome'],
#             'cookie': 'GA1.1.209467062.1650350987'
#         }
#     for i, id in enumerate(id_to_search):
#         print(id)
#         await asyncio.sleep(0.5)
#         # Иногда сохраняем текущий результат
#         if i % 200 == 0:
#             pd.DataFrame(result, index=False).to_csv('comments_mirkorma.csv')
#
#         async with session.get(
#                 url='https://w-api2.aplaut.io/widgets/DKryZdHkfYADZHxfKLFv/default/product/' + str(
#                         id) + '/product-reviews.html?hostname=mirkorma.ru&page=1',
#                 headers=headers) as response:
#             response_text = await response.text()
#         soup = BeautifulSoup(response_text, 'html.parser')
#         comments = soup.find_all('div', class_='sp-review sp-review-from-omnibox')
#         # try:
#         if comments:
#             for comment in comments:
#
#                 details = comment.find_all('span', class_='sp-review-author-detail')
#                 if details:
#                     if len(details) == 2:
#                         usage_frequency = details[0].text[
#                                           details[0].text.find(':') + 2:]
#                     usage_period = details[1].text[details[1].text.find(':') + 2:]
#                     elif details[0].text.find('частота использования'):
#                     usage_frequency = details[0].text[details[0].text.find(':') + 2:]
#                 else:
#                     usage_period = details[0].text[details[0].text.find(':') + 2:]
#
#             date = comment.find('div', class_='sp-review-date')['datetime']
#
#             advantages = comment.find('div',
#                                       class_='sp-review-pros-content sp-review-text-content')
#             if advantages:
#                 advantages = advantages.text
#
#         disadvantages = comment.find('div',
#                                      class_='sp-review-cons-content sp-review-text-content')
#         if disadvantages:
#             disadvantages = disadvantages.text
#
#         curr_comment = comment.find('div',
#                                     class_='sp-review-body-content sp-review-text-content')
#         if curr_comment:
#             curr_comment = curr_comment.text
#
#         rating = comment.find(itemprop="ratingValue").get("content")
#
#         author = comment.find('span', class_='sp-review-author-name')
#         if author:
#             author = author.text
#
#         city = comment.find('span', class_='sp-review-author-location')
#         if city:
#             city = city.text
#
#         # Запись в словарь и добавление этого словаря в массив результата
#         comment_dict['id_product'] = id
#         comment_dict['date'] = date
#         comment_dict['author'] = author
#         comment_dict['city'] = city
#         comment_dict['rating'] = rating
#         comment_dict['advantages'] = advantages
#         comment_dict['disadvantages'] = disadvantages
#         comment_dict['comment'] = curr_comment
#         comment_dict['usage_frequency'] = usage_frequency
#         comment_dict['usage_period'] = usage_period
#         result.append(comment_dict.copy())
#
#
# pd.DataFrame(result, index=False).to_csv('comments_mirkorma.csv')
#
# brand_list = [item[0] for item in pd.read_excel('brand_list.xlsx').values]
# id_product_list = pd.read_csv('products_mirkorma.csv')['id_product'].values
# print(len(id_product_list))
# print(id_product_list)
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# asyncio.run(download_mirkorma_comments(id_product_list))
