# Base image
FROM python:3.7-slim

# Working directory
WORKDIR ./redmine-producer

# Copy files into the container
COPY ./producers/redmine-producer .
COPY ./producers/producer.py ./producers/
COPY ./producers/__init__.py ./producers/

# Expose port to other containers
EXPOSE 5000

# Install dependencies
RUN pip3 install -r requirements.txt

CMD python3 -m redmine
