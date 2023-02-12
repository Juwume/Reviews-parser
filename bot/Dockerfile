FROM python:3.9.13-bullseye

COPY requirements.txt .
RUN pip install --user -r requirements.txt

COPY telegram_bot.py .



CMD [ "python", "./telegram_bot.py" ]