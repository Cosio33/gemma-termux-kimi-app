#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill: Calculadora Avanzada
Proporciona funciones matemáticas y de cálculo
"""

import math
import json
from typing import Any


def calc(expression: str) -> str:
    """
    Evalúa una expresión matemática de forma segura.
    
    Args:
        expression: Expresión matemática (ej: "2 + 2", "sqrt(16)", "sin(pi/2)")
    
    Returns:
        Resultado del cálculo
    """
    # Limpiar la expresión
    expression = expression.strip()
    
    # Diccionario de funciones y constantes permitidas
    safe_dict = {
        'abs': abs,
        'round': round,
        'max': max,
        'min': min,
        'sum': sum,
        'pow': pow,
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'sinh': math.sinh,
        'cosh': math.cosh,
        'tanh': math.tanh,
        'log': math.log,
        'log10': math.log10,
        'log2': math.log2,
        'exp': math.exp,
        'ceil': math.ceil,
        'floor': math.floor,
        'factorial': math.factorial,
        'gcd': math.gcd,
        'pi': math.pi,
        'e': math.e,
        'tau': math.tau,
        'inf': math.inf,
        'nan': math.nan,
        'degrees': math.degrees,
        'radians': math.radians,
    }
    
    try:
        # Evaluar la expresión
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        
        # Formatear resultado
        if isinstance(result, float):
            if result.is_integer():
                return f"= {int(result)}"
            return f"= {result:.10f}".rstrip('0').rstrip('.')
        
        return f"= {result}"
        
    except ZeroDivisionError:
        return "Error: División por cero"
    except Exception as e:
        return f"Error en la expresión: {e}"


def convert(value: str, from_unit: str, to_unit: str) -> str:
    """
    Convierte entre diferentes unidades.
    
    Args:
        value: Valor numérico
        from_unit: Unidad de origen
        to_unit: Unidad de destino
    
    Returns:
        Resultado de la conversión
    """
    try:
        val = float(value)
    except ValueError:
        return "Error: El valor debe ser un número"
    
    # Factores de conversión
    conversions = {
        # Longitud
        ('m', 'km'): 0.001,
        ('km', 'm'): 1000,
        ('m', 'cm'): 100,
        ('cm', 'm'): 0.01,
        ('m', 'mm'): 1000,
        ('mm', 'm'): 0.001,
        ('cm', 'mm'): 10,
        ('mm', 'cm'): 0.1,
        ('km', 'mi'): 0.621371,
        ('mi', 'km'): 1.60934,
        ('m', 'ft'): 3.28084,
        ('ft', 'm'): 0.3048,
        ('m', 'in'): 39.3701,
        ('in', 'm'): 0.0254,
        
        # Masa
        ('kg', 'g'): 1000,
        ('g', 'kg'): 0.001,
        ('kg', 'lb'): 2.20462,
        ('lb', 'kg'): 0.453592,
        ('g', 'oz'): 0.035274,
        ('oz', 'g'): 28.3495,
        
        # Temperatura
        ('c', 'f'): 'temp',
        ('f', 'c'): 'temp',
        ('c', 'k'): 'temp',
        ('k', 'c'): 'temp',
        ('f', 'k'): 'temp',
        ('k', 'f'): 'temp',
        
        # Volumen
        ('l', 'ml'): 1000,
        ('ml', 'l'): 0.001,
        ('l', 'gal'): 0.264172,
        ('gal', 'l'): 3.78541,
        
        # Tiempo
        ('s', 'min'): 1/60,
        ('min', 's'): 60,
        ('min', 'h'): 1/60,
        ('h', 'min'): 60,
        ('h', 'd'): 1/24,
        ('d', 'h'): 24,
        
        # Datos
        ('b', 'kb'): 1/1024,
        ('kb', 'b'): 1024,
        ('kb', 'mb'): 1/1024,
        ('mb', 'kb'): 1024,
        ('mb', 'gb'): 1/1024,
        ('gb', 'mb'): 1024,
        ('gb', 'tb'): 1/1024,
        ('tb', 'gb'): 1024,
    }
    
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    if (from_unit, to_unit) not in conversions:
        return f"Conversión no soportada: {from_unit} → {to_unit}"
    
    factor = conversions[(from_unit, to_unit)]
    
    # Manejar conversiones de temperatura
    if factor == 'temp':
        if from_unit == 'c' and to_unit == 'f':
            result = (val * 9/5) + 32
        elif from_unit == 'f' and to_unit == 'c':
            result = (val - 32) * 5/9
        elif from_unit == 'c' and to_unit == 'k':
            result = val + 273.15
        elif from_unit == 'k' and to_unit == 'c':
            result = val - 273.15
        elif from_unit == 'f' and to_unit == 'k':
            result = (val - 32) * 5/9 + 273.15
        elif from_unit == 'k' and to_unit == 'f':
            result = (val - 273.15) * 9/5 + 32
    else:
        result = val * factor
    
    return f"{val} {from_unit} = {result:.6g} {to_unit}"


def base(number: str, from_base: int, to_base: int) -> str:
    """
    Convierte números entre diferentes bases.
    
    Args:
        number: Número en la base de origen
        from_base: Base de origen (2-36)
        to_base: Base de destino (2-36)
    
    Returns:
        Número convertido
    """
    try:
        # Convertir a decimal primero
        decimal = int(str(number), from_base)
        
        # Convertir de decimal a base destino
        if to_base == 10:
            return str(decimal)
        elif to_base == 2:
            return bin(decimal)
        elif to_base == 8:
            return oct(decimal)
        elif to_base == 16:
            return hex(decimal)
        else:
            # Conversión a cualquier base
            digits = "0123456789abcdefghijklmnopqrstuvwxyz"
            result = ""
            while decimal > 0:
                result = digits[decimal % to_base] + result
                decimal //= to_base
            return result if result else "0"
            
    except ValueError as e:
        return f"Error: {e}"


# Definición de comandos exportados
COMMANDS = {
    'calc': calc,
    'convert': convert,
    'base': base,
}


# Información del skill
SKILL_INFO = {
    'name': 'Calculadora',
    'description': 'Funciones matemáticas y de conversión',
    'version': '1.0',
    'author': 'Gemma Termux App',
    'commands': list(COMMANDS.keys())
}


def info():
    """Retorna información del skill"""
    return SKILL_INFO
