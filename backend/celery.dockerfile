FROM python:3.8 as requirements-stage
WORKDIR /tmp
RUN pip install poetry
COPY ./app/pyproject.toml ./app/poetry.lock* /tmp/

RUN poetry export -f requirements.txt -E make_dataset --output requirements.txt --without-hashes


FROM python:3.8-slim AS compile-image
RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc wget

# Make sure we use the virtualenv:
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install numpy==1.21.1

# TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/opt/venv && \
    make && \
    make install

RUN pip install --upgrade pip
RUN pip install --global-option=build_ext --global-option="-L/opt/venv/lib" TA-Lib==0.4.21
RUN rm -R ta-lib ta-lib-0.4.0-src.tar.gz

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

FROM python:3.8-slim AS build-image
COPY --from=compile-image /opt/venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"
ENV LD_LIBRARY_PATH="/opt/venv/lib"

WORKDIR /app/

# Run Celery with superuser privileges if C_FORCE_ROOT=1 
ENV C_FORCE_ROOT=1

COPY ./app /app
WORKDIR /app

ENV PYTHONPATH=/app

COPY ./app/beat-start.sh /beat-start.sh
RUN chmod +x /beat-start.sh

COPY ./app/worker-start.sh /worker-start.sh
RUN chmod +x /worker-start.sh