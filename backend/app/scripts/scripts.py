import mongoengine
from bs4 import BeautifulSoup
import aiohttp
import asyncio
from fake_useragent import UserAgent
import json
from app.models.WB import ProductWB, CommentWB


async def download_wildberries_comments(query: str):
    """
    Function that downloads comments and products from https://www.wildberries.ru by user query (e.g. Whiskas)
    :param query: Query to search
    :return: List of products which were found by this query
    """

    async with aiohttp.ClientSession() as session:
        products = []
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "user_agent": UserAgent()['google chrome']
        }

        url = (
            'https://search.wb.ru/exactmatch/ru/common/v3/search?appType=1&couponsGeo=12,3,18,15,21&curr=rub&dest=-1029256,-102269,-1278703,-1255563&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0&query='
            + str(query) +
            '&reg=0&regions=68,64,83,4,38,80,33,70,82,86,75,30,69,22,66,31,48,1,40,71&resultset=catalog&sort=popular&spp=0&stores=117673,122258,122259,125238,125239,125240,6159,507,3158,117501,120602,120762,6158,121709,124731,159402,2737,130744,117986,1733,686,132043'
        )

        async with session.get(url=url, headers=headers) as response_product:
            response_text_product = await response_product.text()
            json_obj_product = json.loads(response_text_product)
            if json_obj_product:
                for product in json_obj_product.get("catalog").get("data").get("products"):
                    url_imt = "https://wbx-content-v2.wbstatic.net/ru/" + str(product["id"]) + ".json"
                    async with session.get(url=url_imt, headers=headers) as response_imt:
                        response_text_imt = await response_imt.text()
                        json_obj_imt = json.loads(response_text_imt)
                    url_seller = (
                            "https://wbx-content-v2.wbstatic.net/sellers/" +
                            str(product["id"]) +
                            ".json"
                    )
                    async with session.get(url=url_seller, headers=headers) as response_seller:
                        response_text_seller = await response_seller.text()
                        if response_text_seller:
                            json_obj_seller = json.loads(response_text_seller)
                            seller_name = json_obj_seller.get("supplierName")
                        else:
                            seller_name = ''
                    if int(product["feedbacks"]) == 0:
                        continue
                    url = "https://public-feedbacks.wildberries.ru/api/v1/summary/full"
                    # Checking whether there is such product in DB or not
                    try:

                        found = ProductWB.objects(id_product=str(product["id"])).get()
                        print('IT WAS FOUND')
                    except mongoengine.DoesNotExist:
                        found = None
                    if found:
                        comments_amt_before = found.feedbacks_amt
                        comments_amt_after = int(product["feedbacks"])
                        index_to_download = range(int(int(comments_amt_after - comments_amt_before) / 30) + 1)
                    else:
                        comments_amt_before = 0
                        index_to_download = range(int(int(product["feedbacks"]) / 30) + 1)
                    for num_iter in index_to_download:
                        payload = {"imtId": int(json_obj_imt.get("imt_id")), "skip": 30 * num_iter + comments_amt_before,
                                   "take": 30}
                        async with session.post(
                                url=url, headers=headers, json=payload
                        ) as response:
                            response_text = await response.text()
                            if response_text:
                                json_obj = json.loads(response_text)
                                comments = []
                                for comment in json_obj.get("feedbacks"):
                                    if comment.get("votes"):
                                        pluses_amt = comment.get(
                                            "votes").get(
                                            "pluses"
                                        )
                                        minuses_amt = comment.get(
                                            "votes").get(
                                            "minuses"
                                        )
                                    else:
                                        pluses_amt = 0
                                        minuses_amt = 0

                                    comments.append(
                                        CommentWB(
                                            date=str(comment.get("createdDate")),
                                            author=str(comment.get(
                                                "wbUserDetails").get(
                                                "name"
                                            )),
                                            rating=comment.get('productValuation'),
                                            advantages=str(comment.get("pros")),
                                            disadvantages=str(comment.get("cons")),
                                            comment=str(comment.get("text")),
                                            pluses_amt=int(pluses_amt),
                                            minuses_amt=int(minuses_amt)
                                        )
                                    )

                    if found:
                        for comment in comments:
                            found.comments.append(comment)
                        found.feedbacks_amt = int(product["feedbacks"])
                        products.append(found)
                    else:
                        products.append(
                            ProductWB(
                                id_product=str(product["id"]),
                                imt_id=str(json_obj_imt.get("imt_id")),
                                name=str(json_obj_imt.get("imt_name")),
                                description=str(json_obj_imt.get("description")),
                                seller=seller_name,
                                category_name=str(product["name"]),
                                brand=str(product["brand"]),
                                price=int(product["salePriceU"]) / 100,
                                price_old=int(product["priceU"]) / 100,
                                url=(
                                    "https://www.wildberries.ru/catalog/"
                                    + str(product["id"])
                                    + "/detail.aspx?targetUrl=XS"
                                ),
                                rating=float(product["rating"]),
                                feedbacks_amt=int(product["feedbacks"]),
                                query=query,
                                comments=comments
                            )
                        )

        await asyncio.sleep(0.5)
    for product in products:
        product.save()
    return products


