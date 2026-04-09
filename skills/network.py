#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill: Utilidades de Red
Proporciona herramientas de red y conectividad
"""

import socket
import subprocess
import urllib.request
import json
from typing import Any


def ping(host: str, count: str = '4') -> str:
    """
    Realiza ping a un host.
    
    Args:
        host: Host a hacer ping
        count: Número de paquetes
    
    Returns:
        Resultado del ping
    """
    try:
        result = subprocess.run(
            ['ping', '-c', count, host],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Extraer resumen
        output = result.stdout
        lines = output.split('\n')
        
        summary = []
        for line in lines:
            if 'packets transmitted' in line or 'packet loss' in line:
                summary.append(line)
            if 'round-trip' in line or 'rtt' in line:
                summary.append(line)
        
        if summary:
            return "\n".join(summary)
        else:
            return output[:500]  # Retornar primeros 500 caracteres
            
    except subprocess.TimeoutExpired:
        return "Timeout: El ping tardó demasiado."
    except Exception as e:
        return f"Error: {e}"


def resolve(domain: str) -> str:
    """
    Resuelve un dominio a direcciones IP.
    
    Args:
        domain: Dominio a resolver
    
    Returns:
        Direcciones IP asociadas
    """
    try:
        # Obtener información del host
        addr_info = socket.getaddrinfo(domain, None)
        
        ips = set()
        for info in addr_info:
            ip = info[4][0]
            ips.add(ip)
        
        if ips:
            result = [f"Direcciones IP para {domain}:"]
            for ip in sorted(ips):
                result.append(f"  • {ip}")
            return "\n".join(result)
        else:
            return f"No se encontraron direcciones IP para {domain}"
            
    except socket.gaierror as e:
        return f"Error resolviendo {domain}: {e}"
    except Exception as e:
        return f"Error: {e}"


def myip() -> str:
    """
    Obtiene la dirección IP pública.
    
    Returns:
        IP pública e información relacionada
    """
    services = [
        'https://api.ipify.org?format=json',
        'https://httpbin.org/ip',
        'https://api.myip.com',
    ]
    
    for service in services:
        try:
            with urllib.request.urlopen(service, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                if 'ip' in data:
                    ip = data['ip']
                elif 'origin' in data:
                    ip = data['origin']
                else:
                    continue
                
                result = []
                result.append(f"🌐 Tu IP Pública: {ip}")
                
                if 'country' in data:
                    result.append(f"País: {data['country']}")
                if 'city' in data:
                    result.append(f"Ciudad: {data['city']}")
                if 'isp' in data:
                    result.append(f"ISP: {data['isp']}")
                
                return "\n".join(result)
                
        except Exception:
            continue
    
    return "No se pudo obtener la IP pública."


def localip() -> str:
    """
    Obtiene las direcciones IP locales.
    
    Returns:
        IPs locales del dispositivo
    """
    try:
        # Obtener hostname
        hostname = socket.gethostname()
        
        # Intentar obtener IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
        finally:
            s.close()
        
        result = []
        result.append("📡 INTERFACES DE RED LOCALES")
        result.append("═" * 40)
        result.append(f"Hostname: {hostname}")
        result.append(f"IP Local: {local_ip}")
        
        # Intentar obtener más información con ifconfig o ip
        try:
            ifconfig_result = subprocess.run(
                ['ifconfig'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if ifconfig_result.returncode == 0:
                result.append("")
                result.append("Interfaces:")
                # Extraer interfaces
                for line in ifconfig_result.stdout.split('\n'):
                    if line and not line.startswith(' '):
                        result.append(f"  {line.split(':')[0]}")
        except:
            pass
        
        return "\n".join(result)
        
    except Exception as e:
        return f"Error obteniendo IP local: {e}"


def port_check(host: str, port: str) -> str:
    """
    Verifica si un puerto está abierto.
    
    Args:
        host: Host a verificar
        port: Puerto a verificar
    
    Returns:
        Estado del puerto
    """
    try:
        port_num = int(port)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        result = sock.connect_ex((host, port_num))
        sock.close()
        
        if result == 0:
            return f"✓ Puerto {port} en {host} está ABIERTO"
        else:
            return f"✗ Puerto {port} en {host} está CERRADO"
            
    except ValueError:
        return "Error: El puerto debe ser un número."
    except socket.gaierror:
        return f"Error: No se pudo resolver {host}"
    except Exception as e:
        return f"Error: {e}"


def whois(domain: str) -> str:
    """
    Realiza consulta WHOIS básica.
    
    Args:
        domain: Dominio a consultar
    
    Returns:
        Información WHOIS
    """
    try:
        result = subprocess.run(
            ['whois', domain],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            output = result.stdout
            
            # Extraer información relevante
            lines = output.split('\n')
            relevant = []
            
            for line in lines:
                if any(keyword in line.lower() for keyword in [
                    'domain name', 'registrar', 'creation date', 'expiration date',
                    'name server', 'status', 'registrant', 'admin', 'tech'
                ]):
                    if not line.startswith('%') and not line.startswith('#'):
                        relevant.append(line.strip())
            
            if relevant:
                return "\n".join(relevant[:30])  # Limitar a 30 líneas
            else:
                return output[:1000]  # Retornar primeros 1000 caracteres
        else:
            return f"Error: {result.stderr}"
            
    except FileNotFoundError:
        return "whois no instalado. Instala: pkg install whois"
    except subprocess.TimeoutExpired:
        return "Timeout: La consulta WHOIS tardó demasiado."
    except Exception as e:
        return f"Error: {e}"


def curl(url: str, method: str = 'GET', data: str = None) -> str:
    """
    Realiza peticiones HTTP.
    
    Args:
        url: URL a consultar
        method: Método HTTP (GET, POST, etc.)
        data: Datos a enviar (para POST)
    
    Returns:
        Respuesta HTTP
    """
    try:
        cmd = ['curl', '-s', '-w', '\n---\nHTTP Code: %{http_code}\nTime: %{time_total}s\nSize: %{size_download}bytes']
        
        if method.upper() != 'GET':
            cmd.extend(['-X', method.upper()])
        
        if data:
            cmd.extend(['-d', data])
        
        cmd.extend(['-L', '--max-time', '30', url])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=35
        )
        
        if result.returncode == 0:
            # Limitar output
            output = result.stdout
            if len(output) > 3000:
                output = output[:3000] + "\n... (truncado)"
            return output
        else:
            return f"Error: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "Timeout: La petición tardó demasiado."
    except Exception as e:
        return f"Error: {e}"


def scan_ports(host: str, start_port: str = '1', end_port: str = '100') -> str:
    """
    Escanea puertos en un host.
    
    Args:
        host: Host a escanear
        start_port: Puerto inicial
        end_port: Puerto final
    
    Returns:
        Puertos abiertos encontrados
    """
    try:
        start = int(start_port)
        end = int(end_port)
        
        if end - start > 100:
            return "Error: Rango máximo de 100 puertos."
        
        open_ports = []
        
        for port in range(start, end + 1):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                # Intentar identificar servicio
                service = socket.getservbyport(port, 'tcp') if port < 1024 else 'unknown'
                open_ports.append((port, service))
        
        if open_ports:
            result = [f"Puertos abiertos en {host}:"]
            for port, service in open_ports:
                result.append(f"  {port}/tcp - {service}")
            return "\n".join(result)
        else:
            return f"No se encontraron puertos abiertos en {host} ({start}-{end})"
            
    except ValueError:
        return "Error: Los puertos deben ser números."
    except socket.gaierror:
        return f"Error: No se pudo resolver {host}"
    except Exception as e:
        return f"Error: {e}"


# Definición de comandos exportados
COMMANDS = {
    'ping': ping,
    'resolve': resolve,
    'myip': myip,
    'localip': localip,
    'port_check': port_check,
    'whois': whois,
    'curl': curl,
    'scan_ports': scan_ports,
}


# Información del skill
SKILL_INFO = {
    'name': 'Network',
    'description': 'Utilidades de red y conectividad',
    'version': '1.0',
    'author': 'Gemma Termux App',
    'commands': list(COMMANDS.keys())
}


def info():
    """Retorna información del skill"""
    return SKILL_INFO
