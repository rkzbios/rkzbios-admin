# Use an official Python runtime as a parent image
FROM python:3.7
LABEL maintainer="robert.hofstra@gmail.com"


RUN apt-get update
RUN apt-get install python3-dev default-libmysqlclient-dev  -y


RUN \
  apt-get update && \
  apt-get upgrade -y && \
  apt-get install python3-dev default-libmysqlclient-dev  -y && \
  rm -rf /var/lib/apt/lists/*

# Set environment varibles
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV production
ENV DJANGO_SETTINGS_MODULE rkzbios_site.settings.production

ARG NEXUS_USER
ARG NEXUS_PWD

COPY ./requirements.txt /code/requirements.txt
COPY ./requirements-nexus.txt /code/requirements-nexus.txt
COPY ./install.py /code/install.py


RUN pip install --upgrade pip
# Install any needed packages specified in requirements.txt
RUN pip install -r /code/requirements.txt
RUN pip install gunicorn

WORKDIR /code/
RUN python install.py $NEXUS_USER $NEXUS_PWD


# Copy the current directory contents into the container at /code/
COPY . /code/
# Set the working directory to /code/
WORKDIR /code/

#RUN useradd wagtail
#RUN chown -R wagtail /code
#USER wagtail

EXPOSE 8000
CMD exec gunicorn rkzbios_site.wsgi:application --bind 0.0.0.0:8000 --workers 3
