FROM python:3.9
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt


COPY main.py /app/app.py
COPY jobs.py /app/jobs.py
COPY worker.py /app/worker.py
