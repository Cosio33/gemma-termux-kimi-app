#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemma Termux App - Asistente IA Local con Skills y Memoria Persistente
Implementación nativa del modelo Gemma 4-E2B-it para Termux/Android
"""

import os
import sys
import json
import sqlite3
import argparse
import importlib.util
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, asdict
import readline
import threading
import time

# Configuración de paths
BASE_DIR = Path(__file__).parent.parent.absolute()
CONFIG_DIR = BASE_DIR / "config"
SKILLS_DIR = BASE_DIR / "skills"
SANDBOX_DIR = BASE_DIR / "sandbox"
MODELS_DIR = BASE_DIR / "models"
DB_PATH = BASE_DIR / "memory.db"

# Asegurar que existan los directorios
SANDBOX_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)


@dataclass
class Message:
    """Representa un mensaje en la conversación"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: str = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


class DatabaseManager:
    """Gestiona la memoria persistente usando SQLite"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa las tablas de la base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabla de conversaciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            ''')
            
            # Tabla de memoria a largo plazo (hechos importantes)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS long_term_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    importance INTEGER DEFAULT 5,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Tabla de configuración
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Tabla de estadísticas de uso
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usage_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    tokens_input INTEGER DEFAULT 0,
                    tokens_output INTEGER DEFAULT 0,
                    requests INTEGER DEFAULT 0,
                    UNIQUE(date)
                )
            ''')
            
            conn.commit()
    
    def save_message(self, session_id: str, message: Message):
        """Guarda un mensaje en la base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversations (session_id, role, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                session_id,
                message.role,
                message.content,
                message.timestamp,
                json.dumps(message.metadata) if message.metadata else '{}'
            ))
            conn.commit()
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Message]:
        """Obtiene el historial de conversación"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role, content, timestamp, metadata FROM conversations
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (session_id, limit))
            
            messages = []
            for row in cursor.fetchall():
                messages.append(Message(
                    role=row[0],
                    content=row[1],
                    timestamp=row[2],
                    metadata=json.loads(row[3]) if row[3] else {}
                ))
            return list(reversed(messages))
    
    def save_memory(self, key: str, value: str, category: str = 'general', importance: int = 5):
        """Guarda un recuerdo en memoria a largo plazo"""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO long_term_memory (key, value, category, importance, created_at, updated_at)
                VALUES (?, ?, ?, ?, COALESCE((SELECT created_at FROM long_term_memory WHERE key = ?), ?), ?)
            ''', (key, value, category, importance, key, now, now))
            conn.commit()
    
    def get_memory(self, key: str) -> Optional[str]:
        """Obtiene un recuerdo por clave"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM long_term_memory WHERE key = ?', (key,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def search_memories(self, query: str, category: str = None, limit: int = 10) -> List[Dict]:
        """Busca recuerdos por contenido"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute('''
                    SELECT key, value, category, importance, updated_at FROM long_term_memory
                    WHERE (key LIKE ? OR value LIKE ?) AND category = ?
                    ORDER BY importance DESC, updated_at DESC
                    LIMIT ?
                ''', (f'%{query}%', f'%{query}%', category, limit))
            else:
                cursor.execute('''
                    SELECT key, value, category, importance, updated_at FROM long_term_memory
                    WHERE key LIKE ? OR value LIKE ?
                    ORDER BY importance DESC, updated_at DESC
                    LIMIT ?
                ''', (f'%{query}%', f'%{query}%', limit))
            
            return [
                {
                    'key': row[0],
                    'value': row[1],
                    'category': row[2],
                    'importance': row[3],
                    'updated_at': row[4]
                }
                for row in cursor.fetchall()
            ]
    
    def get_all_memories(self, category: str = None) -> List[Dict]:
        """Obtiene todos los recuerdos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute('''
                    SELECT key, value, category, importance, updated_at FROM long_term_memory
                    WHERE category = ?
                    ORDER BY updated_at DESC
                ''', (category,))
            else:
                cursor.execute('''
                    SELECT key, value, category, importance, updated_at FROM long_term_memory
                    ORDER BY updated_at DESC
                ''')
            
            return [
                {
                    'key': row[0],
                    'value': row[1],
                    'category': row[2],
                    'importance': row[3],
                    'updated_at': row[4]
                }
                for row in cursor.fetchall()
            ]
    
    def delete_memory(self, key: str):
        """Elimina un recuerdo"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM long_term_memory WHERE key = ?', (key,))
            conn.commit()
    
    def update_stats(self, tokens_input: int = 0, tokens_output: int = 0):
        """Actualiza estadísticas de uso"""
        today = datetime.now().strftime('%Y-%m-%d')
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO usage_stats (date, tokens_input, tokens_output, requests)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(date) DO UPDATE SET
                    tokens_input = tokens_input + ?,
                    tokens_output = tokens_output + ?,
                    requests = requests + 1
            ''', (today, tokens_input, tokens_output, tokens_input, tokens_output))
            conn.commit()
    
    def get_setting(self, key: str, default: str = None) -> str:
        """Obtiene una configuración"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            result = cursor.fetchone()
            return result[0] if result else default
    
    def set_setting(self, key: str, value: str):
        """Guarda una configuración"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, value, datetime.now().isoformat()))
            conn.commit()


class SkillManager:
    """Gestiona la carga y ejecución de skills"""
    
    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.skills: Dict[str, Any] = {}
        self.commands: Dict[str, Callable] = {}
        self.load_all_skills()
    
    def load_all_skills(self):
        """Carga todos los skills del directorio"""
        if not self.skills_dir.exists():
            return
        
        for skill_file in self.skills_dir.glob('*.py'):
            if skill_file.name.startswith('_'):
                continue
            self.load_skill(skill_file)
    
    def load_skill(self, skill_path: Path):
        """Carga un skill individual"""
        try:
            spec = importlib.util.spec_from_file_location(
                skill_path.stem,
                skill_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            skill_name = skill_path.stem
            self.skills[skill_name] = module
            
            # Registrar comandos si el skill los expone
            if hasattr(module, 'COMMANDS'):
                for cmd_name, cmd_func in module.COMMANDS.items():
                    self.commands[cmd_name] = cmd_func
            
            print(f"✓ Skill cargado: {skill_name}")
            
        except Exception as e:
            print(f"✗ Error cargando skill {skill_path.name}: {e}")
    
    def execute_command(self, command: str, *args, **kwargs) -> Any:
        """Ejecuta un comando de skill"""
        if command in self.commands:
            try:
                return self.commands[command](*args, **kwargs)
            except Exception as e:
                return f"Error ejecutando '{command}': {e}"
        return None
    
    def get_available_commands(self) -> List[str]:
        """Retorna lista de comandos disponibles"""
        return list(self.commands.keys())
    
    def reload_skills(self):
        """Recarga todos los skills"""
        self.skills.clear()
        self.commands.clear()
        self.load_all_skills()


class SandboxManager:
    """Gestiona operaciones en el sandbox de archivos"""
    
    def __init__(self, sandbox_dir: Path):
        self.sandbox_dir = sandbox_dir
        self.sandbox_dir.mkdir(exist_ok=True)
    
    def _resolve_path(self, path: str) -> Path:
        """Resuelve y valida una ruta dentro del sandbox"""
        resolved = (self.sandbox_dir / path).resolve()
        # Asegurar que la ruta está dentro del sandbox
        try:
            resolved.relative_to(self.sandbox_dir.resolve())
        except ValueError:
            raise ValueError(f"Ruta fuera del sandbox: {path}")
        return resolved
    
    def create_file(self, path: str, content: str = "") -> str:
        """Crea un archivo en el sandbox"""
        try:
            file_path = self._resolve_path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            return f"✓ Archivo creado: {path}"
        except Exception as e:
            return f"✗ Error creando archivo: {e}"
    
    def read_file(self, path: str) -> str:
        """Lee un archivo del sandbox"""
        try:
            file_path = self._resolve_path(path)
            if not file_path.exists():
                return f"✗ Archivo no encontrado: {path}"
            return file_path.read_text(encoding='utf-8')
        except Exception as e:
            return f"✗ Error leyendo archivo: {e}"
    
    def write_file(self, path: str, content: str) -> str:
        """Escribe contenido a un archivo"""
        try:
            file_path = self._resolve_path(path)
            if not file_path.exists():
                return f"✗ Archivo no existe. Usa 'create' primero: {path}"
            file_path.write_text(content, encoding='utf-8')
            return f"✓ Archivo actualizado: {path}"
        except Exception as e:
            return f"✗ Error escribiendo archivo: {e}"
    
    def append_file(self, path: str, content: str) -> str:
        """Añade contenido al final de un archivo"""
        try:
            file_path = self._resolve_path(path)
            if not file_path.exists():
                return f"✗ Archivo no encontrado: {path}"
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
            return f"✓ Contenido añadido a: {path}"
        except Exception as e:
            return f"✗ Error añadiendo contenido: {e}"
    
    def delete_file(self, path: str) -> str:
        """Elimina un archivo"""
        try:
            file_path = self._resolve_path(path)
            if not file_path.exists():
                return f"✗ Archivo no encontrado: {path}"
            if file_path.is_dir():
                import shutil
                shutil.rmtree(file_path)
                return f"✓ Directorio eliminado: {path}"
            else:
                file_path.unlink()
                return f"✓ Archivo eliminado: {path}"
        except Exception as e:
            return f"✗ Error eliminando: {e}"
    
    def list_files(self, path: str = ".") -> str:
        """Lista archivos en un directorio"""
        try:
            dir_path = self._resolve_path(path)
            if not dir_path.exists():
                return f"✗ Directorio no encontrado: {path}"
            
            items = []
            for item in sorted(dir_path.iterdir()):
                item_type = "📁" if item.is_dir() else "📄"
                size = ""
                if item.is_file():
                    size_bytes = item.stat().st_size
                    if size_bytes < 1024:
                        size = f" ({size_bytes}B)"
                    elif size_bytes < 1024*1024:
                        size = f" ({size_bytes/1024:.1f}KB)"
                    else:
                        size = f" ({size_bytes/(1024*1024):.1f}MB)"
                items.append(f"{item_type} {item.name}{size}")
            
            return "\n".join(items) if items else "(directorio vacío)"
        except Exception as e:
            return f"✗ Error listando archivos: {e}"
    
    def get_info(self, path: str) -> str:
        """Obtiene información de un archivo"""
        try:
            file_path = self._resolve_path(path)
            if not file_path.exists():
                return f"✗ No encontrado: {path}"
            
            stat = file_path.stat()
            info = [
                f"Nombre: {file_path.name}",
                f"Ruta: {path}",
                f"Tipo: {'Directorio' if file_path.is_dir() else 'Archivo'}",
                f"Tamaño: {stat.st_size} bytes",
                f"Creado: {datetime.fromtimestamp(stat.st_ctime).isoformat()}",
                f"Modificado: {datetime.fromtimestamp(stat.st_mtime).isoformat()}",
            ]
            return "\n".join(info)
        except Exception as e:
            return f"✗ Error obteniendo info: {e}"


class GemmaInference:
    """Gestiona la inferencia del modelo Gemma"""
    
    def __init__(self, models_dir: Path, db: DatabaseManager):
        self.models_dir = models_dir
        self.db = db
        self.model_path = None
        self.llama_cpp_path = None
        self.context_size = 4096
        self.temperature = 0.7
        self.max_tokens = 2048
        
        self.find_model()
        self.find_llama_cpp()
    
    def find_model(self):
        """Busca el modelo Gemma en el directorio"""
        # Buscar archivos de modelo comunes
        patterns = ['*.gguf', '*gemma*.bin', '*gemma*.gguf']
        for pattern in patterns:
            for model_file in self.models_dir.glob(pattern):
                self.model_path = model_file
                print(f"✓ Modelo encontrado: {model_file.name}")
                return
        
        print("⚠ No se encontró modelo Gemma. Colócalo en la carpeta 'models/'")
        print("  Formatos soportados: .gguf, .bin")
    
    def find_llama_cpp(self):
        """Busca la instalación de llama.cpp"""
        import shutil
        
        # Buscar en PATH usando shutil.which (portable, no requiere 'which')
        for cmd in ['llama-cli', 'llama.cpp', 'main']:
            path = shutil.which(cmd)
            if path:
                self.llama_cpp_path = path
                print(f"✓ llama.cpp encontrado: {self.llama_cpp_path}")
                return
        
        # Buscar en directorios comunes de Termux
        termux_paths = [
            '/data/data/com.termux/files/usr/bin/llama-cli',
            '/data/data/com.termux/files/usr/local/bin/llama-cli',
            '/data/data/com.termux/files/usr/bin/main',
        ]
        for path in termux_paths:
            if os.path.exists(path):
                self.llama_cpp_path = path
                print(f"✓ llama.cpp encontrado: {path}")
                return
        
        print("⚠ llama.cpp no encontrado. Instálalo con: pkg install llama-cpp")
    
    def is_available(self) -> bool:
        """Verifica si el sistema de inferencia está listo"""
        return self.model_path is not None and self.llama_cpp_path is not None
    
    def generate(self, prompt: str, system_prompt: str = None, 
                 temperature: float = None, max_tokens: int = None) -> str:
        """Genera una respuesta usando el modelo"""
        if not self.is_available():
            return "Error: Modelo o llama.cpp no disponible."
        
        temp = temperature or self.temperature
        tokens = max_tokens or self.max_tokens
        
        # Construir el prompt completo en formato chat
        full_prompt = self._format_chat_prompt(prompt, system_prompt)
        
        try:
            # Construir comando
            cmd = [
                self.llama_cpp_path,
                '-m', str(self.model_path),
                '-c', str(self.context_size),
                '-n', str(tokens),
                '--temp', str(temp),
                '-p', full_prompt,
                '--no-display-prompt'
            ]
            
            # Ejecutar inferencia
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                # Limpiar respuesta
                response = self._clean_response(response, full_prompt)
                return response
            else:
                error_msg = result.stderr
                
                # Detectar error de arquitectura no soportada
                if 'unknown model architecture' in error_msg.lower() or 'gemma4' in error_msg.lower():
                    return """❌ Error: Tu versión de llama.cpp no soporta Gemma 4

