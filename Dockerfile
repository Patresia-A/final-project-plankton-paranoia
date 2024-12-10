FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ADD src /app

RUN pip install --no-cache-dir -r /app/requirements.txt

ENV FLASK_APP=app.routes:create_app

ENV FLASK_ENV=development

# Expose the Flask port and run the application
CMD ["flask", "run", "--host=0.0.0.0", "--debug"]
