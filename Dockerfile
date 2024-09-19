FROM python:3.11-slim 

COPY . /app
WORKDIR /app

RUN apt-get update && apt-get install -y g++
RUN pip3 install -r requirements.txt 

CMD uvicorn app.server:app --host 0.0.0.0 --port 8000  