La versión instalada desde 'pkg install llama-cpp' está desactualizada.

🔧 SOLUCIÓN - Compilar llama.cpp desde fuente:

1. Elimina la versión antigua:
   pkg uninstall llama-cpp

2. Instala dependencias de compilación:
   pkg install git cmake clang

3. Clona y compila la última versión:
   cd ~
   git clone --depth 1 https://github.com/ggerganov/llama.cpp.git
   cd llama.cpp
   cmake -B build
   cmake --build build --config Release -j$(nproc)

4. Crea un enlace simbólico:
   ln -s ~/llama.cpp/build/bin/llama-cli $PREFIX/bin/llama-cli

5. Verifica la instalación:
   llama-cli --version

6. Reinicia Gemma Termux App

📚 Más info: https://github.com/ggerganov/llama.cpp#build"""
                
                return f"Error en inferencia: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return "Error: Tiempo de espera agotado (5 minutos)"
        except Exception as e:
            return f"Error generando respuesta: {e}"
    
    def _format_chat_prompt(self, user_message: str, system_prompt: str = None) -> str:
        """Formatea el prompt en formato chat de Gemma"""
        # Formato de chat de Gemma 2/3/4
        if system_prompt:
            prompt = f"<start_of_turn>user\n{system_prompt}\n\n{user_message}<end_of_turn>\n<start_of_turn>model\n"
        else:
            prompt = f"<start_of_turn>user\n{user_message}<end_of_turn>\n<start_of_turn>model\n"
        return prompt
    
    def _clean_response(self, response: str, original_prompt: str) -> str:
        """Limpia la respuesta del modelo"""
        # Remover el prompt original si está presente
        if original_prompt in response:
            response = response.replace(original_prompt, "")
        
        # Remover tokens especiales
        response = response.replace("<start_of_turn>", "")
        response = response.replace("<end_of_turn>", "")
        response = response.replace("user", "")
        response = response.replace("model", "")
        
        # Limpiar espacios y líneas vacías al inicio
        response = response.strip()
        
        return response


