FROM python:3.9-slim-buster

ENV PATH="/opt/homebrew/bin:$PATH"

WORKDIR /project-3-final-project-plankton-paranoia

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /project-3-final-project-plankton-paranoia/src

ENV FLASK_APP=app
ENV FLASK_ENV=development
ENV PYTHONPATH=/project-3-final-project-plankton-paranoia/src

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]