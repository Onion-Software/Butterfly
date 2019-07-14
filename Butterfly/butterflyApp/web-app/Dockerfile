# Base image
FROM python:3.7-slim

# Working directory
WORKDIR ./web-app

# Copy files into the container
COPY ./web-app .
COPY ./mongodb ./mongodb

# Exopose port to other containers
EXPOSE 80

# Install dependencies
RUN pip3 install -r requirements.txt

CMD python3 -m app
