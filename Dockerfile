FROM python:3.11

RUN apt update && apt upgrade -y
RUN apt install -y poppler-utils

# Set the POPPLER_PATH environment variable dynamically
RUN POPPLER_PATH=$(dirname $(which pdftotext)) && echo "POPPLER_PATH=$POPPLER_PATH" >> /etc/environment
ENV POPPLER_PATH=$POPPLER_PATH
ENV PATH=$POPPLER_PATH:$PATH

COPY src /app/src
COPY run_application.py /app/run_application.py
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock
COPY .env /app/.env
COPY config.cfg /app/config.cfg
WORKDIR /app
RUN mkdir -p /app/temp

RUN pip install --no-cache-dir uv
RUN uv sync --frozen
ENTRYPOINT [ "uv", "run","run_app.py" ]


