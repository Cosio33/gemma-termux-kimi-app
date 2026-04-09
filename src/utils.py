#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidades compartidas para Gemma Termux App
"""

import os
import re
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta


def format_size(size_bytes: int) -> str:
    """Formatea tamaño en bytes a formato legible"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f}KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f}MB"
    else:
        return f"{size_bytes/(1024**3):.1f}GB"


def format_duration(seconds: int) -> str:
    """Formatea segundos a formato legible"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Trunca texto a longitud máxima"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """Sanitiza nombre de archivo"""
    # Remover caracteres inválidos
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remover espacios al inicio/fin
    filename = filename.strip()
    # Limitar longitud
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255 - len(ext)] + ext
    return filename


def hash_string(text: str, algorithm: str = 'md5') -> str:
    """Genera hash de string"""
    if algorithm == 'md5':
        return hashlib.md5(text.encode()).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(text.encode()).hexdigest()
    elif algorithm == 'sha256':
        return hashlib.sha256(text.encode()).hexdigest()
    else:
        raise ValueError(f"Algoritmo no soportado: {algorithm}")


def parse_time_string(time_str: str) -> Optional[int]:
    """
    Parsea string de tiempo a segundos.
    
    Soporta formatos:
    - '10s' -> 10 segundos
    - '5m' -> 5 minutos
    - '2h' -> 2 horas
    - '1d' -> 1 día
    - '30' -> 30 segundos (default)
    """
    time_str = time_str.strip().lower()
    
    # Patrón: número + unidad
    match = re.match(r'^(\d+)\s*([smhd])?$', time_str)
    if not match:
        return None
    
    value = int(match.group(1))
    unit = match.group(2) or 's'
    
    multipliers = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
    }
    
    return value * multipliers.get(unit, 1)


def is_valid_email(email: str) -> bool:
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_url(url: str) -> bool:
    """Valida formato de URL"""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None


def extract_urls(text: str) -> List[str]:
    """Extrae URLs de texto"""
    pattern = r'https?://[^\s/$.?#].[^\s]*'
    return re.findall(pattern, text)


def extract_emails(text: str) -> List[str]:
    """Extrae emails de texto"""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)


def safe_eval(expression: str, allowed_names: Dict[str, Any] = None) -> Any:
    """
    Evalúa expresión de forma segura.
    
    Args:
        expression: Expresión a evaluar
        allowed_names: Diccionario de nombres permitidos
    
    Returns:
        Resultado de la evaluación
    """
    if allowed_names is None:
        allowed_names = {}
    
    # Crear entorno seguro
    safe_dict = {
        '__builtins__': {},
        'abs': abs,
        'round': round,
        'max': max,
        'min': min,
        'sum': sum,
        'len': len,
        'range': range,
    }
    safe_dict.update(allowed_names)
    
    try:
        return eval(expression, {"__builtins__": {}}, safe_dict)
    except Exception as e:
        raise ValueError(f"Error evaluando expresión: {e}")


def load_json_file(path: Path) -> Dict[str, Any]:
    """Carga archivo JSON de forma segura"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parseando JSON: {e}")


