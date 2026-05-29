FROM python:3.13-slim

# Ustawienie katalogu roboczego w kontenerze
WORKDIR /code

# Skopiowanie pliku z zależnościami
COPY ./requirements.txt /code/requirements.txt

# Instalacja zależności
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /code/requirements.txt

# Skopiowanie całej reszty kodu źródłowego
COPY . /code

# Komenda uruchamiająca aplikację wewnątrz kontenera
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]