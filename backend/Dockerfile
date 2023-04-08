# Выкачиваем из dockerhub образ с python версии 3.9
FROM python:3.9.13-bullseye
# Устанавливаем рабочую директорию для проекта в контейнере
WORKDIR /backend
# Скачиваем/обновляем необходимые библиотеки для проекта
#COPY pyproject.toml /backend/

RUN pip3 install --upgrade pip &&  \
    pip3 install "poetry==1.1.15"

COPY pyproject.toml ./pyproject.toml
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi && \
    poetry lock
COPY . .
# Устанавливаем порт, который будет использоваться для сервера
EXPOSE 5000