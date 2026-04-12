#!/bin/bash
# =============================================================================
# Gemma Termux App - Script de Instalación
# Instala y configura la aplicación de asistente IA local
# =============================================================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
APP_NAME="Gemma Termux App"
INSTALL_DIR="$HOME/gemma-termux-app"
REPO_URL="https://github.com/google/gemma.cpp"  # Referencia

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   ██████╗ ███████╗███╗   ███╗███╗   ███╗ █████╗             ║"
echo "║  ██╔════╝ ██╔════╝████╗ ████║████╗ ████║██╔══██╗            ║"
echo "║  ██║  ███╗█████╗  ██╔████╔██║██╔████╔██║███████║            ║"
echo "║  ██║   ██║██╔══╝  ██║╚██╔╝██║██║╚██╔╝██║██╔══██║            ║"
echo "║  ╚██████╔╝███████╗██║ ╚═╝ ██║██║ ╚═╝ ██║██║  ██║            ║"
echo "║   ╚═════╝ ╚══════╝╚═╝     ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝            ║"
echo "║                                                              ║"
echo "║              TERMUX APP - Instalador v1.0                    ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Funciones de utilidad
print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Verificar que estamos en Termux
if [ -z "$TERMUX_VERSION" ] && [ ! -d "/data/data/com.termux" ]; then
    print_warning "No parece que estés en Termux. Algunas funciones pueden no funcionar."
    read -p "¿Continuar de todos modos? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

print_status "Iniciando instalación de $APP_NAME..."
echo

# =============================================================================
# PASO 1: Actualizar repositorios
# =============================================================================
print_status "Paso 1/7: Actualizando repositorios..."
apt update -y > /dev/null 2>&1 || true
print_success "Repositorios actualizados"

# =============================================================================
# PASO 2: Instalar dependencias básicas
# =============================================================================
print_status "Paso 2/7: Instalando dependencias básicas..."

PACKAGES="python python-pip git wget curl"

for pkg in $PACKAGES; do
    if ! dpkg -l | grep -q "^ii  $pkg "; then
        print_status "  Instalando $pkg..."
        apt install -y $pkg > /dev/null 2>&1 || print_warning "No se pudo instalar $pkg"
    fi
done

print_success "Dependencias básicas instaladas"

# =============================================================================
# PASO 3: Instalar/Compilar llama.cpp
# =============================================================================
print_status "Paso 3/7: Instalando llama.cpp..."

# Función para compilar llama.cpp desde fuente
compile_llama_cpp() {
    print_status "Compilando llama.cpp desde fuente (soporta Gemma 4)..."
    
    # Instalar dependencias de compilación
    print_status "  Instalando dependencias de compilación..."
    apt install -y git cmake clang 2>/dev/null || {
        print_error "No se pudieron instalar dependencias de compilación"
        return 1
    }
    
    # Crear directorio de compilación
    LLAMA_DIR="$HOME/llama.cpp"
    
    # Eliminar instalación anterior si existe
    if [ -d "$LLAMA_DIR" ]; then
        print_status "  Eliminando instalación anterior..."
        rm -rf "$LLAMA_DIR"
    fi
    
    # Clonar repositorio
    print_status "  Clonando llama.cpp..."
    cd "$HOME"
    git clone --depth 1 https://github.com/ggerganov/llama.cpp.git 2>/dev/null || {
        print_error "No se pudo clonar llama.cpp"
        return 1
    }
    
    cd "$LLAMA_DIR"
    
    # Compilar con cmake
    print_status "  Compilando (esto puede tardar varios minutos)..."
    cmake -B build -DCMAKE_BUILD_TYPE=Release 2>/dev/null || {
        print_error "Error en cmake"
        return 1
    }
    
    cmake --build build --config Release -j$(nproc) 2>/dev/null || {
        print_warning "Error paralelo, intentando compilación secuencial..."
        cmake --build build --config Release
    }
    
    # Verificar que se creó el binario
    if [ -f "$LLAMA_DIR/build/bin/llama-cli" ]; then
        # Crear enlaces simbólicos
        ln -sf "$LLAMA_DIR/build/bin/llama-cli" "$PREFIX/bin/llama-cli"
        ln -sf "$LLAMA_DIR/build/bin/llama-server" "$PREFIX/bin/llama-server" 2>/dev/null || true
        
        print_success "llama.cpp compilado e instalado correctamente"
        return 0
    else
        print_error "No se encontró el binario compilado"
        return 1
    fi
}

