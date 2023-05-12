[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=40&duration=4000&pause=1000&color=19F768&background=3925FF00&vCenter=true&width=435&lines=Our+Diploma+work;Enjoy+%3A3)](https://git.io/typing-svg)
## PURPOSE
This our final project in BMSTU.
## AUTHORS
1. Smyslov Maxim (Back-end)
2. Bogdanova Valeria (Front-end)
## ARCHITECTURE
![image](https://github.com/Juwume/Reviews-parser/assets/71034341/fd63ea12-fd24-4d5a-bcaa-ef01344e97b5)

## TECHNOLOGIES
This app works as a web service, which parses marketplaces, 
then classifies comments as negative or positive and finaly 
sends the results in Telegram bot

### Technology stack: 
  - `Telebot` 
  - `Flask` 
  - `Aiohttp`
  - `TF-IDF` as text transformer
  - `XGBoost` as tonality classifier
  - `mongoengine` as ORM 
  - `MongoDB` on parser side
  - `PostgreSQL` on bot side
## DATASET
For classification was taken a dataset of human labeled comments from marketplaces. This dataset contains comments from cat food products and each comment is marked as positive or negative.
## MODEL QUALITY
    Precicion = 0.9260379462934971
    Recall = 0.9390572924932551
    Roc auc = 0.9466007732268533
## HOW TO RUN
1. Fill in the credentials in the `.env` file (there is an example)
2. ```docker-compose build```
3. ```docker-compose up```
4. Enjoy