# async def download_wildberries_products(queries: list, connector):
#     # Массив для словарей
#     result = []
#     # print(queries)
#     product_dict = dict.fromkeys(
#         [
#             "id_product",
#             "category_name",
#             "brand",
#             "price",
#             "price_old",
#             "url",
#             "rating",
#             "feedbacks",
#             "query"
#         ]
#     )
#
#     async with aiohttp.ClientSession() as session:
#         headers = {
#             "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#             "user_agent": UserAgent()["google_chrome"]
#         }
#         for query in queries:
#
#             url = (
#                 'https://search.wb.ru/exactmatch/ru/common/v3/search?appType=1&couponsGeo=12,3,18,15,21&curr=rub&dest=-1029256,-102269,-1278703,-1255563&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0&query='
#                 + str(query) +
#                 '&reg=0&regions=68,64,83,4,38,80,33,70,82,86,75,30,69,22,66,31,48,1,40,71&resultset=catalog&sort=popular&spp=0&stores=117673,122258,122259,125238,125239,125240,6159,507,3158,117501,120602,120762,6158,121709,124731,159402,2737,130744,117986,1733,686,132043'
#             )
#
#             async with session.get(url=url, headers=headers) as response:
#                 response_text = await response.text()
#
#                 json_obj = json.loads(response_text)
#                 # print('-------------')
#                 # print(response_text)
#                 # print('-------------')
#                 if json_obj:
#                     for product in json_obj.get("catalog").get("data").get("products"):
#                         product_dict["query_str"] = query
#                         product_dict["id_product"] = product["id"]
#                         product_dict["category_name"] = product["name"]
#                         product_dict["brand"] = product["brand"]
#                         product_dict["price"] = str(int(product["salePriceU"]) / 100)
#                         # Не у всех товаров есть старая цена
#                         try:
#                             product_dict["price_old"] = str(int(product["priceU"]) / 100)
#                         except:
#                             pass
#                         product_dict["url"] = (
#                             "https://www.wildberries.ru/catalog/"
#                             + str(product["id"])
#                             + "/detail.aspx?targetUrl=XS"
#                         )
#                         product_dict["rating"] = product["rating"]
#                         product_dict["feedbacks"] = product["feedbacks"]
#                         # print(product_dict)
#                         # print("-------------------------")
#                         result.append(product_dict.copy())
#             await asyncio.sleep(0.5)
#         await connector['products'].insert_many(result)
#         for find in await connector.find():
#             print(find)
#     return True


