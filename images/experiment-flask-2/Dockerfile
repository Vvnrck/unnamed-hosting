FROM ubuntu:16.04
MAINTAINER Anton Mitkovets <raisiel@yandex.ru>
RUN apt-get update && apt-get install -y git python-pip python-dev build-essential 
RUN pip install --upgrade pip 
RUN mkdir app && cd app
RUN git clone https://github.com/Vvnrck/unnamed-hosting-sample-flask.git
RUN cd unnamed-hosting-sample-flask
RUN pip install -r /unnamed-hosting-sample-flask/requirements.txt