class GemmaApp:
    """Aplicación principal de Gemma Termux"""
    
    def __init__(self):
        self.db = DatabaseManager(DB_PATH)
        self.skills = SkillManager(SKILLS_DIR)
        self.sandbox = SandboxManager(SANDBOX_DIR)
        self.inference = GemmaInference(MODELS_DIR, self.db)
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.running = True
        
        # Configuración del sistema
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Construye el prompt del sistema con información de skills y contexto"""
        skills_info = []
        
        # Información de skills disponibles
        if self.skills.get_available_commands():
            skills_info.append("Comandos disponibles:")
            for cmd in self.skills.get_available_commands():
                skills_info.append(f"  - {cmd}")
        
        # Información del sandbox
        sandbox_info = f"Sandbox: {SANDBOX_DIR}"
        
        prompt_parts = [
            "Eres un asistente de IA ejecutándose localmente en Termux/Android.",
            "Tienes acceso a las siguientes capacidades:",
            "",
            "1. MEMORIA PERSISTENTE: Puedes recordar información importante.",
            "   - Para guardar: usa 'recuerda [clave] [valor]'",
            "   - Para buscar: usa 'busca [consulta]'",
            "",
            "2. SANDBOX DE ARCHIVOS: Puedes crear y editar archivos.",
            f"   {sandbox_info}",
            "   - Crear archivo: usa 'archivo crear [ruta] [contenido]'",
            "   - Leer archivo: usa 'archivo leer [ruta]'",
            "   - Escribir: usa 'archivo escribir [ruta] [contenido]'",
            "   - Listar: usa 'archivo listar [ruta]'",
            "",
        ]
        
        if skills_info:
            prompt_parts.extend([
                "3. SKILLS ESPECIALIZADOS:",
                "   " + "\n   ".join(skills_info),
                "",
            ])
        
        prompt_parts.extend([
            "Responde de manera concisa y útil.",
            "Si el usuario pide crear código o archivos, ofrécelo y pregúntale si quiere guardarlo."
        ])
        
        return "\n".join(prompt_parts)
    
    def process_command(self, user_input: str) -> Optional[str]:
        """Procesa comandos especiales del usuario"""
        user_input_lower = user_input.lower().strip()
        parts = user_input.split(maxsplit=2)
        
        if not parts:
            return None
        
        cmd = parts[0].lower()
        
        # Comandos de control
        if cmd in ['salir', 'exit', 'quit']:
            self.running = False
            return "¡Hasta luego! 👋"
        
        if cmd == 'ayuda' or cmd == 'help':
            return self._show_help()
        
        if cmd == 'limpiar' or cmd == 'clear':
            os.system('clear')
            return "Terminal limpiada."
        
        # Comandos de memoria
        if cmd == 'recuerda' and len(parts) >= 3:
            key = parts[1]
            value = parts[2]
            self.db.save_memory(key, value)
            return f"✓ Recordado: '{key}'"
        
        if cmd == 'busca' and len(parts) >= 2:
            query = parts[1]
            memories = self.db.search_memories(query)
            if memories:
                result = ["Recuerdos encontrados:"]
                for mem in memories[:5]:
                    result.append(f"  • {mem['key']}: {mem['value'][:100]}...")
                return "\n".join(result)
            return "No se encontraron recuerdos."
        
        if cmd == 'memorias':
            memories = self.db.get_all_memories()
            if memories:
                result = ["Tus memorias:"]
                for mem in memories[:10]:
                    result.append(f"  • {mem['key']}: {mem['value'][:80]}...")
                return "\n".join(result)
            return "No hay memorias guardadas."
        
        # Comandos de sandbox
        if cmd == 'archivo':
            return self._handle_sandbox_command(parts[1:])
        
        # Comandos de skills
        if cmd in self.skills.get_available_commands():
            args = parts[1:] if len(parts) > 1 else []
            return self.skills.execute_command(cmd, *args)
        
        # Comandos del sistema
        if cmd == 'modelo':
            return self._show_model_info()
        
        if cmd == 'stats':
            return self._show_stats()
        
        if cmd == 'reload':
            self.skills.reload_skills()
            return "Skills recargados."
        
        return None
    
    def _handle_sandbox_command(self, args: List[str]) -> str:
        """Maneja comandos del sandbox"""
        if len(args) < 1:
            return "Uso: archivo [crear|leer|escribir|listar|eliminar|info] [args...]"
        
        subcmd = args[0].lower()
        
        if subcmd == 'crear' and len(args) >= 2:
            path = args[1]
            content = args[2] if len(args) > 2 else ""
            return self.sandbox.create_file(path, content)
        
        elif subcmd == 'leer' and len(args) >= 2:
            path = args[1]
            return self.sandbox.read_file(path)
        
        elif subcmd == 'escribir' and len(args) >= 3:
            path = args[1]
            content = args[2]
            return self.sandbox.write_file(path, content)
        
        elif subcmd == 'añadir' and len(args) >= 3:
            path = args[1]
            content = args[2]
            return self.sandbox.append_file(path, content)
        
        elif subcmd == 'listar':
            path = args[1] if len(args) > 1 else "."
            return self.sandbox.list_files(path)
        
        elif subcmd == 'eliminar' and len(args) >= 2:
            path = args[1]
            return self.sandbox.delete_file(path)
        
        elif subcmd == 'info' and len(args) >= 2:
            path = args[1]
            return self.sandbox.get_info(path)
        
        return f"Comando de archivo desconocido: {subcmd}"
    
    def _show_help(self) -> str:
        """Muestra la ayuda de la aplicación"""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                    GEMMA TERMUX APP                          ║
║              Asistente IA Local para Android                 ║
╚══════════════════════════════════════════════════════════════╝

COMANDOS GENERALES:
  ayuda, help          - Muestra esta ayuda
  limpiar, clear       - Limpia la terminal
  salir, exit, quit    - Cierra la aplicación
  modelo               - Información del modelo
  stats                - Estadísticas de uso
  reload               - Recarga los skills

MEMORIA PERSISTENTE:
  recuerda [clave] [valor]  - Guarda información
  busca [consulta]          - Busca en memorias
  memorias                  - Lista todas las memorias

SANDBOX DE ARCHIVOS:
  archivo crear [ruta] [contenido]   - Crea archivo
  archivo leer [ruta]                - Lee archivo
  archivo escribir [ruta] [contenido] - Escribe archivo
  archivo añadir [ruta] [contenido]  - Añade al final
  archivo listar [ruta]              - Lista archivos
  archivo eliminar [ruta]            - Elimina archivo
  archivo info [ruta]                - Info del archivo

SKILLS DISPONIBLES:
"""
        for cmd in self.skills.get_available_commands():
            help_text += f"  {cmd}\n"
        
        return help_text
    
    def _show_model_info(self) -> str:
        """Muestra información del modelo"""
        info = []
        info.append("═" * 50)
        info.append("INFORMACIÓN DEL MODELO")
        info.append("═" * 50)
        
        if self.inference.model_path:
            info.append(f"Modelo: {self.inference.model_path.name}")
            size_mb = self.inference.model_path.stat().st_size / (1024*1024)
            info.append(f"Tamaño: {size_mb:.1f} MB")
        else:
            info.append("Modelo: No encontrado")
        
        if self.inference.llama_cpp_path:
            info.append(f"Backend: llama.cpp")
            info.append(f"Ruta: {self.inference.llama_cpp_path}")
        else:
            info.append("Backend: No disponible")
        
        info.append(f"Contexto: {self.inference.context_size} tokens")
        info.append(f"Temperatura: {self.inference.temperature}")
        info.append(f"Max tokens: {self.inference.max_tokens}")
        info.append("═" * 50)
        
        return "\n".join(info)
    
    def _show_stats(self) -> str:
        """Muestra estadísticas de uso"""
        # TODO: Implementar estadísticas detalladas
        return "Estadísticas - Próximamente"
    
    def chat(self, message: str) -> str:
        """Procesa un mensaje de chat"""
        # Guardar mensaje del usuario
        user_msg = Message(role='user', content=message)
        self.db.save_message(self.session_id, user_msg)
        
        # Verificar si es un comando
        command_result = self.process_command(message)
        if command_result is not None:
            # Es un comando, no pasar al modelo
            if not message.lower().startswith(('salir', 'exit', 'quit')):
                assistant_msg = Message(role='assistant', content=command_result)
                self.db.save_message(self.session_id, assistant_msg)
            return command_result
        
        # Buscar memorias relevantes
        relevant_memories = self.db.search_memories(message, limit=3)
        memory_context = ""
        if relevant_memories:
            memory_context = "\nInformación relevante de tu memoria:\n"
            for mem in relevant_memories:
                memory_context += f"- {mem['key']}: {mem['value']}\n"
        
        # Construir prompt con contexto
        full_prompt = message
        if memory_context:
            full_prompt = memory_context + "\n" + message
        
        # Generar respuesta
        if self.inference.is_available():
            response = self.inference.generate(
                full_prompt,
                system_prompt=self.system_prompt
            )
        else:
            response = """Modelo no disponible. Asegúrate de:
1. Tener llama.cpp instalado: pkg install llama-cpp
2. Descargar el modelo Gemma 4B: 
   wget https://huggingface.co/.../gemma-4b-it-Q4_K_M.gguf -O models/gemma-4b-it.gguf
3. Reiniciar la aplicación"""
        
        # Guardar respuesta
        assistant_msg = Message(role='assistant', content=response)
        self.db.save_message(self.session_id, assistant_msg)
        
        return response
    
    def run_interactive(self):
        """Ejecuta el modo interactivo"""
        # Banner
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ██████╗ ███████╗███╗   ███╗███╗   ███╗ █████╗             ║
║  ██╔════╝ ██╔════╝████╗ ████║████╗ ████║██╔══██╗            ║
║  ██║  ███╗█████╗  ██╔████╔██║██╔████╔██║███████║            ║
║  ██║   ██║██╔══╝  ██║╚██╔╝██║██║╚██╔╝██║██╔══██║            ║
║  ╚██████╔╝███████╗██║ ╚═╝ ██║██║ ╚═╝ ██║██║  ██║            ║
║   ╚═════╝ ╚══════╝╚═╝     ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝            ║
║                                                              ║
║              TERMUX APP v1.0 - Asistente IA Local            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
        # Estado del sistema
        print("Estado del sistema:")
        if self.inference.is_available():
            print(f"  ✓ Modelo: {self.inference.model_path.name}")
        else:
            print("  ✗ Modelo: No disponible")
        print(f"  ✓ Memoria: {DB_PATH}")
        print(f"  ✓ Sandbox: {SANDBOX_DIR}")
        print(f"  ✓ Skills cargados: {len(self.skills.skills)}")
        print()
        print("Escribe 'ayuda' para ver los comandos disponibles.")
        print("═" * 60)
        
        # Bucle principal
        while self.running:
            try:
                # Leer input del usuario
                user_input = input("\n👤 Tú: ").strip()
                
                if not user_input:
                    continue
                
                # Procesar y mostrar respuesta
                response = self.chat(user_input)
                
                if self.running:  # Si no salimos
                    print(f"\n🤖 Gemma: {response}")
                
            except KeyboardInterrupt:
                print("\n\nUse 'salir' para terminar.")
            except EOFError:
                break
        
        print("\n¡Gracias por usar Gemma Termux App! 👋")


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Gemma Termux App - Asistente IA Local'
    )
    parser.add_argument(
        '--message', '-m',
        help='Mensaje único (modo no interactivo)'
    )
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Ejecutar configuración inicial'
    )
    
    args = parser.parse_args()
    
    if args.setup:
        print("Configuración inicial...")
        # Crear estructura de directorios
        for dir_path in [SKILLS_DIR, SANDBOX_DIR, MODELS_DIR, CONFIG_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
        print("✓ Estructura creada")
        print(f"✓ Base de datos: {DB_PATH}")
        print(f"✓ Coloca tu modelo en: {MODELS_DIR}")
        return
    
    # Crear instancia de la app
    app = GemmaApp()
    
    if args.message:
        # Modo no interactivo
        response = app.chat(args.message)
        print(response)
    else:
        # Modo interactivo
        app.run_interactive()


if __name__ == '__main__':
    main()
