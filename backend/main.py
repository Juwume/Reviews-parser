# from flask_script import Manager, Shell
from src import app
# from src.classifier.bert_classifier import BertClassifier
# from config import MODEL_PATH, TOKENIZER_PATH, TO_CLASSIFY
# manager = Manager(src)


# эти переменные доступны внутри оболочки без явного импорта
# def make_shell_context():
#     return dict(src=src)
import os

# manager.add_command('shell', Shell(make_context=make_shell_context))
# manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

    # bert_model_tiny2 = BertClassifier(
    #     MODEL_PATH,
    #     TOKENIZER_PATH,
    #     n_classes=3,
    #     epochs=20,
    #     model_save_path='models/rubert-tiny2/bert.pt',
    #     to_classify=TO_CLASSIFY
    # )
