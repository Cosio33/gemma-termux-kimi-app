#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill: Utilidades de Código
Proporciona herramientas para trabajar con código
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Any, List


def analyze_code(code: str, language: str = 'python') -> str:
    """
    Analiza código y proporciona información.
    
    Args:
        code: Código a analizar (o ruta al archivo)
        language: Lenguaje de programación
    
    Returns:
        Análisis del código
    """
    # Si es una ruta, leer el archivo
    if os.path.exists(code):
        try:
            with open(code, 'r', encoding='utf-8') as f:
                code = f.read()
            language = Path(code).suffix.lstrip('.')
        except Exception as e:
            return f"Error leyendo archivo: {e}"
    
    lines = code.split('\n')
    total_lines = len(lines)
    non_empty_lines = len([l for l in lines if l.strip()])
    
    analysis = []
    analysis.append("═" * 50)
    analysis.append("ANÁLISIS DE CÓDIGO")
    analysis.append("═" * 50)
    analysis.append(f"Lenguaje: {language}")
    analysis.append(f"Líneas totales: {total_lines}")
    analysis.append(f"Líneas no vacías: {non_empty_lines}")
    
    if language == 'python':
        # Análisis específico de Python
        try:
            tree = ast.parse(code)
            
            # Contar definiciones
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            
            analysis.append("")
            analysis.append("ESTRUCTURA:")
            analysis.append(f"  Funciones: {len(functions)}")
            analysis.append(f"  Clases: {len(classes)}")
            analysis.append(f"  Imports: {len(imports)}")
            
            if functions:
                analysis.append("")
                analysis.append("FUNCIONES:")
                for func in functions[:10]:  # Mostrar solo las primeras 10
                    args = [arg.arg for arg in func.args.args]
                    analysis.append(f"  • {func.name}({', '.join(args)})")
                if len(functions) > 10:
                    analysis.append(f"  ... y {len(functions) - 10} más")
            
            if classes:
                analysis.append("")
                analysis.append("CLASES:")
                for cls in classes:
                    methods = [node.name for node in ast.walk(cls) if isinstance(node, ast.FunctionDef)]
                    analysis.append(f"  • {cls.name} ({len(methods)} métodos)")
            
            # Buscar TODOs
            todos = []
            for i, line in enumerate(lines, 1):
                if 'TODO' in line or 'FIXME' in line or 'XXX' in line:
                    todos.append(f"  Línea {i}: {line.strip()}")
            
            if todos:
                analysis.append("")
                analysis.append("TAREAS PENDIENTES:")
                analysis.extend(todos[:5])
                if len(todos) > 5:
                    analysis.append(f"  ... y {len(todos) - 5} más")
                    
        except SyntaxError as e:
            analysis.append(f"\n⚠ Error de sintaxis: {e}")
    
    analysis.append("═" * 50)
    
    return "\n".join(analysis)


def format_code(code: str, language: str = 'python') -> str:
    """
    Formatea código (aplica indentación básica).
    
    Args:
        code: Código a formatear
        language: Lenguaje de programación
    
    Returns:
        Código formateado
    """
    lines = code.split('\n')
    formatted = []
    indent_level = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Reducir indentación si la línea cierra un bloque
        if stripped.startswith(('}', ']', ')', 'end', 'fi', 'done', 'esac')):
            indent_level = max(0, indent_level - 1)
        
        # Añadir línea con indentación
        if stripped:
            formatted.append('    ' * indent_level + stripped)
        else:
            formatted.append('')
        
        # Aumentar indentación si la línea abre un bloque
        if stripped.endswith(('{', '[', '(', ':')) or stripped.startswith(('if ', 'for ', 'while ', 'def ', 'class ', 'try:', 'except', 'else:', 'elif ')):
            if not stripped.endswith('pass') and not stripped.startswith('return'):
                indent_level += 1
    
    return '\n'.join(formatted)


def minify_code(code: str, language: str = 'python') -> str:
    """
    Minifica código eliminando comentarios y espacios innecesarios.
    
    Args:
        code: Código a minificar
        language: Lenguaje de programación
    
    Returns:
        Código minificado
    """
    lines = code.split('\n')
    minified_lines = []
    
    for line in lines:
        # Remover comentarios
        if language in ['python', 'py']:
            if '#' in line:
                line = line[:line.index('#')]
        elif language in ['javascript', 'js', 'typescript', 'ts', 'java', 'c', 'cpp', 'cxx']:
            if '//' in line:
                line = line[:line.index('//')]
        
        stripped = line.strip()
        if stripped:
            minified_lines.append(stripped)
    
    return ' '.join(minified_lines)


