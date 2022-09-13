# Выкачиваем из dockerhub образ с python версии 3.9
FROM python:3.9.13-bullseye
# Устанавливаем рабочую директорию для проекта в контейнере
WORKDIR /backend
# Скачиваем/обновляем необходимые библиотеки для проекта
#COPY pyproject.toml /backend/
RUN pip install --upgrade pip
RUN pip3 install "poetry==1.1.15"
COPY pyproject.toml /backend/
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi
RUN poetry add flask gunicorn bs4 aiohttp asyncio fake_useragent pymongo aioflask asgiref python-dotenv redis mongoengine
RUN poetry lock
COPY . /backend
# Устанавливаем порт, который будет использоваться для сервера
EXPOSE 5000