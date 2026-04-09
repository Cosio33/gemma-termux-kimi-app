# 🤖 Gemma Termux App

Un asistente de inteligencia artificial **local y privado** para Termux/Android, implementando el modelo **Gemma 4-E2B-it** de Google de forma nativa. Caracterizado por su sistema de skills extensible, memoria persistente y capacidad de gestión de archivos sandbox.

Este asistente fue creado con la ayuda de [Kimi AI](https://www.kimi.com/) gracias a su modelo K2.5 se genero con todas las herramientas y correcciones necesarias para que el proyecto pueda desplegarse de forma correcta.

![Versión](https://img.shields.io/badge/versión-1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Licencia](https://img.shields.io/badge/licencia-MIT-yellow)

---

## ✨ Características

- 🧠 **Inferencia Local**: Ejecuta Gemma completamente en tu dispositivo, sin conexión a internet
- 🔌 **Sistema de Skills**: Extensible con plugins personalizados
- 💾 **Memoria Persistente**: SQLite para recordar información importante
- 📁 **Sandbox de Archivos**: Crea y edita archivos de forma segura
- 📱 **Integración Termux**: Aprovecha las APIs de Termux (batería, WiFi, vibración, etc.)
- 🛠️ **Herramientas Integradas**: Calculadora, utilidades de red, análisis de código, y más
- 💬 **Chat Interactivo**: Interfaz conversacional natural
- 🔒 **100% Privado**: Tus datos nunca salen de tu dispositivo

---

## 📋 Requisitos

- **Termux** (última versión de F-Droid)
- **Android 7.0+** (API 24)
- **Almacenamiento**: 3GB+ libres (para modelo + app)
- **RAM**: 4GB+ recomendado

---

## ⚠️ IMPORTANTE: Compatibilidad con Gemma 4

### Error Común: "unknown model architecture: 'gemma4'"

Si ves este error al ejecutar la app:
```
llama_model_load: error loading model: error loading model architecture: unknown model architecture: 'gemma4'
```

**Significa que tu versión de llama.cpp no soporta Gemma 4.**

### Solución Rápida

Ejecuta el script de corrección:
```bash
bash fix_llama.sh
```

O manualmente:
```bash
# 1. Desinstala la versión antigua
pkg uninstall llama-cpp

# 2. Instala dependencias
pkg install git cmake clang

# 3. Compila desde fuente
cd ~
git clone --depth 1 https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
cmake -B build
cmake --build build --config Release -j$(nproc)

# 4. Crea enlace simbólico
ln -s ~/llama.cpp/build/bin/llama-cli $PREFIX/bin/llama-cli
```

---

## 🚀 Instalación Rápida

### Método 1: Script Automático (Recomendado)

```bash
# Descargar el instalador
curl -fsSL https://raw.githubusercontent.com/tu-repo/gemma-termux-app/main/install.sh -o install.sh

# Ejecutar instalador
bash install.sh
```

### Método 2: Instalación Manual

```bash
# 1. Actualizar Termux
pkg update && pkg upgrade -y

# 2. Instalar dependencias
pkg install python python-pip git wget curl

# 3. Instalar llama.cpp
pkg install llama-cpp
# O compilar desde fuente:
# git clone https://github.com/ggerganov/llama.cpp
# cd llama.cpp && make
# cp main $PREFIX/bin/llama-cli

# 4. Clonar la aplicación
cd $HOME
git clone https://github.com/tu-repo/gemma-termux-app.git

# 5. Crear estructura
mkdir -p gemma-termux-app/{src,skills,sandbox,models,config}

# 6. Descargar modelo Gemma (FORMATO GGUF REQUERIDO)
cd gemma-termux-app/models

# ⚠️ IMPORTANTE: Esta app usa llama.cpp que requiere modelos en formato GGUF
# NO uses modelos LiteRT-LM (.litertlm) - son incompatibles

# 📱 GEMMA 4 ESPECIALES PARA ANDROID (Recomendados):

# Opción A: Gemma 4 E2B-IT (2B params, ~1.5GB) - Muy ligero
wget https://huggingface.co/unsloth/gemma-4-e2b-it-GGUF/resolve/main/gemma-4-e2b-it-Q4_K_M.gguf

# Opción B: Gemma 4 E4B-IT (4B params, ~2.6GB) - RECOMENDADO ✓
wget https://huggingface.co/lmstudio-community/gemma-4-E4B-it-GGUF/resolve/main/gemma-4-E4B-it-Q4_K_M.gguf

# 📊 GEMMA 4 ESTÁNDAR:

# Opción C: Gemma 4 4B-IT (4B params, ~2.5GB) - Estándar
wget https://huggingface.co/unsloth/gemma-4-4b-it-GGUF/resolve/main/gemma-4-4b-it-Q4_K_M.gguf

# Opción D: Gemma 4 12B-IT (12B params, ~7GB) - Alta calidad
wget https://huggingface.co/unsloth/gemma-4-12b-it-GGUF/resolve/main/gemma-4-12b-it-Q4_K_M.gguf

# 💡 Nota: Q4_K_M = buen balance, Q5_K_M = mejor calidad, Q8_0 = casi sin pérdida

# 7. Crear launcher
echo '#!/bin/bash' > $PREFIX/bin/gemma
echo 'cd $HOME/gemma-termux-app && python src/main.py "$@"' >> $PREFIX/bin/gemma
chmod +x $PREFIX/bin/gemma

# 8. ¡Ejecutar!
gemma
```

---

## 📚 Información sobre Modelos

### ⚠️ GGUF vs LiteRT-LM - ¡Importante!

Esta aplicación utiliza **llama.cpp** como backend de inferencia, que requiere modelos en formato **GGUF**.

| Formato | Descripción | Compatible |
|---------|-------------|------------|
| **GGUF** (.gguf) | Formato de llama.cpp (GGML) | ✅ Sí |
| **LiteRT-LM** (.litertlm) | TensorFlow Lite para Android | ❌ No |
| **SafeTensors** (.safetensors) | Formato original de Hugging Face | ⚠️ Requiere conversión |

**¿Por qué no LiteRT-LM?**
- LiteRT-LM usa TensorFlow Lite Runtime
- GGUF usa GGML/llama.cpp
- Son arquitecturas completamente diferentes e incompatibles

**¿Dónde conseguir modelos GGUF?**
- [unsloth/gemma-4-4b-it-GGUF](https://huggingface.co/unsloth/gemma-4-4b-it-GGUF) - Gemma 4 estándar
- [lmstudio-community/gemma-4-E4B-it-GGUF](https://huggingface.co/lmstudio-community/gemma-4-E4B-it-GGUF) - Gemma 4 E4B especializado
- [unsloth/gemma-4-e2b-it-GGUF](https://huggingface.co/unsloth/gemma-4-e2b-it-GGUF) - Gemma 4 E2B ligero

**¿Cómo convertir de SafeTensors a GGUF?**
Usa el notebook de Google Colab incluido: [`convert_to_gguf_colab.ipynb`](convert_to_gguf_colab.ipynb)

### 📊 Tabla de Modelos Recomendados

| Modelo | Parámetros | Tamaño Q4_K_M | VRAM/RAM | Ideal Para |
|--------|------------|---------------|----------|------------|
| Gemma 4 E2B-IT | 2B | ~1.5 GB | 2-3 GB | Móviles básicos |
| Gemma 4 E4B-IT | 4B | ~2.6 GB | 3-4 GB | **Android recomendado** ✓ |
| Gemma 4 4B-IT | 4B | ~2.5 GB | 3-4 GB | Balance general |
| Gemma 4 12B-IT | 12B | ~7 GB | 8+ GB | Alta calidad |

### 🔧 Niveles de Cuantización

| Tipo | Tamaño | Calidad | Uso Recomendado |
|------|--------|---------|-----------------|
| Q4_K_M | Base | Buena | **Recomendado para Android** |
| Q5_K_M | +25% | Mejor | Si tienes RAM suficiente |
| Q8_0 | +50% | Excelente | Casi sin pérdida |
| F16 | +200% | Original | Solo si tienes mucha RAM |

---

## 🎮 Uso

### Modo Interactivo (Recomendado)

```bash
gemma
```

Interfaz de chat conversacional con:
- Historial persistente
- Comandos integrados
- Acceso a todos los skills

### Modo No Interactivo

```bash
# Ejecutar un solo mensaje
gemma -m "¿Qué puedes hacer?"

# Pipe de entrada
echo "Hola" | gemma
```

### Configuración Inicial

```bash
gemma --setup
```

---

## 📚 Comandos Disponibles

### Generales

| Comando | Descripción |
|---------|-------------|
| `ayuda`, `help` | Muestra ayuda completa |
| `limpiar`, `clear` | Limpia la terminal |
| `salir`, `exit`, `quit` | Cierra la aplicación |
| `modelo` | Información del modelo cargado |
| `stats` | Estadísticas de uso |
| `reload` | Recarga los skills |

### Memoria Persistente

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `recuerda [clave] [valor]` | Guarda información | `recuerda mi_color azul` |
| `busca [consulta]` | Busca en memorias | `busca color` |
| `memorias` | Lista todas las memorias | `memorias` |

### Sandbox de Archivos

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `archivo crear [ruta] [contenido]` | Crea archivo | `archivo crear notas.txt Mis notas` |
| `archivo leer [ruta]` | Lee archivo | `archivo leer notas.txt` |
| `archivo escribir [ruta] [contenido]` | Sobreescribe archivo | `archivo escribir notas.txt Nuevo contenido` |
| `archivo añadir [ruta] [contenido]` | Añade al final | `archivo añadir notas.txt Más notas` |
| `archivo listar [ruta]` | Lista archivos | `archivo listar .` |
| `archivo eliminar [ruta]` | Elimina archivo | `archivo eliminar notas.txt` |
| `archivo info [ruta]` | Información del archivo | `archivo info notas.txt` |

### Skills Integrados

#### 🧮 Calculadora (`skills/calculator.py`)

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `calc [expresión]` | Calcula expresiones | `calc 2 + 2 * 5` |
| `convert [valor] [de] [a]` | Convierte unidades | `convert 100 m km` |
| `base [número] [base_origen] [base_destino]` | Convierte bases | `base 1010 2 10` |

#### 🖥️ Sistema (`skills/system.py`)

| Comando | Descripción |
|---------|-------------|
| `sysinfo` | Información del sistema |
| `battery` | Estado de la batería |
| `wifi [acción]` | Control WiFi (status/on/off/info) |
| `clipboard [acción]` | Gestión del portapapeles |
| `torch [estado]` | Control de linterna |
| `vibrate [duración]` | Vibración del dispositivo |
| `share [texto]` | Comparte texto |
| `open_url [url]` | Abre URL en navegador |

#### 💻 Code Utils (`skills/code_utils.py`)

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `analyze_code [código/archivo]` | Analiza código | `analyze_code script.py` |
| `format_code [código]` | Formatea código | `format_code "def foo():pass"` |
| `minify_code [código]` | Minifica código | `minify_code script.py` |
| `count_lines [ruta]` | Cuenta líneas | `count_lines ./proyecto` |
| `find_functions [código]` | Encuentra funciones | `find_functions script.py` |
| `generate_docstring [código]` | Genera docstrings | `generate_docstring "def add(a,b):pass"` |

#### 🌐 Network (`skills/network.py`)

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `ping [host]` | Ping a host | `ping google.com` |
| `resolve [dominio]` | Resuelve DNS | `resolve google.com` |
| `myip` | Muestra IP pública | `myip` |
| `localip` | Muestra IP local | `localip` |
| `port_check [host] [puerto]` | Verifica puerto | `port_check localhost 8080` |
| `whois [dominio]` | Consulta WHOIS | `whois google.com` |
| `curl [url]` | Petición HTTP | `curl https://api.example.com` |
| `scan_ports [host] [inicio] [fin]` | Escanea puertos | `scan_ports localhost 1 100` |

#### ⏰ Time Utils (`skills/time_utils.py`)

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `now` | Fecha y hora actual | `now` |
| `timer [segundos]` | Temporizador | `timer 300` |
| `countdown [fecha]` | Cuenta regresiva | `countdown 2024-12-31` |
| `stopwatch [acción]` | Cronómetro | `stopwatch start` |
| `calendar [mes] [año]` | Calendario | `calendar 12 2024` |
| `convert_time [hora] [de] [a]` | Convierte zonas | `convert_time 12:00 est jst` |

---

## 🔧 Crear Skills Personalizados

Los skills son módulos Python que se cargan dinámicamente. Para crear uno:

### 1. Crear archivo en `skills/`

```python
#!/usr/bin/env python3
# skills/mi_skill.py

def saludo(nombre: str = "mundo") -> str:
    """Retorna un saludo personalizado."""
    return f"¡Hola, {nombre}! 👋"

def despedida() -> str:
    """Retorna una despedida."""
    return "¡Hasta luego! 👋"

# Comandos exportados (obligatorio)
COMMANDS = {
    'saludo': saludo,
    'despedida': despedida,
}

# Información del skill (opcional)
SKILL_INFO = {
    'name': 'Mi Skill',
    'description': 'Ejemplo de skill personalizado',
    'version': '1.0',
    'author': 'Tu Nombre',
    'commands': list(COMMANDS.keys())
}

def info():
    return SKILL_INFO
```

### 2. Recargar skills

```
reload
```

### 3. Usar el nuevo comando

```
saludo Juan
```

---

## 📁 Estructura del Proyecto

```
gemma-termux-app/
├── src/
│   └── main.py              # Aplicación principal
├── skills/
│   ├── calculator.py        # Skill de calculadora
│   ├── system.py            # Skill de sistema
│   ├── code_utils.py        # Skill de código
│   ├── network.py           # Skill de red
│   └── time_utils.py        # Skill de tiempo
├── sandbox/                 # Carpeta segura para archivos
├── models/                  # Modelos GGUF
│   └── gemma-*.gguf
├── config/                  # Configuraciones
├── memory.db                # Base de datos SQLite
├── install.sh               # Script de instalación
└── README.md                # Este archivo
```

---

## ⚙️ Configuración Avanzada

### Variables de Entorno

```bash
# Ruta al modelo
export GEMMA_MODEL_PATH="$HOME/gemma-termux-app/models/gemma-4b-it.gguf"

# Tamaño de contexto
export GEMMA_CONTEXT_SIZE=4096

# Temperatura (creatividad)
export GEMMA_TEMPERATURE=0.7

# Máximo de tokens
export GEMMA_MAX_TOKENS=2048
```

### Configuración en Base de Datos

```python
# Desde la app, puedes configurar:
recuerda config_temperature 0.8
recuerda config_context_size 8192
```

---

## 🔍 Solución de Problemas

### "Modelo no encontrado"

```bash
# Verificar que el modelo existe
ls -la $HOME/gemma-termux-app/models/

# Descargar modelo
wget https://huggingface.co/lmstudio-community/gemma-2b-it-GGUF/resolve/main/gemma-2b-it-Q4_K_M.gguf -P $HOME/gemma-termux-app/models/
```

### "llama.cpp no encontrado"

```bash
# Instalar desde repo
pkg install llama-cpp

# O compilar manualmente
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && make
ln -s $(pwd)/main $PREFIX/bin/llama-cli
```

### "Error de memoria"

- Usa un modelo más pequeño (2B en lugar de 7B)
- Cierra otras aplicaciones
- Aumenta el swap de Termux:
  ```bash
  pkg install zram-config
  ```

### "Skills no cargan"

```bash
# Verificar permisos
chmod +x $HOME/gemma-termux-app/skills/*.py

# Recargar
reload
```

---

## 📝 Ejemplos de Uso

### Ejemplo 1: Asistente de Programación

```
👤 Tú: Crea un script Python que calcule fibonacci

🤖 Gemma: [genera código]

👤 Tú: archivo crear fibonacci.py [código]

✓ Archivo creado: fibonacci.py

👤 Tú: analyze_code fibonacci.py

[análisis del código]
```

### Ejemplo 2: Gestión de Notas

```
👤 Tú: recuerda proyecto_idea "App de productividad con IA"

✓ Recordado: 'proyecto_idea'

👤 Tú: archivo crear ideas.txt Mis ideas de proyectos

✓ Archivo creado: ideas.txt

👤 Tú: busca proyecto

Recuerdos encontrados:
  • proyecto_idea: App de productividad con IA...
```

### Ejemplo 3: Utilidades del Sistema

```
👤 Tú: battery

🔋 ESTADO DE BATERÍA
══════════════════════════════
Nivel: 85%
Estado: CHARGING
Temperatura: 32.5°C

👤 Tú: wifi status

📶 INFORMACIÓN WiFi
══════════════════════════════
SSID: MiRedWiFi
RSSI: -45 dBm
IP: 192.168.1.100
```

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Ideas de Contribución

- [ ] Nuevos skills (clima, traductor, etc.)
- [ ] Soporte para más modelos (Llama, Mistral, etc.)
- [ ] Interfaz web opcional
- [ ] Integración con más APIs de Termux
- [ ] Sincronización de memoria entre dispositivos
- [ ] Exportar/importar conversaciones

### Logs al momento

🪧 Se tiene un error de tiempo de espera de 5 minutos ya que el ajente usa razonamiento profundo se esta trabajando en este error. 


---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

---

## 🙏 Agradecimientos

- [Kimi AI](https://www.kimi.com/) por el modelo k2.5 con Agente autónomo es simplemente revolucionaria. La forma en que K2.5 puede planificar estrategias multi-paso, razonar sobre problemas complejos y ejecutar acciones utilizando herramientas integradas—desde búsquedas web precisas hasta el análisis de datos en tiempo real—demuestra un nivel de autonomía y proactividad que va más allá de los simples chatbots. Esa capacidad de descomponer tareas complejas, tomar decisiones informadas y mantener el contexto a lo largo de conversaciones extensas hace que realmente sienta que tengo un colaborador inteligente a mi lado, no solo una interfaz de texto.

El entorno de ejecución de código en la nube con terminal es, sin duda, una de las funcionalidades más poderosas y diferenciadoras. El hecho de poder escribir, ejecutar y depurar código Python en tiempo real dentro de la conversación—con acceso a bibliotecas completas de análisis de datos, capacidad de generar visualizaciones profesionales con matplotlib, procesar imágenes y realizar cálculos complejos—elimina completamente la fricción entre la ideación y la implementación. Es como tener un Jupyter Notebook potenciado por IA, donde puedo iterar instantáneamente sobre soluciones, ver resultados visuales inmediatos y construir pipelines de datos sofisticados sin salir del flujo de trabajo conversacional.

- [Google](https://ai.google.dev/gemma) por el modelo Gemma
- [llama.cpp](https://github.com/ggerganov/llama.cpp) por el motor de inferencia
- [Termux](https://termux.dev/) por la excelente app de terminal
- Comunidad de IA open source

---



<p align="center">
  <b>Hecho con ❤️ para la comunidad de Termux</b>
</p>

<p align="center">
  <a href="https://github.com/tu-repo/gemma-termux-app">⭐ Star en GitHub</a>
</p>
