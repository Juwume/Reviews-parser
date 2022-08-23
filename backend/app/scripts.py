from bs4 import BeautifulSoup
import aiohttp
import asyncio
from fake_useragent import UserAgent
import json

# import pandas as pd


async def download_wildberries_products(queries: list, connector: object):
    # Массив для словарей
    result = []
    # print(queries)
    connector = connector['products']
    product_dict = dict.fromkeys(
        [
            "id_product",
            "category_name",
            "brand",
            "price",
            "price_old",
            "url",
            "rating",
            "feedbacks",
            "query"
        ]
    )

    async with aiohttp.ClientSession() as session:
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "user_agent": UserAgent()["google_chrome"]
        }
        for query in queries:

            url = (
                'https://search.wb.ru/exactmatch/ru/common/v3/search?appType=1&couponsGeo=12,3,18,15,21&curr=rub&dest=-1029256,-102269,-1278703,-1255563&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0&query='
                + str(query) +
                '&reg=0&regions=68,64,83,4,38,80,33,70,82,86,75,30,69,22,66,31,48,1,40,71&resultset=catalog&sort=popular&spp=0&stores=117673,122258,122259,125238,125239,125240,6159,507,3158,117501,120602,120762,6158,121709,124731,159402,2737,130744,117986,1733,686,132043'
            )

            async with session.get(url=url, headers=headers) as response:
                response_text = await response.text()

                json_obj = json.loads(response_text)
                # print('-------------')
                # print(response_text)
                # print('-------------')
                if json_obj:
                    for product in json_obj.get("catalog").get("data").get("products"):
                        product_dict["query"] = query
                        product_dict["id_product"] = product["id"]
                        product_dict["category_name"] = product["name"]
                        product_dict["brand"] = product["brand"]
                        product_dict["price"] = str(int(product["salePriceU"]) / 100)
                        # Не у всех товаров есть старая цена
                        try:
                            product_dict["price_old"] = str(int(product["priceU"]) / 100)
                        except:
                            pass
                        product_dict["url"] = (
                            "https://www.wildberries.ru/catalog/"
                            + str(product["id"])
                            + "/detail.aspx?targetUrl=XS"
                        )
                        product_dict["rating"] = product["rating"]
                        product_dict["feedbacks"] = product["feedbacks"]
                        # print(product_dict)
                        # print("-------------------------")
                        result.append(product_dict.copy())
            await asyncio.sleep(0.5)
        connector.insert_many(result)
        for find in connector.find():
            print(find)
    return True


async def download_wildberries_imt_id(ids):
    # Массив для словарей
    result = []

    product_dict = dict.fromkeys(
        [
            "id_product",
            "imt_id",
            "name",
            "description",
            "seller"
        ]
    )

    async with aiohttp.ClientSession() as session:
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                      "image/avif,image/webp,image/apng,*/*;q=0.8,application"
                      "/signed-exchange;v=b3;q=0.9",
            "user_agent": UserAgent()["google_chrome"],
            "cookie": "GA1.1.209467062.1650350987",
        }
        for id in ids:
            url_imt = "https://wbx-content-v2.wbstatic.net/ru/" + str(id) + ".json"

            async with session.get(url=url_imt, headers=headers) as response:
                response_text = await response.text()
                json_obj = json.loads(response_text)
                product_dict["id_product"] = str(id)
                product_dict["imt_id"] = json_obj.get("imt_id")
                product_dict["name"] = json_obj.get("imt_name")
                product_dict["description"] = json_obj.get("description")
                print(product_dict)
                result.append(product_dict.copy())
            url_seller = (
                "https://wbx-content-v2.wbstatic.net/sellers/" + str(id) + ".json"
            )
            async with session.get(url=url_seller, headers=headers) as response:
                response_text = await response.text()
                json_obj = json.loads(response_text)
                product_dict["seller"] = json_obj.get("supplierName")
            await asyncio.sleep(0.5)
        # pd.DataFrame(result).to_csv("imt_wildberries.csv", index=False)


async def download_wildberries_comments(imt_ids_feedbacks):
    # Массив для словарей
    result = []

    comment_dict = dict.fromkeys(
        [
            "id_product",
            "date",
            "author",
            "advantages",
            "disadvantages",
            "comment",
            "pluses",
            "minuses",
        ]
    )

    async with aiohttp.ClientSession() as session:
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "user_agent": UserAgent()["google_chrome"],
        }
        for imt_id in imt_ids_feedbacks:
            if imt_id[1] == 0:
                continue
            print(imt_id)
            url = "https://public-feedbacks.wildberries.ru/api/v1/summary/full"
            for num_iter in range(int(imt_id[1] / 30) + 1):
                payload = {"imtId": int(imt_id[0]), "skip": 30 * num_iter, "take": 30}
                print(payload)
                async with session.post(
                    url=url, headers=headers, json=payload
                ) as response:
                    response_text = await response.text()
                    if response_text:
                        json_obj = json.loads(response_text)

                        for comment in json_obj.get("feedbacks"):
                            comment_dict["id_product"] = comment.get("nmId")
                            comment_dict["date"] = comment.get("createdDate")
                            comment_dict["author"] = comment.get("wbUserDetails").get(
                                "name"
                            )
                            comment_dict["advantages"] = comment.get("pros")
                            comment_dict["disadvantages"] = comment.get("cons")
                            comment_dict["comment"] = comment.get("text")
                            comment_dict["rating"] = comment.get("productValuation")
                            if comment.get("votes"):
                                comment_dict["pluses"] = comment.get("votes").get(
                                    "pluses"
                                )
                                comment_dict["minuses"] = comment.get("votes").get(
                                    "minuses"
                                )
                            else:
                                comment_dict["pluses"] = 0
                                comment_dict["minuses"] = 0

                            print(comment_dict)
                            print("-----------------")
                            result.append(comment_dict.copy())

            await asyncio.sleep(0.5)
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
