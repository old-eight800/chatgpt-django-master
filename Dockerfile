FROM python:3.9.0
RUN mkdir /app
COPY . /app 
COPY requirements.txt /app
RUN pip install -r /app/requirements.txt
WORKDIR /app
RUN python manage.py migrate
RUN python manage.py makemigrations
