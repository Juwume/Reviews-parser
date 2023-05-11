from src import app
import os
import time

if __name__ == '__main__':
    os.environ['TZ'] = 'Europe/Moscow'
    time.tzset()
    app.run(host='0.0.0.0', port=5000)

