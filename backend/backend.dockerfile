FROM python:3.8

WORKDIR /app/
# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy using poetry.lock* in case it doesn't exist yet
COPY ./app/pyproject.toml ./app/poetry.lock* /app/

COPY ./gunicorn.conf.py /gunicorn.conf.py
COPY ./app/start.sh /start.sh
RUN chmod +x /start.sh
COPY ./app/start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh


RUN poetry install --no-root --no-dev

COPY ./app /app
ENV PYTHONPATH=/app

EXPOSE 80
CMD ["/start.sh"]