def save_json_file(path: Path, data: Dict[str, Any], indent: int = 2):
    """Guarda datos a archivo JSON"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def get_file_info(path: Path) -> Dict[str, Any]:
    """Obtiene información detallada de un archivo"""
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    
    stat = path.stat()
    
    return {
        'name': path.name,
        'path': str(path),
        'size': stat.st_size,
        'size_formatted': format_size(stat.st_size),
        'is_file': path.is_file(),
        'is_dir': path.is_dir(),
        'extension': path.suffix,
        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
    }


def search_files(directory: Path, pattern: str = '*', recursive: bool = True) -> List[Path]:
    """Busca archivos por patrón"""
    if recursive:
        return list(directory.rglob(pattern))
    else:
        return list(directory.glob(pattern))


def count_lines_of_code(directory: Path, extensions: List[str] = None) -> Dict[str, int]:
    """Cuenta líneas de código por extensión"""
    if extensions is None:
        extensions = ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h']
    
    stats = {ext: {'files': 0, 'lines': 0} for ext in extensions}
    
    for ext in extensions:
        for file_path in directory.rglob(f'*{ext}'):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                        stats[ext]['files'] += 1
                        stats[ext]['lines'] += lines
                except:
                    pass
    
    return stats


def create_table(data: List[List[str]], headers: List[str] = None) -> str:
    """Crea tabla ASCII a partir de datos"""
    if not data:
        return "(sin datos)"
    
    # Calcular anchos de columna
    if headers:
        all_rows = [headers] + data
    else:
        all_rows = data
    
    col_widths = []
    for col_idx in range(len(all_rows[0])):
        max_width = max(len(str(row[col_idx])) for row in all_rows if col_idx < len(row))
        col_widths.append(max_width)
    
    # Construir tabla
    lines = []
    
    # Línea superior
    lines.append('+' + '+'.join('-' * (w + 2) for w in col_widths) + '+')
    
    # Headers
    if headers:
        header_row = '| ' + ' | '.join(
            str(h).ljust(w) for h, w in zip(headers, col_widths)
        ) + ' |'
        lines.append(header_row)
        lines.append('+' + '+'.join('=' * (w + 2) for w in col_widths) + '+')
    
    # Datos
    for row in data:
        data_row = '| ' + ' | '.join(
            str(cell).ljust(w) for cell, w in zip(row, col_widths)
        ) + ' |'
        lines.append(data_row)
    
    # Línea inferior
    lines.append('+' + '+'.join('-' * (w + 2) for w in col_widths) + '+')
    
    return '\n'.join(lines)


def progress_bar(current: int, total: int, width: int = 40) -> str:
    """Genera barra de progreso ASCII"""
    if total == 0:
        return "[" + " " * width + "] 0%"
    
    percent = current / total
    filled = int(width * percent)
    empty = width - filled
    
    bar = "█" * filled + "░" * empty
    percentage = int(percent * 100)
    
    return f"[{bar}] {percentage}%"


def spinner_frame(frame: int) -> str:
    """Retorna frame de spinner para animación"""
    frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    return frames[frame % len(frames)]


def natural_sort_key(text: str) -> List:
    """Key para ordenamiento natural"""
    return [int(c) if c.isdigit() else c.lower() for c in re.split('([0-9]+)', text)]


def pluralize(count: int, singular: str, plural: str = None) -> str:
    """Pluraliza palabra según count"""
    if plural is None:
        plural = singular + 's'
    
    if count == 1:
        return f"{count} {singular}"
    else:
        return f"{count} {plural}"


def humanize_datetime(dt: datetime) -> str:
    """Humaniza fecha/hora (ej: 'hace 5 minutos')"""
    now = datetime.now()
    diff = now - dt
    
    if diff < timedelta(minutes=1):
        return "hace unos segundos"
    elif diff < timedelta(hours=1):
        minutes = int(diff.seconds / 60)
        return f"hace {pluralize(minutes, 'minuto')}"
    elif diff < timedelta(days=1):
        hours = int(diff.seconds / 3600)
        return f"hace {pluralize(hours, 'hora')}"
    elif diff < timedelta(days=7):
        days = diff.days
        return f"hace {pluralize(days, 'día')}"
    elif diff < timedelta(days=30):
        weeks = diff.days // 7
        return f"hace {pluralize(weeks, 'semana')}"
    elif diff < timedelta(days=365):
        months = diff.days // 30
        return f"hace {pluralize(months, 'mes', 'meses')}"
    else:
        years = diff.days // 365
        return f"hace {pluralize(years, 'año')}"


# Clase para caché simple
class SimpleCache:
    """Caché en memoria simple con TTL"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Any:
        """Obtiene valor del caché"""
        if key in self._cache:
            item = self._cache[key]
            if item['expires'] is None or datetime.now() < item['expires']:
                return item['value']
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = None):
        """Guarda valor en caché"""
        expires = None
        if ttl_seconds is not None:
            expires = datetime.now() + timedelta(seconds=ttl_seconds)
        
        self._cache[key] = {
            'value': value,
            'expires': expires,
        }
    
    def delete(self, key: str):
        """Elimina valor del caché"""
        self._cache.pop(key, None)
    
    def clear(self):
        """Limpia todo el caché"""
        self._cache.clear()
    
    def keys(self) -> List[str]:
        """Retorna todas las claves"""
        return list(self._cache.keys())


# Instancia global de caché
cache = SimpleCache()
