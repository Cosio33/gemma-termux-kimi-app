#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill: Utilidades del Sistema
Proporciona información y control del sistema Android/Termux
"""

import os
import subprocess
import platform
import shutil
from datetime import datetime
from typing import Any


def sysinfo() -> str:
    """
    Muestra información del sistema.
    
    Returns:
        Información detallada del sistema
    """
    info = []
    info.append("═" * 50)
    info.append("INFORMACIÓN DEL SISTEMA")
    info.append("═" * 50)
    
    # Información básica
    info.append(f"Sistema: {platform.system()}")
    info.append(f"Máquina: {platform.machine()}")
    info.append(f"Procesador: {platform.processor()}")
    info.append(f"Python: {platform.python_version()}")
    
    # Información de Termux
    if 'TERMUX_VERSION' in os.environ:
        info.append(f"Termux: {os.environ.get('TERMUX_VERSION', 'N/A')}")
    
    # Uso de disco
    try:
        stat = shutil.disk_usage('/')
        total_gb = stat.total / (1024**3)
        used_gb = stat.used / (1024**3)
        free_gb = stat.free / (1024**3)
        percent_used = (stat.used / stat.total) * 100
        
        info.append("")
        info.append("ALMACENAMIENTO:")
        info.append(f"  Total: {total_gb:.1f} GB")
        info.append(f"  Usado: {used_gb:.1f} GB ({percent_used:.1f}%)")
        info.append(f"  Libre: {free_gb:.1f} GB")
    except Exception as e:
        info.append(f"Almacenamiento: Error obteniendo info - {e}")
    
    # Memoria (usando /proc/meminfo si está disponible)
    try:
        if os.path.exists('/proc/meminfo'):
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            
            # Parsear memoria total
            for line in meminfo.split('\n'):
                if line.startswith('MemTotal:'):
                    mem_total_kb = int(line.split()[1])
                    mem_total_gb = mem_total_kb / (1024**2)
                    info.append("")
                    info.append("MEMORIA:")
                    info.append(f"  Total: {mem_total_gb:.1f} GB")
                    break
    except Exception as e:
        info.append(f"Memoria: Error obteniendo info - {e}")
    
    # Información de batería (Android)
    try:
        result = subprocess.run(
            ['termux-battery-status'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            battery_info = eval(result.stdout)  # JSON-like output
            info.append("")
            info.append("BATERÍA:")
            info.append(f"  Nivel: {battery_info.get('percentage', 'N/A')}%")
            info.append(f"  Estado: {battery_info.get('status', 'N/A')}")
            info.append(f"  Temperatura: {battery_info.get('temperature', 'N/A')}°C")
    except:
        pass  # termux-battery-status no disponible
    
    info.append("═" * 50)
    
    return "\n".join(info)


def battery() -> str:
    """
    Muestra información de la batería.
    
    Returns:
        Estado de la batería
    """
    try:
        result = subprocess.run(
            ['termux-battery-status'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            import json
            info = json.loads(result.stdout)
            
            lines = []
            lines.append("🔋 ESTADO DE BATERÍA")
            lines.append("═" * 30)
            lines.append(f"Nivel: {info.get('percentage', 'N/A')}%")
            lines.append(f"Estado: {info.get('status', 'N/A')}")
            
            if 'temperature' in info:
                lines.append(f"Temperatura: {info['temperature']}°C")
            if 'current' in info:
                lines.append(f"Corriente: {info['current']} mA")
            if 'voltage' in info:
                lines.append(f"Voltaje: {info['voltage']} mV")
            
            return "\n".join(lines)
        else:
            return "No se pudo obtener información de la batería."
            
    except FileNotFoundError:
        return "termux-battery-status no disponible. Instala: pkg install termux-api"
    except Exception as e:
        return f"Error obteniendo batería: {e}"


def wifi(action: str = 'status') -> str:
    """
    Controla y muestra información de WiFi.
    
    Args:
        action: 'status', 'on', 'off', 'info'
    
    Returns:
        Información o resultado de la acción
    """
    action = action.lower()
    
    if action == 'status':
        try:
            result = subprocess.run(
                ['termux-wifi-connectioninfo'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                
                if info.get('ssid'):
                    lines = []
                    lines.append("📶 INFORMACIÓN WiFi")
                    lines.append("═" * 30)
                    lines.append(f"SSID: {info.get('ssid', 'N/A')}")
                    lines.append(f"BSSID: {info.get('bssid', 'N/A')}")
                    lines.append(f"RSSI: {info.get('rssi', 'N/A')} dBm")
                    lines.append(f"Frecuencia: {info.get('frequency_mhz', 'N/A')} MHz")
                    lines.append(f"Velocidad: {info.get('link_speed_mbps', 'N/A')} Mbps")
                    lines.append(f"IP: {info.get('ip', 'N/A')}")
                    lines.append(f"Máscara: {info.get('netmask', 'N/A')}")
                    return "\n".join(lines)
                else:
                    return "No conectado a ninguna red WiFi."
            else:
                return "Error obteniendo información WiFi."
                
        except FileNotFoundError:
            return "termux-wifi-connectioninfo no disponible."
        except Exception as e:
            return f"Error: {e}"
    
    elif action in ['on', 'off']:
        try:
            cmd = 'enable' if action == 'on' else 'disable'
            result = subprocess.run(
                ['termux-wifi-enable', cmd],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return f"✓ WiFi {'encendido' if action == 'on' else 'apagado'}"
            else:
                return f"Error: {result.stderr}"
                
        except FileNotFoundError:
            return "termux-wifi-enable no disponible."
        except Exception as e:
            return f"Error: {e}"
    
    elif action == 'info':
        try:
            result = subprocess.run(
                ['termux-wifi-scaninfo'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                import json
                networks = json.loads(result.stdout)
                
                if networks:
                    lines = []
                    lines.append("📶 REDES WiFi DISPONIBLES")
                    lines.append("═" * 40)
                    
                    for net in networks[:10]:  # Mostrar solo las 10 primeras
                        ssid = net.get('ssid', 'Desconocida')
                        rssi = net.get('rssi', 'N/A')
                        freq = net.get('frequency_mhz', 'N/A')
                        lines.append(f"  • {ssid} ({rssi} dBm, {freq} MHz)")
                    
                    return "\n".join(lines)
                else:
                    return "No se encontraron redes WiFi."
            else:
                return "Error escaneando redes."
                
        except FileNotFoundError:
            return "termux-wifi-scaninfo no disponible."
        except Exception as e:
            return f"Error: {e}"
    
    return f"Acción desconocida: {action}. Usa: status, on, off, info"


def clipboard(action: str = 'get', text: str = None) -> str:
    """
    Gestiona el portapapeles.
    
    Args:
        action: 'get' (obtener) o 'set' (establecer)
        text: Texto a copiar (solo para 'set')
    
    Returns:
        Contenido del portapapeles o confirmación
    """
    if action == 'get':
        try:
            result = subprocess.run(
                ['termux-clipboard-get'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                content = result.stdout
                if content:
                    return f"📋 Contenido del portapapeles:\n{content}"
                else:
                    return "El portapapeles está vacío."
            else:
                return "Error leyendo portapapeles."
                
        except FileNotFoundError:
            return "termux-clipboard-get no disponible."
        except Exception as e:
            return f"Error: {e}"
    
    elif action == 'set':
        if text is None:
            return "Error: Debes proporcionar texto para copiar."
        
        try:
            result = subprocess.run(
                ['termux-clipboard-set'],
                input=text,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return f"✓ Copiado al portapapeles: {text[:50]}..."
            else:
                return f"Error: {result.stderr}"
                
        except FileNotFoundError:
            return "termux-clipboard-set no disponible."
        except Exception as e:
            return f"Error: {e}"
    
    return f"Acción desconocida: {action}. Usa: get, set"


def torch(state: str = 'toggle') -> str:
    """
    Controla la linterna.
    
    Args:
        state: 'on', 'off', o 'toggle'
    
    Returns:
        Confirmación del estado
    """
    try:
        result = subprocess.run(
            ['termux-torch', state],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return f"✓ Linterna {state}"
        else:
            return f"Error: {result.stderr}"
            
    except FileNotFoundError:
        return "termux-torch no disponible. Instala: pkg install termux-api"
    except Exception as e:
        return f"Error: {e}"


def vibrate(duration: str = '300') -> str:
    """
    Hace vibrar el dispositivo.
    
    Args:
        duration: Duración en milisegundos (default: 300)
    
    Returns:
        Confirmación
    """
    try:
        result = subprocess.run(
            ['termux-vibrate', '-d', duration, '-f'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return f"✓ Vibración ({duration}ms)"
        else:
            return f"Error: {result.stderr}"
            
    except FileNotFoundError:
        return "termux-vibrate no disponible."
    except Exception as e:
        return f"Error: {e}"


def share(text: str) -> str:
    """
    Comparte texto con otras aplicaciones.
    
    Args:
        text: Texto a compartir
    
    Returns:
        Confirmación
    """
    try:
        result = subprocess.run(
            ['termux-share', '-a', 'send', text],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return "✓ Diálogo de compartir abierto"
        else:
            return f"Error: {result.stderr}"
            
    except FileNotFoundError:
        return "termux-share no disponible. Instala: pkg install termux-api"
    except Exception as e:
        return f"Error: {e}"


def open_url(url: str) -> str:
    """
    Abre una URL en el navegador.
    
    Args:
        url: URL a abrir
    
    Returns:
        Confirmación
    """
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        result = subprocess.run(
            ['termux-open-url', url],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return f"✓ Abriendo: {url}"
        else:
            return f"Error: {result.stderr}"
            
    except FileNotFoundError:
        return "termux-open-url no disponible."
    except Exception as e:
        return f"Error: {e}"


# Definición de comandos exportados
COMMANDS = {
    'sysinfo': sysinfo,
    'battery': battery,
    'wifi': wifi,
    'clipboard': clipboard,
    'torch': torch,
    'vibrate': vibrate,
    'share': share,
    'open_url': open_url,
}


# Información del skill
SKILL_INFO = {
    'name': 'Sistema',
    'description': 'Utilidades del sistema Android/Termux',
    'version': '1.0',
    'author': 'Gemma Termux App',
    'commands': list(COMMANDS.keys()),
    'requirements': ['termux-api (opcional)']
}


def info():
    """Retorna información del skill"""
    return SKILL_INFO
