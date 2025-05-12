# -*- coding: utf-8 -*-
from flask import Flask, render_template
import requests
import json
import time
import os

app = Flask(__name__)

# Configurações da API do OpenWeatherMap
API_KEY = "0e873405fb1221fdf1c2478212d6bb44"
CIDADE = "Blumenau,BR"
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CIDADE}&appid={API_KEY}&units=metric&lang=pt_br"
CACHE_FILE = "weather_cache.json"
CACHE_DURATION = 600  # 10 minutos em segundos

def get_weather_data():
    # Verifica se o arquivo de cache existe e tenta usá-lo
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
                if time.time() - cache['timestamp'] < CACHE_DURATION:
                    return cache['data']
        except (json.JSONDecodeError, KeyError):
            # Se o arquivo de cache estiver corrompido, prossegue para criar um novo
            pass

    # Se o cache não existe, está expirado ou corrompido, faz uma nova chamada à API
    try:
        weather_response = requests.get(WEATHER_URL)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        if weather_response.status_code == 200:
            # Dados atuais
            current_data = {
                'temperatura': weather_data['main']['temp'],
                'descricao': weather_data['weather'][0]['description'],
                'cidade': CIDADE,
                'sensacao': weather_data['main']['feels_like'],
                'umidade': weather_data['main']['humidity'],
                'vento': weather_data['wind']['speed'] * 3.6  # Convertendo m/s para km/h
            }

            # Salva os dados no cache
            cache_data = {
                'timestamp': time.time(),
                'data': current_data
            }
            with open(CACHE_FILE, 'w') as f:
                json.dump(cache_data, f)
            return cache_data['data']
        else:
            return {'erro': f"Erro na API: Código {weather_response.status_code}"}
    except Exception as e:
        return {'erro': f"Erro: {str(e)}"}

@app.route('/')
def index():
    weather_data = get_weather_data()
    if 'erro' in weather_data:
        return render_template('index.html', erro=weather_data['erro'])
    return render_template('index.html', 
                         temperatura=weather_data['temperatura'], 
                         descricao=weather_data['descricao'], 
                         cidade=weather_data['cidade'],
                         sensacao=weather_data['sensacao'],
                         umidade=weather_data['umidade'],
                         vento=weather_data['vento'])

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))  # Usa a porta fornecida pelo Render ou 5000 como padrão
    app.run(host='0.0.0.0', port=port, debug=False)
