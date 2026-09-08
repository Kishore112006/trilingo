# TriDict

TriDict is a multilingual dictionary and translation web application.

It supports:

- English
- Telugu
- Hindi

## Technologies

- HTML
- CSS
- JavaScript
- Python
- Flask
- MySQL

## Features

- Automatic language detection
- English to Telugu
- English to Hindi
- Telugu to English
- Telugu to Hindi
- Hindi to English
- Hindi to Telugu
- English dictionary meaning
- Search history
- Delete history
- Mobile responsive design

## APIs

Translation:

MyMemory Translation API

Dictionary:

Free Dictionary API

## Installation

Install Python packages:

pip install -r requirements.txt

## Database

Create MySQL database:

CREATE DATABASE tridict;

Create history table:

CREATE TABLE history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    searched_word VARCHAR(255) NOT NULL,
    detected_language VARCHAR(20) NOT NULL,
    english VARCHAR(255),
    telugu VARCHAR(255),
    hindi VARCHAR(255),
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

## Run

python app.py

Open:

http://127.0.0.1:5000