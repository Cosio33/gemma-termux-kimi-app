#!/bin/bash
# =============================================================================
# Gemma Termux App - Script de Corrección de llama.cpp
# Recompila llama.cpp desde fuente para soportar Gemma 4
# =============================================================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     CORRECCIÓN DE LLAMA.CPP PARA GEMMA 4                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

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
    print_warning "No parece que estés en Termux."
    read -p "¿Continuar de todos modos? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

echo
print_status "Este script recompilará llama.cpp desde la fuente más reciente"
print_status "para asegurar compatibilidad con los modelos Gemma 4."
echo

# Desinstalar versión antigua si existe
if dpkg -l | grep -q "^ii  llama-cpp "; then
    print_status "Desinstalando llama-cpp del repositorio..."
    apt remove -y llama-cpp 2>/dev/null || true
fi

# Eliminar binarios antiguos
if [ -f "$PREFIX/bin/llama-cli" ]; then
    print_status "Eliminando binarios antiguos..."
    rm -f "$PREFIX/bin/llama-cli"
    rm -f "$PREFIX/bin/llama-server"
fi

# Eliminar compilación anterior
if [ -d "$HOME/llama.cpp" ]; then
    print_status "Eliminando compilación anterior..."
    rm -rf "$HOME/llama.cpp"
fi

# Instalar dependencias
print_status "Instalando dependencias de compilación..."
apt update -y > /dev/null 2>&1 || true
apt install -y git cmake clang 2>/dev/null || {
    print_error "No se pudieron instalar dependencias"
    exit 1
}

# Clonar repositorio
print_status "Clonando llama.cpp..."
cd "$HOME"
git clone --depth 1 https://github.com/ggerganov/llama.cpp.git

cd llama.cpp

# Compilar
print_status "Compilando llama.cpp..."
print_status "Esto puede tardar 5-15 minutos según tu dispositivo..."
echo

cmake -B build -DCMAKE_BUILD_TYPE=Release 2>/dev/null || {
    print_error "Error configurando con cmake"
    exit 1
}

cmake --build build --config Release -j$(nproc) 2>/dev/null || {
    print_warning "Compilación paralela falló, intentando secuencial..."
    cmake --build build --config Release
}

# Verificar binario
if [ ! -f "$HOME/llama.cpp/build/bin/llama-cli" ]; then
    print_error "No se encontró el binario compilado"
    exit 1
fi

# Crear enlaces simbólicos
ln -sf "$HOME/llama.cpp/build/bin/llama-cli" "$PREFIX/bin/llama-cli"
ln -sf "$HOME/llama.cpp/build/bin/llama-server" "$PREFIX/bin/llama-server" 2>/dev/null || true

# Verificar instalación
echo
print_status "Verificando instalación..."
if command -v llama-cli &> /dev/null; then
    VERSION=$(llama-cli --version 2>&1 | head -1)
    print_success "llama.cpp instalado correctamente"
    print_status "Versión: $VERSION"
else
    print_error "No se pudo verificar la instalación"
    exit 1
fi

echo
print_success "¡Corrección completada!"
echo
print_status "Ahora puedes usar Gemma Termux App con modelos Gemma 4"
echo "  Ejecuta: gemma"
echo
