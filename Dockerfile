# Usa una base Python ufficiale
FROM python:3.11-slim

# Installa dipendenze di sistema necessarie
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        wget \
        curl \
        ca-certificates \
        gcc \
        make \
        sudo \
        tar \
        libffi-dev \
        libssl-dev \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        && rm -rf /var/lib/apt/lists/*

# Installa TA-Lib da sorgente
RUN curl -L -O http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Imposta variabile per il linker
ENV LD_LIBRARY_PATH="/usr/lib:${LD_LIBRARY_PATH}"

# Imposta directory di lavoro
WORKDIR /app

# Copia i file del progetto
COPY . /app

# Installa le dipendenze Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 10000

# Avvio dell'applicazione (modifica se usi uvicorn o altro)
CMD ["python", "main.py"]
