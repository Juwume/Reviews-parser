import os
import pymorphy2
import re
from joblib import load


MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),'models/xgboost.joblib')
VECTORIZER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),'models/count_vectorizer.pkl')
TRANSFORMER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),'models/tf_idf_transformer.pkl')
STOP_WORDS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),'models/stop_words.txt')
# Constant for classification
THRESHOLD = 0.6

def read_model():
    """
    Function that reads all important objects for inference
    :return: loaded objects (model, stop_words, vectorizer, transformer)
    """
    with open(STOP_WORDS_PATH, 'r', encoding='utf-8') as f:
        stop_words = [line.rstrip('\n') for line in f]
    vectorizer = load(VECTORIZER_PATH)
    transformer = load(TRANSFORMER_PATH)
    model = load(MODEL_PATH)
    return model, stop_words, vectorizer, transformer

def inference(text:str, model, stop_words:list, vectorizer, transformer):
    """
    Inference function for text classification model.
    Our classification model achieves on test data:
    Accuracy = 0.9466007732268533
    Precicion = 0.9260379462934971
    Recall = 0.9390572924932551
    Roc auc = 0.9466007732268533
    :param text: Text to classify
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