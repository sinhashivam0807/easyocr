FROM python:3.10
WORKDIR /app
ADD . /app

ENV PORT 8080
RUN pip install -r requirements.txt

RUN pip install Flask gunicorn
EXPOSE 80

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app