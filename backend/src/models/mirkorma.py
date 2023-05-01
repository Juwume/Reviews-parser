# 'price',
# 'price_old',
# 'url',
# 'is_available',

from mongoengine import *


class CommentMirkorma(EmbeddedDocument):
    date = StringField(required=False)
    author = StringField(required=False)
    city = StringField(required=False)
    advantages = StringField(required=False)
    disadvantages = StringField(required=False)
    comment = StringField(required=False)
    rating = IntField(required=False)
    usage_frequency = StringField(required=False)
    usage_period = StringField(required=False)


class ProductMirkorma(EmbeddedDocument):
    id_product = StringField(required=True)
    name = StringField(required=False)
    category_id = StringField(required=False)
    category_name = StringField(required=False)
    brand = StringField(required=False)
    price = FloatField(required=False)
    price_old = FloatField(required=False)
    url = StringField(required=False)
    query = StringField(required=False)
    is_available = BooleanField(required=False)
    comments = ListField(EmbeddedDocumentField(CommentMirkorma))
    meta = {"db_alias": "MIRKORMA"}


class QueryMirkorma(Document):
    query = StringField(required=True)
    timestamp = DateTimeField()
    comments = ListField(EmbeddedDocumentField(ProductMirkorma))
    meta = {"db_alias": "MIRKORMA"}
