# Выкачиваем из dockerhub образ с python версии 3.9
FROM python:3.10
# Устанавливаем рабочую директорию для проекта в контейнере
WORKDIR /backend
# Скачиваем/обновляем необходимые библиотеки для проекта
COPY pyproject.toml /backend/
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
#RUN poetry lock
RUN poetry install --no-interaction --no-ansi
#RUN poetry --help
RUN poetry add flask gunicorn bs4 aiohttp asyncio fake_useragent pymongo aioflask asgiref python-dotenv
RUN poetry lock
COPY . /backend
# Устанавливаем порт, который будет использоваться для сервера
EXPOSE 9876