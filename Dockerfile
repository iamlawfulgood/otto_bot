FROM python:3

RUN mkdir /var/otto_bot
WORKDIR /var/otto_bot

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-u", "./bot.py" ]