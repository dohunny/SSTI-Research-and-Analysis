FROM python:3

WORKDIR /app

ADD . /app
RUN apt-get update
RUN apt-get install -y build-essential python3.9-dev
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install --upgrade wheel
RUN pip3 install uwsgi
RUN pip3 install -r requirements.txt

CMD ["uwsgi","uwsgi.ini"]
