import os

app_dir = os.path.abspath(os.path.dirname(__file__))

MODEL_PATH = './model/bert_tiny2_v2.pt'
TOKENIZER_PATH = 'model/'
TO_CLASSIFY = True
# Данные для прокси (По умолчанию вставлен рандомный открытый прокси)
PROXY_LOGIN = os.environ.get('PROXY_LOGIN', None)
PROXY_PASS = os.environ.get('PROXY_PASS', None)
PROXY_ADDR = os.environ.get('PROXY_ADDR', 'http://159.112.235.217:80')