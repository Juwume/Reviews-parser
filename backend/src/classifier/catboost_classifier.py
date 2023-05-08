import pymorphy2
import re
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from joblib import load

MODEL_PATH = './models/xgboost.joblib'
VECTORIZER_PATH = './models/count_vectorizer.pkl'
TRANSFORMER_PATH = './models/tf_idf_transformer.pkl'
STOP_WORDS_PATH = './models/stop_words.txt'

def read_model(model_path:str, stop_words_path:str, vectorizer_path, transformer_path):
    """
    Function that reads all important objects for inference
    :param model_path: Path to the pretrained model
    :param stop_words_path: Path to the stop words dictionary
    :param vectorizer_path: Path to the CountVectorizer
    :param transformer_path: Path to the TF-IDF transformer
    :return: loaded objects (model, stop_words, vectorizer, transformer)
    """
    with open(stop_words_path, 'r') as f:
        stop_words = [line.rstrip('\n') for line in f]
    vectorizer = load(vectorizer_path)
    transformer = load(transformer_path)
    model = load(model_path)
    return model, stop_words, vectorizer, transformer

def inference(text:str, model, stop_words:list, vectorizer, transformer):
    """
    Inference function for text classification model
    :param text:
    :param model: Classification model
    :param stop_words: List of words to delete
    :param vectorizer: Pretrained CountVectorizer
    :param transformer: Pretrained TF-IDF transformer
    :return: 1 - if Negative, 0 - if Positive
    """
    # Cleaning text
    text_cleaned = re.sub('[^a-zA-Zа-яА-Я1-9]', ' ', text.lower())
    text_splitted = re.sub(r'\s+', ' ', text_cleaned).replace('не ', 'не').split(" ")
    # Filtering tockens
    text_filtered = [word for word in text_splitted if word not in stop_words and word != '']
    # Lemmatizing text
    morph = pymorphy2.MorphAnalyzer()
    text_lemmatized = ' '.join([morph.parse(word)[0].normal_form for word in text_filtered])
    # TF-IDF
    word_count_vector = vectorizer.transform([text_lemmatized])
    x = transformer.transform(word_count_vector)

    return model.predict(x)[0]