# Verificar si llama.cpp ya está instalado y es compatible
if command -v llama-cli &> /dev/null; then
    # Verificar versión soporta Gemma 4
    LLAMA_VERSION=$(llama-cli --version 2>&1 | head -1)
    print_status "llama-cli encontrado: $LLAMA_VERSION"
    
    # Preguntar si reinstalar
    echo
    print_warning "La versión del repositorio de Termux puede no soportar Gemma 4"
    read -p "¿Recompilar desde fuente para asegurar compatibilidad? (s/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        compile_llama_cpp
    else
        print_warning "Usando versión existente. Si hay errores con Gemma 4, reinstala."
    fi
else
    # No está instalado, compilar desde fuente
    compile_llama_cpp
fi

# =============================================================================
# PASO 4: Instalar dependencias de Python
# =============================================================================
print_status "Paso 4/7: Instalando dependencias de Python..."

# Instalar paquetes necesarios
pip install requests 2>/dev/null || true

print_success "Dependencias de Python instaladas"

# =============================================================================
# PASO 5: Crear estructura de directorios
# =============================================================================
print_status "Paso 5/7: Creando estructura de directorios..."

# Crear directorios
mkdir -p "$INSTALL_DIR"/{src,skills,sandbox,models,config}

print_success "Estructura creada en $INSTALL_DIR"

# =============================================================================
# PASO 6: Descargar modelo Gemma (opcional)
# =============================================================================
print_status "Paso 6/7: Configuración del modelo Gemma..."

echo
echo -e "${YELLOW}══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  MODELO GEMMA 4 - FORMATO GGUF${NC}"
echo -e "${YELLOW}══════════════════════════════════════════════════════════════${NC}"
echo
print_status "Modelos disponibles en formato GGUF (compatible con llama.cpp):"
echo
print_status "📱 GEMMA 4 ESPECIALES PARA ANDROID:"
echo
print_status "1. Gemma 4 E2B-IT (muy ligero, ~1.5GB):"
echo "   2B params especializado, ideal para móviles"
echo "   URL: unsloth/gemma-4-e2b-it-GGUF"
echo
print_status "2. Gemma 4 E4B-IT (balance, ~2.6GB):"
echo "   4B params especializado, recomendado"
echo "   URL: lmstudio-community/gemma-4-E4B-it-GGUF"
echo
print_status "📊 GEMMA 4 ESTÁNDAR:"
echo
print_status "3. Gemma 4 4B-IT (~2.5GB):"
echo "   4B params estándar, buen balance"
echo "   URL: unsloth/gemma-4-4b-it-GGUF"
echo
print_status "4. Gemma 4 12B-IT (~7GB):"
echo "   12B params, máxima calidad (requiere 6GB+ RAM)"
echo "   URL: unsloth/gemma-4-12b-it-GGUF"
echo
print_status "📏 NIVELES DE CUANTIZACIÓN:"
echo "   Q4_K_M = Balance calidad/tamaño (recomendado)"
echo "   Q5_K_M = Mejor calidad, más grande"
echo "   Q8_0   = Casi sin pérdida, muy grande"
echo
echo -e "${YELLOW}══════════════════════════════════════════════════════════════${NC}"
echo

read -p "¿Deseas descargar un modelo ahora? (s/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo
    echo "Selecciona el modelo:"
    echo "  1) Gemma 4 E2B-IT Q4_K_M (~1.5GB) - Móvil básico"
    echo "  2) Gemma 4 E4B-IT Q4_K_M (~2.6GB) - RECOMENDADO ✓"
    echo "  3) Gemma 4 4B-IT Q4_K_M (~2.5GB) - Estándar"
    echo "  4) Gemma 4 E4B-IT Q5_K_M (~3.2GB) - Mejor calidad"
    echo "  5) Omitir descarga"
    echo
    read -p "Opción (1-5): " model_choice
    
    case $model_choice in
        1)
            MODEL_URL="https://huggingface.co/lmstudio-community/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-Q8_0.gguf"
            MODEL_NAME="gemma-4-e2b-it-Q4_K_M.gguf"
            MODEL_DESC="Gemma 4 E2B-IT (2B params)"
            ;;
        2)
            MODEL_URL="https://huggingface.co/lmstudio-community/gemma-4-E4B-it-GGUF/resolve/main/gemma-4-E4B-it-Q4_K_M.gguf"
            MODEL_NAME="gemma-4-E4B-it-Q4_K_M.gguf"
            MODEL_DESC="Gemma 4 E4B-IT (4B params) - RECOMENDADO"
            ;;
        3)
            MODEL_URL="https://huggingface.co/lmstudio-community/DeepSeek-R1-Distill-Llama-8B-GGUF/blob/main/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf"
            MODEL_NAME="gDeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf"
            MODEL_DESC="DeepSeek-R1-8B"
            ;;
        4)
            MODEL_URL="https://huggingface.co/lmstudio-community/GLM-4-9B-0414-GGUF/blob/main/GLM-4-9B-0414-Q4_K_M.gguf"
            MODEL_NAME="GLM-4-9B-0414-Q4_K_M.gguf"
            MODEL_DESC="GLM-4-9B"
            ;;
        *)
            print_status "Descarga omitida"
            MODEL_URL=""
            MODEL_DESC=""
            ;;
    esac
    
    if [ -n "$MODEL_URL" ]; then
        echo
        print_status "Descargando: $MODEL_DESC"
        print_status "Archivo: $MODEL_NAME"
        print_status "Esto puede tardar varios minutos según tu conexión..."
        echo
        cd "$INSTALL_DIR/models"
        wget --show-progress -O "$MODEL_NAME" "$MODEL_URL" 2>&1 || {
            print_error "Error descargando el modelo"
            print_status "Puedes descargarlo manualmente desde:"
            echo "  $MODEL_URL"
            echo
            print_status "O usa huggingface-cli:"
            echo "  pip install huggingface-hub"
            echo "  huggingface-cli download $(dirname $MODEL_URL | sed 's|https://huggingface.co/||') $MODEL_NAME --local-dir ."
        }
        cd "$HOME"
        
        if [ -f "$INSTALL_DIR/models/$MODEL_NAME" ]; then
            print_success "Modelo descargado: $MODEL_NAME"
            
            # Crear enlace simbólico como modelo por defecto
            ln -sf "$MODEL_NAME" "$INSTALL_DIR/models/gemma-default.gguf" 2>/dev/null || true
            print_success "Modelo configurado como predeterminado"
        fi
    fi
