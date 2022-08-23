# from flask_script import Manager, Shell
from app import app

# manager = Manager(app)


# эти переменные доступны внутри оболочки без явного импорта
# def make_shell_context():
#     return dict(app=app)
import os
from dotenv import load_dotenv
# manager.add_command('shell', Shell(make_context=make_shell_context))
# manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    load_dotenv('.env')
    app.run(host='0.0.0.0', port=9876)
