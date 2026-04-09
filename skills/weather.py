#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill: Clima
Proporciona información meteorológica usando wttr.in
"""

import urllib.request
import json
from typing import Any


def weather(location: str = None) -> str:
    """
    Muestra el clima actual.
    
    Args:
        location: Ciudad o ubicación (opcional, usa auto-detección si no se proporciona)
    
    Returns:
        Información del clima
    """
    try:
        # Usar wttr.in (servicio gratuito sin API key)
        if location:
            url = f"https://wttr.in/{location}?format=j1&lang=es"
        else:
            url = "https://wttr.in/?format=j1&lang=es"
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'curl/7.68.0'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        # Extraer información actual
        current = data['current_condition'][0]
        location_info = data['nearest_area'][0]
        
        city = location_info['areaName'][0]['value']
        country = location_info['country'][0]['value']
        
        temp_c = current['temp_C']
        temp_f = current['temp_F']
        feels_like_c = current['FeelsLikeC']
        desc = current['lang_es'][0]['value'] if 'lang_es' in current else current['weatherDesc'][0]['value']
        humidity = current['humidity']
        wind_kmph = current['windspeedKmph']
        visibility = current['visibility']
        pressure = current['pressure']
        uv_index = current['uvIndex']
        
        result = []
        result.append("🌤️  CLIMA ACTUAL")
        result.append("═" * 40)
        result.append(f"📍 Ubicación: {city}, {country}")
        result.append("")
        result.append(f"🌡️  Temperatura: {temp_c}°C ({temp_f}°F)")
        result.append(f"🤔 Sensación térmica: {feels_like_c}°C")
        result.append(f"☁️  Condición: {desc}")
        result.append("")
        result.append(f"💧 Humedad: {humidity}%")
        result.append(f"💨 Viento: {wind_kmph} km/h")
        result.append(f"👁️  Visibilidad: {visibility} km")
        result.append(f"🔽 Presión: {pressure} mb")
        result.append(f"☀️  Índice UV: {uv_index}")
        
        # Pronóstico para hoy
        today = data['weather'][0]
        max_temp = today['maxtempC']
        min_temp = today['mintempC']
        
        result.append("")
        result.append(f"📊 Pronóstico hoy:")
        result.append(f"   Máx: {max_temp}°C | Mín: {min_temp}°C")
        
        return "\n".join(result)
        
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return f"Ubicación no encontrada: {location}"
        return f"Error HTTP: {e.code}"
    except Exception as e:
        return f"Error obteniendo clima: {e}"


def forecast(location: str = None, days: str = "3") -> str:
    """
    Muestra el pronóstico extendido.
    
    Args:
        location: Ciudad o ubicación
        days: Número de días (1-3)
    
    Returns:
        Pronóstico extendido
    """
    try:
        num_days = min(int(days), 3)
        
        if location:
            url = f"https://wttr.in/{location}?format=j1&lang=es"
        else:
            url = "https://wttr.in/?format=j1&lang=es"
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'curl/7.68.0'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        location_info = data['nearest_area'][0]
        city = location_info['areaName'][0]['value']
        
        result = []
        result.append(f"📅 PRONÓSTICO PARA {city.upper()}")
        result.append("═" * 50)
        
        for i in range(num_days):
            day = data['weather'][i]
            date = day['date']
            max_temp = day['maxtempC']
            min_temp = day['mintempC']
            avg_temp = day['avgtempC']
            
            # Condición del día
            hourly = day['hourly'][4]  # Mediodía aprox
            desc = hourly['lang_es'][0]['value'] if 'lang_es' in hourly else hourly['weatherDesc'][0]['value']
            
            # Precipitación
            precip = day['hourly'][0]['chanceofrain']
            
            result.append("")
            result.append(f"📆 {date}:")
            result.append(f"   🌡️  {min_temp}°C - {max_temp}°C (prom: {avg_temp}°C)")
            result.append(f"   ☁️  {desc}")
            result.append(f"   🌧️  Prob. lluvia: {precip}%")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"Error obteniendo pronóstico: {e}"


def moon() -> str:
    """
    Muestra información lunar actual.
    
    Returns:
        Fase lunar y datos
    """
    try:
        url = "https://wttr.in/?format=j1"
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'curl/7.68.0'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        astro = data['weather'][0]['astronomy'][0]
        
        moon_phase = astro.get('moon_phase', 'Desconocida')
        moon_illumination = astro.get('moon_illumination', '0')
        sunrise = astro.get('sunrise', 'N/A')
        sunset = astro.get('sunset', 'N/A')
        moonrise = astro.get('moonrise', 'N/A')
        moonset = astro.get('moonset', 'N/A')
        
        # Emojis según fase
        phase_emojis = {
            'New Moon': '🌑',
            'Waxing Crescent': '🌒',
            'First Quarter': '🌓',
            'Waxing Gibbous': '🌔',
            'Full Moon': '🌕',
            'Waning Gibbous': '🌖',
            'Last Quarter': '🌗',
            'Waning Crescent': '🌘',
        }
        
        emoji = phase_emojis.get(moon_phase, '🌙')
        
        result = []
        result.append(f"{emoji} INFORMACIÓN LUNAR")
        result.append("═" * 40)
        result.append(f"Fase: {moon_phase}")
        result.append(f"Iluminación: {moon_illumination}%")
        result.append("")
        result.append("☀️  Sol:")
        result.append(f"   Salida: {sunrise}")
        result.append(f"   Puesta: {sunset}")
        result.append("")
        result.append("🌙 Luna:")
        result.append(f"   Salida: {moonrise}")
        result.append(f"   Puesta: {moonset}")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"Error obteniendo información lunar: {e}"


# Definición de comandos exportados
COMMANDS = {
    'weather': weather,
    'forecast': forecast,
    'moon': moon,
}


# Información del skill
SKILL_INFO = {
    'name': 'Weather',
    'description': 'Información meteorológica usando wttr.in',
    'version': '1.0',
    'author': 'Gemma Termux App',
    'commands': list(COMMANDS.keys()),
    'requirements': ['Conexión a internet']
}


def info():
    """Retorna información del skill"""
    return SKILL_INFO
