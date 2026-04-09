#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill: Utilidades de Tiempo
Proporciona herramientas de fecha, hora y temporizadores
"""

import time
import subprocess
from datetime import datetime, timedelta
from typing import Any


def now() -> str:
    """
    Muestra la fecha y hora actual.
    
    Returns:
        Fecha y hora formateada
    """
    current = datetime.now()
    
    result = []
    result.append("🕐 FECHA Y HORA ACTUAL")
    result.append("═" * 40)
    result.append(f"Fecha: {current.strftime('%A, %d de %B de %Y')}")
    result.append(f"Hora: {current.strftime('%H:%M:%S')}")
    result.append(f"Zona horaria: {time.tzname[0] if time.tzname else 'UTC'}")
    result.append("")
    result.append(f"ISO 8601: {current.isoformat()}")
    result.append(f"Timestamp: {int(current.timestamp())}")
    
    return "\n".join(result)


def timer(seconds: str, message: str = None) -> str:
    """
    Configura un temporizador.
    
    Args:
        seconds: Segundos para el temporizador
        message: Mensaje opcional
    
    Returns:
        Confirmación
    """
    try:
        secs = int(seconds)
        
        if secs <= 0:
            return "Error: El tiempo debe ser positivo."
        
        if secs > 3600:
            return "Error: Máximo 3600 segundos (1 hora)."
        
        # Calcular tiempo final
        end_time = datetime.now() + timedelta(seconds=secs)
        
        msg = message or "¡Temporizador terminado!"
        
        # En Termux, podemos usar termux-notification o termux-vibrate
        result = []
        result.append(f"⏱️ TEMPORIZADOR CONFIGURADO")
        result.append("═" * 40)
        result.append(f"Duración: {secs} segundos")
        result.append(f"Termina a las: {end_time.strftime('%H:%M:%S')}")
        result.append(f"Mensaje: {msg}")
        result.append("")
        result.append("El temporizador se ejecutará en segundo plano...")
        
        # Crear script de temporizador en segundo plano
        import threading
        
        def timer_thread():
            time.sleep(secs)
            try:
                # Intentar notificar
                subprocess.run(
                    ['termux-notification', '--title', 'Temporizador', '--content', msg],
                    capture_output=True,
                    timeout=5
                )
            except:
                pass
            
            try:
                # Vibrar
                subprocess.run(
                    ['termux-vibrate', '-d', '1000'],
                    capture_output=True,
                    timeout=5
                )
            except:
                pass
        
        thread = threading.Thread(target=timer_thread, daemon=True)
        thread.start()
        
        return "\n".join(result)
        
    except ValueError:
        return "Error: El tiempo debe ser un número entero."


def countdown(target: str) -> str:
    """
    Muestra cuenta regresiva hasta una fecha/hora.
    
    Args:
        target: Fecha objetivo (formato: YYYY-MM-DD HH:MM:SS)
    
    Returns:
        Tiempo restante
    """
    try:
        # Intentar parsear la fecha
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y',
            '%H:%M:%S',
        ]
        
        target_dt = None
        for fmt in formats:
            try:
                target_dt = datetime.strptime(target, fmt)
                break
            except ValueError:
                continue
        
        if target_dt is None:
            return f"Error: Formato de fecha no reconocido. Intenta: YYYY-MM-DD HH:MM:SS"
        
        # Si solo se proporcionó hora, usar fecha de hoy
        if target_dt.year == 1900:
            today = datetime.now()
            target_dt = target_dt.replace(year=today.year, month=today.month, day=today.day)
        
        now_dt = datetime.now()
        diff = target_dt - now_dt
        
        if diff.total_seconds() < 0:
            return "¡La fecha objetivo ya pasó!"
        
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        result = []
        result.append("⏳ CUENTA REGRESIVA")
        result.append("═" * 40)
        result.append(f"Objetivo: {target_dt.strftime('%A, %d de %B de %Y a las %H:%M:%S')}")
        result.append("")
        result.append(f"Tiempo restante:")
        result.append(f"  {days} días")
        result.append(f"  {hours} horas")
        result.append(f"  {minutes} minutos")
        result.append(f"  {seconds} segundos")
        result.append("")
        result.append(f"Total: {int(diff.total_seconds())} segundos")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"Error: {e}"


def stopwatch(action: str = 'start') -> str:
    """
    Controla un cronómetro.
    
    Args:
        action: 'start', 'stop', 'lap', 'reset', 'status'
    
    Returns:
        Estado del cronómetro
    """
    # Usar archivo temporal para persistencia
    import os
    stopwatch_file = '/tmp/gemma_stopwatch.txt'
    
    action = action.lower()
    
    if action == 'start':
        start_time = time.time()
        with open(stopwatch_file, 'w') as f:
            f.write(f"start:{start_time}\nlaps:")
        return f"⏱️ Cronómetro iniciado a las {datetime.now().strftime('%H:%M:%S')}"
    
    elif action == 'stop':
        if not os.path.exists(stopwatch_file):
            return "Error: No hay cronómetro activo. Usa 'stopwatch start' primero."
        
        with open(stopwatch_file, 'r') as f:
            data = f.read()
        
        start_time = float(data.split('\n')[0].split(':')[1])
        elapsed = time.time() - start_time
        
        os.remove(stopwatch_file)
        
        hours, remainder = divmod(int(elapsed), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return f"⏹️ Cronómetro detenido. Tiempo total: {hours:02d}:{minutes:02d}:{seconds:02d}"
    
    elif action == 'lap':
        if not os.path.exists(stopwatch_file):
            return "Error: No hay cronómetro activo."
        
        with open(stopwatch_file, 'r') as f:
            lines = f.read().split('\n')
        
        start_time = float(lines[0].split(':')[1])
        elapsed = time.time() - start_time
        
        hours, remainder = divmod(int(elapsed), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return f"🏁 Vuelta: {hours:02d}:{minutes:02d}:{seconds:02d}"
    
    elif action == 'status':
        if not os.path.exists(stopwatch_file):
            return "No hay cronómetro activo."
        
        with open(stopwatch_file, 'r') as f:
            lines = f.read().split('\n')
        
        start_time = float(lines[0].split(':')[1])
        elapsed = time.time() - start_time
        
        hours, remainder = divmod(int(elapsed), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return f"⏱️ Cronómetro activo: {hours:02d}:{minutes:02d}:{seconds:02d}"
    
    elif action == 'reset':
        if os.path.exists(stopwatch_file):
            os.remove(stopwatch_file)
        return "🔄 Cronómetro reiniciado."
    
    return f"Acción desconocida: {action}. Usa: start, stop, lap, status, reset"


def timezone(tz: str = None) -> str:
    """
    Muestra o cambia la zona horaria.
    
    Args:
        tz: Zona horaria (opcional)
    
    Returns:
        Información de zona horaria
    """
    if tz is None:
        # Mostrar zona horaria actual
        result = []
        result.append("🌍 ZONA HORARIA")
        result.append("═" * 40)
        result.append(f"Zona actual: {time.tzname[0] if time.tzname else 'UTC'}")
        result.append(f"Offset: {time.timezone // 3600} horas")
        result.append("")
        result.append("Zonas horarias comunes:")
        result.append("  UTC, EST, CST, MST, PST")
        result.append("  Europe/Madrid, Europe/London")
        result.append("  America/New_York, America/Los_Angeles")
        result.append("  Asia/Tokyo, Asia/Shanghai")
        
        return "\n".join(result)
    
    # Intentar cambiar zona horaria (solo muestra info, no cambia realmente)
    return f"Información de zona horaria: {tz}\nNota: Cambiar zona horaria requiere permisos de sistema."


def convert_time(time_str: str, from_tz: str, to_tz: str) -> str:
    """
    Convierte hora entre zonas horarias.
    
    Args:
        time_str: Hora a convertir (HH:MM)
        from_tz: Zona horaria de origen
        to_tz: Zona horaria de destino
    
    Returns:
        Hora convertida
    """
    # Esta es una implementación simplificada
    # En una implementación real, usaríamos pytz
    
    offsets = {
        'utc': 0,
        'gmt': 0,
        'est': -5,
        'edt': -4,
        'cst': -6,
        'cdt': -5,
        'mst': -7,
        'mdt': -6,
        'pst': -8,
        'pdt': -7,
        'jst': 9,
        'cst_cn': 8,  # China
        'ist': 5.5,   # India
        'cet': 1,     # Europa Central
        'cest': 2,
    }
    
    from_tz = from_tz.lower()
    to_tz = to_tz.lower()
    
    if from_tz not in offsets or to_tz not in offsets:
        return f"Zonas soportadas: {', '.join(offsets.keys())}"
    
    try:
        # Parsear hora
        parts = time_str.split(':')
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
        
        # Calcular diferencia
        diff = offsets[to_tz] - offsets[from_tz]
        
        # Convertir
        new_hour = (hour + int(diff)) % 24
        new_minute = minute + int((diff % 1) * 60)
        
        if new_minute >= 60:
            new_hour = (new_hour + 1) % 24
            new_minute -= 60
        elif new_minute < 0:
            new_hour = (new_hour - 1) % 24
            new_minute += 60
        
        return f"{hour:02d}:{minute:02d} ({from_tz.upper()}) = {new_hour:02d}:{new_minute:02d} ({to_tz.upper()})"
        
    except Exception as e:
        return f"Error: {e}"


def calendar(month: str = None, year: str = None) -> str:
    """
    Muestra un calendario.
    
    Args:
        month: Mes (1-12)
        year: Año
    
    Returns:
        Calendario formateado
    """
    import calendar as cal
    
    try:
        if month and year:
            month_num = int(month)
            year_num = int(year)
            cal_str = cal.month(year_num, month_num)
        elif year:
            year_num = int(year)
            cal_str = cal.calendar(year_num)
        else:
            now = datetime.now()
            cal_str = cal.month(now.year, now.month)
        
        return f"```\n{cal_str}\n```"
        
    except Exception as e:
        return f"Error: {e}"


# Definición de comandos exportados
COMMANDS = {
    'now': now,
    'timer': timer,
    'countdown': countdown,
    'stopwatch': stopwatch,
    'timezone': timezone,
    'convert_time': convert_time,
    'calendar': calendar,
}


# Información del skill
SKILL_INFO = {
    'name': 'Time Utils',
    'description': 'Utilidades de fecha, hora y temporizadores',
    'version': '1.0',
    'author': 'Gemma Termux App',
    'commands': list(COMMANDS.keys())
}


def info():
    """Retorna información del skill"""
    return SKILL_INFO