def count_lines(path: str, pattern: str = '*') -> str:
    """
    Cuenta líneas de código en archivos.
    
    Args:
        path: Ruta al directorio o archivo
        pattern: Patrón de archivos (ej: '*.py')
    
    Returns:
        Estadísticas de líneas
    """
    target_path = Path(path)
    
    if not target_path.exists():
        return f"Ruta no encontrada: {path}"
    
    stats = {
        'total_files': 0,
        'total_lines': 0,
        'code_lines': 0,
        'blank_lines': 0,
        'comment_lines': 0,
        'by_extension': {}
    }
    
    if target_path.is_file():
        files = [target_path]
    else:
        files = list(target_path.rglob(pattern))
    
    for file_path in files:
        if not file_path.is_file():
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                ext = file_path.suffix.lstrip('.') or 'no_extension'
                
                if ext not in stats['by_extension']:
                    stats['by_extension'][ext] = {
                        'files': 0,
                        'lines': 0
                    }
                
                stats['by_extension'][ext]['files'] += 1
                stats['by_extension'][ext]['lines'] += len(lines)
                
                stats['total_files'] += 1
                stats['total_lines'] += len(lines)
                
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        stats['blank_lines'] += 1
                    elif stripped.startswith('#') or stripped.startswith('//'):
                        stats['comment_lines'] += 1
                    else:
                        stats['code_lines'] += 1
                        
        except Exception as e:
            continue
    
    # Generar reporte
    report = []
    report.append("═" * 50)
    report.append("ESTADÍSTICAS DE LÍNEAS DE CÓDIGO")
    report.append("═" * 50)
    report.append(f"Archivos analizados: {stats['total_files']}")
    report.append(f"Líneas totales: {stats['total_lines']:,}")
    report.append(f"Líneas de código: {stats['code_lines']:,}")
    report.append(f"Líneas en blanco: {stats['blank_lines']:,}")
    report.append(f"Líneas de comentarios: {stats['comment_lines']:,}")
    
    if stats['total_lines'] > 0:
        code_percent = (stats['code_lines'] / stats['total_lines']) * 100
        report.append(f"Porcentaje código: {code_percent:.1f}%")
    
    if stats['by_extension']:
        report.append("")
        report.append("POR EXTENSIÓN:")
        for ext, data in sorted(stats['by_extension'].items(), key=lambda x: -x[1]['lines']):
            report.append(f"  .{ext}: {data['files']} archivos, {data['lines']:,} líneas")
    
    report.append("═" * 50)
    
    return "\n".join(report)


def find_functions(code: str, name_pattern: str = None) -> str:
    """
    Encuentra funciones en código Python.
    
    Args:
        code: Código Python o ruta al archivo
        name_pattern: Patrón de nombre a buscar (opcional)
    
    Returns:
        Lista de funciones encontradas
    """
    # Si es una ruta, leer el archivo
    if os.path.exists(code):
        try:
            with open(code, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            return f"Error leyendo archivo: {e}"
    
    try:
        tree = ast.parse(code)
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if name_pattern is None or name_pattern.lower() in node.name.lower():
                    # Obtener docstring
                    docstring = ast.get_docstring(node)
                    
                    # Obtener argumentos
                    args = [arg.arg for arg in node.args.args]
                    
                    # Obtener línea
                    line_num = node.lineno
                    
                    functions.append({
                        'name': node.name,
                        'args': args,
                        'line': line_num,
                        'docstring': docstring[:100] + '...' if docstring and len(docstring) > 100 else docstring
                    })
        
        if not functions:
            return "No se encontraron funciones."
        
        result = []
        result.append(f"FUNCIONES ENCONTRADAS ({len(functions)}):")
        result.append("═" * 50)
        
        for func in functions:
            result.append(f"\n{func['name']}({', '.join(func['args'])})")
            result.append(f"  Línea: {func['line']}")
            if func['docstring']:
                result.append(f"  Doc: {func['docstring']}")
        
        return "\n".join(result)
        
    except SyntaxError as e:
        return f"Error de sintaxis: {e}"


def generate_docstring(code: str) -> str:
    """
    Genera un docstring básico para una función Python.
    
    Args:
        code: Código de la función
    
    Returns:
        Docstring generado
    """
    try:
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                args = [arg.arg for arg in node.args.args]
                
                docstring = f'"""\n'
                docstring += f'{func_name}\n\n'
                
                if args:
                    docstring += 'Args:\n'
                    for arg in args:
                        docstring += f'    {arg}: Descripción\n'
                    docstring += '\n'
                
                docstring += 'Returns:\n'
                docstring += '    Descripción del retorno\n'
                docstring += '"""'
                
                return docstring
        
        return "No se encontró ninguna función en el código."
        
    except SyntaxError as e:
        return f"Error de sintaxis: {e}"


# Definición de comandos exportados
COMMANDS = {
    'analyze_code': analyze_code,
    'format_code': format_code,
    'minify_code': minify_code,
    'count_lines': count_lines,
    'find_functions': find_functions,
    'generate_docstring': generate_docstring,
}


# Información del skill
SKILL_INFO = {
    'name': 'Code Utils',
    'description': 'Utilidades para análisis y manipulación de código',
    'version': '1.0',
    'author': 'Gemma Termux App',
    'commands': list(COMMANDS.keys())
}


def info():
    """Retorna información del skill"""
    return SKILL_INFO
