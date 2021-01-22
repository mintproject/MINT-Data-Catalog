FROM python:3.6-alpine
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev g++ nodejs npm
# Install python requirements
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 7000
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]