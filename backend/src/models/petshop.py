from mongoengine import *


class CommentPetshop(EmbeddedDocument):
    id_comment = StringField(required=True)
    date = DateTimeField()
    author = StringField(required=False)
    city = StringField(required=False)
    advantages = StringField(required=False)
    disadvantages = StringField(required=False)
    comment = StringField(required=False)
    rating = IntField(required=False)
    tonality = FloatField(required=False)


class ProductPetshop(Document):
    id_product = StringField(required=True)
    id_similar_products = StringField(required=False)
    name = StringField(required=False)
    description = StringField(required=False)
    category_id = StringField(required=False)
    category_name = StringField(required=False)
    brand = StringField(required=False)
    price = FloatField(required=False)
    price_regional = FloatField(required=False)
    price_old = FloatField(required=False)
    url = StringField(required=False)
    is_available = BooleanField(required=False)
    comments_amt = IntField(required=False)
    comments = ListField(EmbeddedDocumentField(CommentPetshop))
    meta = {"db_alias": "PETSHOP"}


# class ProductPetshopEmbedded(EmbeddedDocument):
#     id_product = StringField(required=True)
#     id_similar_products = StringField(required=False)
#     name = StringField(required=False)
#     description = StringField(required=False)
#     category_id = StringField(required=False)
#     category_name = StringField(required=False)
#     brand = StringField(required=False)
#     price = FloatField(required=False)
#     price_regional = FloatField(required=False)
#     price_old = FloatField(required=False)
#     url = StringField(required=False)
#     is_available = BooleanField(required=False)
#     comments_amt = IntField(required=False)
#     comments = ListField(EmbeddedDocumentField(CommentPetshop))


class QueryPetshop(Document):
    query = StringField(required=True)
    timestamp = DateTimeField()
    products = ListField(StringField())
    meta = {"db_alias": "PETSHOP"}
