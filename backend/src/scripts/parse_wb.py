import mongoengine
import aiohttp
from fake_useragent import UserAgent
import json
from datetime import datetime
from src.models.wb import ProductWB, CommentWB
from src.classifier.catboost_classifier import read_model, inference
from src.utils import check_proxy
from src.config import PROXY_LOGIN, PROXY_PASS, PROXY_ADDR

async def download_wildberries_comments(query: str):
    """
    Function that downloads comments and products from https://www.wildberries.ru by user query (e.g. Whiskas)
    :param query: Query to search
    :return: List of products which were found by this query
    """
    # Reading model
    model, stop_words, vectorizer, transformer = read_model()
    # Список прокси для запросов
    if PROXY_LOGIN and PROXY_PASS:
        proxy_auth = aiohttp.BasicAuth(PROXY_LOGIN, PROXY_PASS)
    else:
        proxy_auth = None
    proxy_list = [PROXY_ADDR]
    # Create session
    async with aiohttp.ClientSession() as session:
        products = []
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "user_agent": UserAgent()["google chrome"],
        }
        # Check if proxy works
        for proxy_url in proxy_list:
            proxy = await check_proxy(proxy_url, session, headers, proxy_auth)
            if proxy:
                break
        print(proxy)
        # URL to parse products
        url = (
            "https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=12,3,18,15,21&curr=rub&dest=-1029256,-102269,-1278703,-1255563&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0&query="
            + str(query)
            + "&reg=0&regions=68,64,83,4,38,80,33,70,82,86,75,30,69,22,66,31,48,1,40,71&resultset=catalog&sort=popular&spp=0&stores=117673,122258,122259,125238,125239,125240,6159,507,3158,117501,120602,120762,6158,121709,124731,159402,2737,130744,117986,1733,686,132043"
        )
        # Products query
        async with session.get(url=url, headers=headers) as response_product:
            response_text_product = await response_product.text()
            json_obj_product = json.loads(response_text_product)
            if json_obj_product:
                for product in json_obj_product.get("data").get("products"):
                    url_imt = (
                        "https://wbx-content-v2.wbstatic.net/ru/"
                        + str(product["id"])
                        + ".json"
                    )
                    print("im on " + url_imt)
                    async with session.get(
                        url=url_imt, headers=headers
                    ) as response_imt:
                        response_text_imt = await response_imt.text()
                        json_obj_imt = json.loads(response_text_imt)
                    url_seller = (
                        "https://wbx-content-v2.wbstatic.net/sellers/"
                        + str(product["id"])
                        + ".json"
                    )
                    async with session.get(
                        url=url_seller, headers=headers
                    ) as response_seller:
                        response_text_seller = await response_seller.text()
                        if response_text_seller:
                            json_obj_seller = json.loads(response_text_seller)
                            seller_name = json_obj_seller.get("supplierName")
                        else:
                            seller_name = ""
                    if int(product["feedbacks"]) == 0:
                        continue
                    product_root = str(product.get("root"))
                    # Checking whether there is such product in DB or not
                    try:
                        found = ProductWB.objects(id_product=str(product["id"])).get()
                        print("IT WAS FOUND")
                    except mongoengine.DoesNotExist:
                        found = None
                    comments_amt_after = int(product["feedbacks"])
                    if found:
                        comments_amt_before = found.comments_amt
                    else:
                        comments_amt_before = 0
                    comments = []
                    url_comments = (
                        "https://feedbacks1.wb.ru/feedbacks/v1/" + product_root
                    )
                    url_comments_second_mirror = (
                        "https://feedbacks2.wb.ru/feedbacks/v1/" + product_root
                    )
                    async with session.get(
                        url=url_comments, headers=headers
                    ) as response:
                        response_text = await response.text()
                        feedbacks = json.loads(response_text).get("feedbacks")
                        if not feedbacks:
                            # if no comments => search second mirror
                            async with session.get(
                                url=url_comments_second_mirror, headers=headers
                            ) as response_second_mirror:
                                response_text = await response_second_mirror.text()
                                feedbacks = json.loads(response_text).get("feedbacks")
                                if not feedbacks:
                                    feedbacks = []
                        print(str(len(feedbacks)))
                        if len(feedbacks) > 0:
                            for comment in feedbacks[
                                comments_amt_before:comments_amt_after
                            ]:
                                if comment.get("votes"):
                                    pluses_amt = comment.get("votes").get("pluses")
                                    minuses_amt = comment.get("votes").get("minuses")
                                else:
                                    pluses_amt = 0
                                    minuses_amt = 0
                                print(comment.get("text"))
                                print(comment.get("createdDate"))
                                try:
                                    date = datetime.strptime(
                                        comment.get("createdDate"), "%Y-%m-%dT%H:%M:%SZ"
                                    )
                                except ValueError:
                                    date = None
                                comments.append(
                                    CommentWB(
                                        date=date,
                                        author=str(
                                            comment.get("wbUserDetails").get("name")
                                        ),
                                        rating=comment.get("productValuation"),
                                        advantages=str(comment.get("pros")),
                                        disadvantages=str(comment.get("cons")),
                                        comment=str(comment.get("text")),
                                        pluses_amt=int(pluses_amt),
                                        minuses_amt=int(minuses_amt),
                                        tonality=inference(
                                            str(comment.get("text")),
                                            model,
                                            stop_words,
                                            vectorizer,
                                            transformer,
                                        ),
                                    )
                                )
                    # If product was found then we add comments to it
                    if found:
                        found.comments.extend(comments)
                        found.comments_amt = int(product["feedbacks"])
                        products.append(found.id_product)
                    # Else we create new product
                    else:
                        ProductWB(
                            id_product=str(product["id"]),
                            root_imt_id=product_root,
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
                            comments_amt=int(product["feedbacks"]),
                            comments=comments,
                        ).save()
                        products.append(str(product["id"]))
    return products
