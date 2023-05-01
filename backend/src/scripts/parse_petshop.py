from bs4 import BeautifulSoup
import mongoengine
import aiohttp
import asyncio
from fake_useragent import UserAgent
import json
from src.models.petshop import ProductPetshop, CommentPetshop
from copy import deepcopy
from src.utils import check_proxy


def ids_to_str(ids):
    if type(ids) is list:
        return ",".join([str(id) for id in ids])
    else:
        return str(ids)


async def download_petshop_products(query):
    # Список задач (страницы товаров)
    tasks = []
    # Массив для продуктов
    products = []
    # Список прокси для запросов
    proxy_list = [
        "http://85.26.146.169",
        "http://203.30.189.221:80",
        "http://203.30.188.42:80",
        "http://95.174.98.125:80",
        "http://45.8.211.90:80"
    ]

    # Открытие сессии
    async with aiohttp.ClientSession() as session:
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "user_agent": UserAgent()["google_chrome"],
            "cookie": "GA1.1.209467062.1650350987",
        }
        for proxy_url in proxy_list:
            proxy = await check_proxy(proxy_url, session, headers)
            if proxy:
                break
        print(proxy)
        # Получение страницы с товарами по нашему запросу
        async with session.get(
            url="https://www.petshop.ru/search/?q=" + query + "#ps=100",
            headers=headers,
            proxy=proxy,
        ) as response:
            response_text = await response.text()

            soup = BeautifulSoup(response_text, "html.parser")
            # Поиск всех товаров на странице
            pages = soup.find_all("a", class_="j_product-link image")

            for note in pages:
                # Добавление всех товаров с список задач
                tasks.append(note["href"])
        # Cтрока с куском кода где лежит информация о продукте
        string_to_find = '$(window).trigger("onProductView", '

        for task in tasks:
            print("im on " + task)
            url_to_visit = "https://www.petshop.ru" + task
            async with session.get(
                url=url_to_visit, headers=headers, proxy=proxy
            ) as response_product:
                response_text = await response_product.text()
                response_text = response_text[
                    response_text.find(string_to_find) + len(string_to_find) :
                ]
                response_text = response_text[: response_text.find(");")]
                json_obj_product = json.loads(response_text)
                if not json_obj_product:
                    continue
                # Проверка на наличие в базе
                try:
                    found = ProductPetshop.objects(
                        id_product=str(json_obj_product["product"]["id"])
                    ).get()
                    print("IT WAS FOUND")
                except mongoengine.DoesNotExist:
                    found = None
                # Получение комментариев
                async with session.get(
                    url="https://www.petshop.ru/api/v2/site/product/"
                    + str(json_obj_product["product"]["id"])
                    + "/reviews/?offset=0&limit=200",
                    headers=headers,
                    proxy=proxy
                ) as response_comments:
                    comments = []
                    response_text = await response_comments.text()
                    try:
                        json_obj_comment = json.loads(response_text)
                        if "message" in json_obj_comment:
                            continue
                        elif "comments" in json_obj_comment:
                            for comment in json_obj_comment["comments"]:
                                comment.pop("adminFeature", None)
                                comments.append(
                                    CommentPetshop(
                                        id_comment=str(comment["id"]),
                                        date=str(comment["date"]),
                                        author=str(comment["author"]),
                                        city=str(comment["city"]),
                                        advantages=str(comment["advantages"]),
                                        disadvantages=str(comment["disadvantages"]),
                                        comment=str(comment["comment"]),
                                        rating=float(comment["rating"]),
                                    )
                                )
                    except:
                        pass
                    if found:
                        found.id_product = str(json_obj_product["product"]["id"])
                        found.id_similar_products = ids_to_str(
                            json_obj_product["product"]["ids"]
                        )
                        found.name = str(json_obj_product["product"]["name"])
                        found.brand = str(json_obj_product["product"]["brand"])
                        found.price = json_obj_product["product"]["price"]
                        found.price_old = json_obj_product["product"]["price_old"]
                        found.url = json_obj_product["product"]["url"]
                        found.price_regional = json_obj_product["product"][
                            "price_regional"
                        ]
                        found.description = str(
                            json_obj_product["product"]["description"]
                        )
                        found.is_available = json_obj_product["product"]["isAvailable"]
                        found.category_id = str(json_obj_product["category"]["id"])
                        found.category_name = str(json_obj_product["category"]["name"])
                        found.comments = deepcopy(comments)
                        products.append(found)
                    else:
                        products.append(
                            ProductPetshop(
                                id_product=str(json_obj_product["product"]["id"]),
                                id_similar_products=ids_to_str(
                                    json_obj_product["product"]["ids"]
                                ),
                                name=str(json_obj_product["product"]["name"]),
                                brand=str(json_obj_product["product"]["brand"]),
                                price=json_obj_product["product"]["price"],
                                price_old=json_obj_product["product"]["price_old"],
                                url=json_obj_product["product"]["url"],
                                price_regional=json_obj_product["product"][
                                    "price_regional"
                                ],
                                description=str(
                                    json_obj_product["product"]["description"]
                                ),
                                is_available=json_obj_product["product"]["isAvailable"],
                                category_id=str(json_obj_product["category"]["id"]),
                                category_name=str(json_obj_product["category"]["name"]),
                                comments=comments,
                            )
                        )
    for product in products:
        product.save()
    return products


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