from mongoengine import *


class CommentWB(EmbeddedDocument):
    date = StringField(required=False)
    author = StringField(required=False)
    advantages = StringField(required=False)
    disadvantages = StringField(required=False)
    comment = StringField(required=False)
    rating = IntField(required=False)
    pluses_amt = IntField(required=False)
    minuses_amt = IntField(required=False)


class ProductWB(Document):
    id_product = StringField(required=True)
    root_imt_id = StringField(required=True)
    name = StringField(required=True)
    description = StringField(required=False)
    seller = StringField(required=False)
    category_name = StringField(required=False)
    brand = StringField(required=False)
    price = FloatField(required=False)
    price_old = FloatField(required=False)
    url = StringField(required=False)
    rating = FloatField(required=False)
    feedbacks_amt = IntField(required=True)
    query = StringField(required=False)
    comments = ListField(EmbeddedDocumentField(CommentWB))
    meta = {"db_alias": "WILDBERRIES"}


class QueryWB(Document):
    query = StringField(required=True)
    timestamp = DateTimeField()
    meta = {"db_alias": "WILDBERRIES"}