# async def download_wildberries_imt_id(ids):
#     # Массив для словарей
#     result = []
#
#     product_dict = dict.fromkeys(
#         [
#             "id_product",
#             "imt_id",
#             "name",
#             "description",
#             "seller"
#         ]
#     )
#
#     async with aiohttp.ClientSession() as session:
#         headers = {
#             "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
#                       "image/avif,image/webp,image/apng,*/*;q=0.8,application"
#                       "/signed-exchange;v=b3;q=0.9",
#             "user_agent": UserAgent()["google_chrome"],
#             "cookie": "GA1.1.209467062.1650350987",
#         }
#         for id in ids:
#             url_imt = "https://wbx-content-v2.wbstatic.net/ru/" + str(id) + ".json"
#
#             async with session.get(url=url_imt, headers=headers) as response:
#                 response_text = await response.text()
#                 json_obj = json.loads(response_text)
#                 product_dict["id_product"] = str(id)
#                 product_dict["imt_id"] = json_obj.get("imt_id")
#                 product_dict["name"] = json_obj.get("imt_name")
#                 product_dict["description"] = json_obj.get("description")
#                 print(product_dict)
#                 result.append(product_dict.copy())
#             url_seller = (
#                 "https://wbx-content-v2.wbstatic.net/sellers/" + str(id) + ".json"
#             )
#             async with session.get(url=url_seller, headers=headers) as response:
#                 response_text = await response.text()
#                 json_obj = json.loads(response_text)
#                 product_dict["seller"] = json_obj.get("supplierName")
#             await asyncio.sleep(0.5)
#         # pd.DataFrame(result).to_csv("imt_wildberries.csv", index=False)


# async def download_wildberries_comments(imt_ids_feedbacks):
#     # Массив для словарей
#     result = []
#
#     comment_dict = dict.fromkeys(
#         [
#             "id_product",
#             "date",
#             "author",
#             "advantages",
#             "disadvantages",
#             "comment",
#             "pluses_amt",
#             "minuses_amt",
#         ]
#     )
#
#     async with aiohttp.ClientSession() as session:
#         headers = {
#             "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#             "user_agent": UserAgent()["google_chrome"],
#         }
#         for imt_id in imt_ids_feedbacks:
#             if imt_id[1] == 0:
#                 continue
#             url = "https://public-feedbacks.wildberries.ru/api/v1/summary/full"
#             for num_iter in range(int(imt_id[1] / 30) + 1):
#                 payload = {"imtId": int(imt_id[0]), "skip": 30 * num_iter, "take": 30}
#                 async with session.post(
#                     url=url, headers=headers, json=payload
#                 ) as response:
#                     response_text = await response.text()
#                     if response_text:
#                         json_obj = json.loads(response_text)
#
#                         for comment in json_obj.get("feedbacks"):
#                             comment_dict["id_product"] = comment.get("nmId")
#                             comment_dict["date"] = comment.get("createdDate")
#                             comment_dict["author"] = comment.get("wbUserDetails").get(
#                                 "name"
#                             )
#                             comment_dict["advantages"] = comment.get("pros")
#                             comment_dict["disadvantages"] = comment.get("cons")
#                             comment_dict["comment"] = comment.get("text")
#                             comment_dict["rating"] = comment.get("productValuation")
#                             if comment.get("votes"):
#                                 comment_dict["pluses_amt"] = comment.get("votes").get(
#                                     "pluses"
#                                 )
#                                 comment_dict["minuses_amt"] = comment.get("votes").get(
#                                     "minuses"
#                                 )
#                             else:
#                                 comment_dict["pluses_amt"] = 0
#                                 comment_dict["minuses_amt"] = 0
#
#                             print(comment_dict)
#                             print("-----------------")
#                             result.append(comment_dict.copy())
#
#             await asyncio.sleep(0.5)
            # pd.DataFrame(result).to_csv("comments_wildberries.csv", index=False)


# imt_df = pd.read_csv("imt_wildberries.csv")[["id_product", "imt_id"]]
# print(imt_df)
# product_df = pd.read_csv("products_wildberries.csv")[["id_product", "feedbacks"]]
# print(product_df)
# brand_list = [item[0] for item in pd.read_excel("brand_list.xlsx").values]
# id_product_list = product_df["id_product"].values
# imt_id_list = imt_df["imt_id"].values
#
# imt_feedbacks = imt_df.merge(product_df, on="id_product", how="left")[
#     ["imt_id", "feedbacks"]
# ].values
#
# # print(imt_feedbacks)
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# asyncio.run(download_wildberries_comments(imt_feedbacks))