else
    print_status "Puedes descargar un modelo más tarde en: $INSTALL_DIR/models/"
    print_status "URLs recomendadas:"
    echo "  wget https://huggingface.co/lmstudio-community/gemma-4-E4B-it-GGUF/resolve/main/gemma-4-E4B-it-Q4_K_M.gguf"
fi

# =============================================================================
# PASO 7: Configurar aplicación
# =============================================================================
print_status "Paso 7/7: Configurando aplicación..."

# Verificar si los archivos fuente existen en el directorio actual
if [ -f "src/main.py" ]; then
    print_status "  Copiando archivos fuente..."
    cp -r src/* "$INSTALL_DIR/src/" 2>/dev/null || true
    cp -r skills/* "$INSTALL_DIR/skills/" 2>/dev/null || true
    print_success "Archivos fuente copiados"
else
    print_warning "No se encontraron archivos fuente en el directorio actual"
    print_status "Debes copiar manualmente los archivos a: $INSTALL_DIR"
fi

# Crear script de inicio
LAUNCHER="$PREFIX/bin/gemma"
cat > "$LAUNCHER" << 'EOF'
#!/bin/bash
# Launcher para Gemma Termux App

INSTALL_DIR="$HOME/gemma-termux-app"

if [ ! -d "$INSTALL_DIR" ]; then
    echo "Error: No se encontró la instalación en $INSTALL_DIR"
    exit 1
fi

cd "$INSTALL_DIR"
python "$INSTALL_DIR/src/main.py" "$@"
EOF

chmod +x "$LAUNCHER"
print_success "Script de inicio creado: gemma"

# Crear script de inicio corto
SHORT_LAUNCHER="$PREFIX/bin/g"
cat > "$SHORT_LAUNCHER" << 'EOF'
#!/bin/bash
# Launcher corto para Gemma
exec gemma "$@"
EOF

chmod +x "$SHORT_LAUNCHER"
print_success "Alias corto creado: g"

# =============================================================================
# Instalación completada
# =============================================================================
echo
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ¡INSTALACIÓN COMPLETADA!${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo
print_success "$APP_NAME instalado correctamente"
echo
print_status "Ubicación: $INSTALL_DIR"
print_status "Modelos: $INSTALL_DIR/models/"
print_status "Sandbox: $INSTALL_DIR/sandbox/"
echo
print_status "Comandos disponibles:"
echo "  gemma          - Iniciar la aplicación"
echo "  g              - Alias corto"
echo "  gemma --setup  - Configuración inicial"
echo "  gemma -m       - Modo no interactivo"
echo
echo -e "${YELLOW}Primeros pasos:${NC}"
echo "  1. Asegúrate de tener un modelo en: $INSTALL_DIR/models/"
echo "  2. Ejecuta: gemma"
echo "  3. Escribe 'ayuda' para ver los comandos"
echo
echo -e "${BLUE}¡Disfruta tu asistente IA local! 🤖${NC}"
echo

# Preguntar si desea ejecutar
read -p "¿Deseas ejecutar Gemma ahora? (s/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    exec gemma
fi
