

# 'price',
# 'price_old',
# 'url',
# 'is_available',

from mongoengine import *


class ProductMirkorma(Document):
	id_product = StringField(required=True)
	name = StringField(required=True)
	category_id = StringField(required=True)
	category_name = StringField(required=False)
	brand = StringField(required=False)
	price = FloatField(required=False)
	price_old = FloatField(required=False)
	url = StringField(required=False)
	rating = FloatField(required=False)
	query = StringField(required=False)
	comments = ListField(EmbeddedDocumentField(CommentWB))
	meta = {"db_alias": "WILDBERRIES"}