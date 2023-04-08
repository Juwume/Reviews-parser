FROM python:3.9.13-bullseye

COPY requirements.txt .
RUN pip install --user -r requirements.txt
WORKDIR /app
COPY /app .



CMD [ "python", "./telegram_bot.py" ]