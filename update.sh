#!/bin/bash
# =============================================================================
# Gemma Termux App - Script de Actualización
# =============================================================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_DIR="$HOME/gemma-termux-app"
BACKUP_DIR="$HOME/.gemma-backups"

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              GEMMA TERMUX APP - ACTUALIZACIÓN                ║"
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

# Verificar instalación
if [ ! -d "$INSTALL_DIR" ]; then
    print_error "No se encontró instalación en $INSTALL_DIR"
    echo "Ejecuta el instalador primero:"
    echo "  bash install.sh"
    exit 1
fi

# Obtener versión actual
if [ -f "$INSTALL_DIR/.version" ]; then
    CURRENT_VERSION=$(cat "$INSTALL_DIR/.version")
else
    CURRENT_VERSION="desconocida"
fi

print_status "Versión actual: $CURRENT_VERSION"

# =============================================================================
# PASO 1: Crear backup
# =============================================================================
print_status "Paso 1/5: Creando backup..."

mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).tar.gz"

tar -czf "$BACKUP_FILE" -C "$HOME" gemma-termux-app 2>/dev/null || {
    print_warning "No se pudo crear backup completo, intentando backup selectivo..."
    mkdir -p "$BACKUP_DIR/selective-$(date +%Y%m%d-%H%M%S)"
    cp -r "$INSTALL_DIR/sandbox" "$BACKUP_DIR/selective-$(date +%Y%m%d-%H%M%S)/" 2>/dev/null || true
    cp "$INSTALL_DIR/memory.db" "$BACKUP_DIR/selective-$(date +%Y%m%d-%H%M%S)/" 2>/dev/null || true
}

print_success "Backup creado"

# =============================================================================
# PASO 2: Descargar actualización
# =============================================================================
print_status "Paso 2/5: Descargando actualización..."

TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Intentar descargar desde GitHub
if command -v git &> /dev/null; then
    git clone --depth 1 https://github.com/tu-repo/gemma-termux-app.git 2>/dev/null || {
        print_warning "No se pudo clonar desde GitHub"
    }
fi

if [ -d "gemma-termux-app" ]; then
    print_success "Actualización descargada"
else
    print_error "No se pudo descargar la actualización"
    echo "Verifica tu conexión a internet"
    exit 1
fi

# =============================================================================
# PASO 3: Preservar datos del usuario
# =============================================================================
print_status "Paso 3/5: Preservando datos del usuario..."

# Guardar archivos importantes
USER_DATA_DIR=$(mktemp -d)
cp -r "$INSTALL_DIR/sandbox" "$USER_DATA_DIR/" 2>/dev/null || true
cp "$INSTALL_DIR/memory.db" "$USER_DATA_DIR/" 2>/dev/null || true
cp "$INSTALL_DIR/models"/*.gguf "$USER_DATA_DIR/" 2>/dev/null || true

print_success "Datos preservados"

# =============================================================================
# PASO 4: Actualizar archivos
# =============================================================================
print_status "Paso 4/5: Actualizando archivos..."

# Preservar configuración personalizada
if [ -f "$INSTALL_DIR/config/user.conf" ]; then
    cp "$INSTALL_DIR/config/user.conf" "$USER_DATA_DIR/" 2>/dev/null || true
fi

# Actualizar archivos fuente
rm -rf "$INSTALL_DIR/src"
rm -rf "$INSTALL_DIR/skills"
cp -r "$TEMP_DIR/gemma-termux-app/src" "$INSTALL_DIR/"
cp -r "$TEMP_DIR/gemma-termux-app/skills" "$INSTALL_DIR/"

# Actualizar otros archivos
for file in install.sh update.sh README.md requirements.txt; do
    if [ -f "$TEMP_DIR/gemma-termux-app/$file" ]; then
        cp "$TEMP_DIR/gemma-termux-app/$file" "$INSTALL_DIR/" 2>/dev/null || true
    fi
done

# Actualizar versión
if [ -f "$TEMP_DIR/gemma-termux-app/.version" ]; then
    cp "$TEMP_DIR/gemma-termux-app/.version" "$INSTALL_DIR/"
fi

print_success "Archivos actualizados"

# =============================================================================
# PASO 5: Restaurar datos del usuario
# =============================================================================
print_status "Paso 5/5: Restaurando datos del usuario..."

# Restaurar sandbox
if [ -d "$USER_DATA_DIR/sandbox" ]; then
    cp -r "$USER_DATA_DIR/sandbox" "$INSTALL_DIR/" 2>/dev/null || true
fi

# Restaurar base de datos
if [ -f "$USER_DATA_DIR/memory.db" ]; then
    cp "$USER_DATA_DIR/memory.db" "$INSTALL_DIR/" 2>/dev/null || true
fi

# Restaurar configuración
if [ -f "$USER_DATA_DIR/user.conf" ]; then
    cp "$USER_DATA_DIR/user.conf" "$INSTALL_DIR/config/" 2>/dev/null || true
fi

print_success "Datos restaurados"

# =============================================================================
# Limpieza
# =============================================================================
print_status "Limpiando archivos temporales..."

rm -rf "$TEMP_DIR"
rm -rf "$USER_DATA_DIR"

# =============================================================================
# Finalización
# =============================================================================
echo
print_success "¡Actualización completada!"

# Mostrar nueva versión
if [ -f "$INSTALL_DIR/.version" ]; then
    NEW_VERSION=$(cat "$INSTALL_DIR/.version")
    print_status "Nueva versión: $NEW_VERSION"
fi

echo
print_status "Cambios en esta versión:"
echo "  - Ver CHANGELOG.md para detalles"
echo
print_status "Para iniciar la aplicación:"
echo "  gemma"
echo
print_status "Backup guardado en: $BACKUP_DIR"
echo
