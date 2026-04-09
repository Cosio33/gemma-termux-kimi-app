#!/bin/bash
# =============================================================================
# Gemma Termux App - Script de Descarga de Modelos
# Descarga modelos GGUF de Gemma 4 para usar con la app
# =============================================================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Directorio de modelos
MODELS_DIR="${MODELS_DIR:-$HOME/gemma-termux-app/models}"
mkdir -p "$MODELS_DIR"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          DESCARGA DE MODELOS GEMMA 4 (GGUF)                  ║"
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

# Función para descargar con progreso
download_model() {
    local url="$1"
    local output="$2"
    local desc="$3"
    
    print_status "Descargando: $desc"
    print_status "URL: $url"
    print_status "Destino: $output"
    echo
    
    if wget --show-progress -O "$output" "$url" 2>&1; then
        print_success "Descarga completada: $(basename $output)"
        return 0
    else
        print_error "Error descargando el modelo"
        rm -f "$output"  # Limpiar archivo parcial
        return 1
    fi
}

# Menú de selección
show_menu() {
    echo
    echo -e "${CYAN}Modelos disponibles:${NC}"
    echo
    echo "📱 ESPECIALES PARA ANDROID:"
    echo "  1) Gemma 4 E2B-IT Q4_K_M  (~1.5GB) - Móvil básico"
    echo "  2) Gemma 4 E4B-IT Q4_K_M  (~2.6GB) - RECOMENDADO ✓"
    echo "  3) Gemma 4 E4B-IT Q5_K_M  (~3.2GB) - Mejor calidad"
    echo
    echo "📊 ESTÁNDAR:"
    echo "  4) Gemma 4 4B-IT Q4_K_M   (~2.5GB) - Balance"
    echo "  5) Gemma 4 4B-IT Q5_K_M   (~3.1GB) - Mejor calidad"
    echo "  6) Gemma 4 12B-IT Q4_K_M  (~7GB)   - Alta calidad"
    echo
    echo "⚡ ULTRA LIGERO:"
    echo "  7) Gemma 4 E2B-IT IQ4_XS  (~1.2GB) - Mínimo tamaño"
    echo
    echo "  0) Salir"
    echo
}

# URLs de modelos
get_model_url() {
    case $1 in
        1)
            echo "https://huggingface.co/unsloth/gemma-4-e2b-it-GGUF/resolve/main/gemma-4-e2b-it-Q4_K_M.gguf"
            ;;
        2)
            echo "https://huggingface.co/lmstudio-community/gemma-4-E4B-it-GGUF/resolve/main/gemma-4-E4B-it-Q4_K_M.gguf"
            ;;
        3)
            echo "https://huggingface.co/lmstudio-community/gemma-4-E4B-it-GGUF/resolve/main/gemma-4-E4B-it-Q5_K_M.gguf"
            ;;
        4)
            echo "https://huggingface.co/unsloth/gemma-4-4b-it-GGUF/resolve/main/gemma-4-4b-it-Q4_K_M.gguf"
            ;;
        5)
            echo "https://huggingface.co/unsloth/gemma-4-4b-it-GGUF/resolve/main/gemma-4-4b-it-Q5_K_M.gguf"
            ;;
        6)
            echo "https://huggingface.co/unsloth/gemma-4-12b-it-GGUF/resolve/main/gemma-4-12b-it-Q4_K_M.gguf"
            ;;
        7)
            echo "https://huggingface.co/unsloth/gemma-4-e2b-it-GGUF/resolve/main/gemma-4-e2b-it-IQ4_XS.gguf"
            ;;
        *)
            echo ""
            ;;
    esac
}

get_model_name() {
    case $1 in
        1) echo "gemma-4-e2b-it-Q4_K_M.gguf" ;;
        2) echo "gemma-4-E4B-it-Q4_K_M.gguf" ;;
        3) echo "gemma-4-E4B-it-Q5_K_M.gguf" ;;
        4) echo "gemma-4-4b-it-Q4_K_M.gguf" ;;
        5) echo "gemma-4-4b-it-Q5_K_M.gguf" ;;
        6) echo "gemma-4-12b-it-Q4_K_M.gguf" ;;
        7) echo "gemma-4-e2b-it-IQ4_XS.gguf" ;;
        *) echo "" ;;
    esac
}

get_model_desc() {
    case $1 in
        1) echo "Gemma 4 E2B-IT Q4_K_M (2B params, ~1.5GB)" ;;
        2) echo "Gemma 4 E4B-IT Q4_K_M (4B params, ~2.6GB) - RECOMENDADO" ;;
        3) echo "Gemma 4 E4B-IT Q5_K_M (4B params, ~3.2GB)" ;;
        4) echo "Gemma 4 4B-IT Q4_K_M (4B params, ~2.5GB)" ;;
        5) echo "Gemma 4 4B-IT Q5_K_M (4B params, ~3.1GB)" ;;
        6) echo "Gemma 4 12B-IT Q4_K_M (12B params, ~7GB)" ;;
        7) echo "Gemma 4 E2B-IT IQ4_XS (2B params, ~1.2GB)" ;;
        *) echo "" ;;
    esac
}

# Verificar espacio disponible
check_space() {
    local required_gb="$1"
    local available_kb=$(df "$MODELS_DIR" | tail -1 | awk '{print $4}')
    local available_gb=$((available_kb / 1024 / 1024))
    
    if [ "$available_gb" -lt "$required_gb" ]; then
        print_error "Espacio insuficiente: ${available_gb}GB disponible, ${required_gb}GB requeridos"
        return 1
    fi
    
    print_status "Espacio disponible: ${available_gb}GB"
    return 0
}

# Main
main() {
    # Verificar argumentos
    if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
        echo "Uso: $0 [opción]"
        echo
        echo "Descarga modelos Gemma 4 en formato GGUF para Gemma Termux App"
        echo
        echo "Opciones:"
        echo "  1-7    Descargar modelo específico"
        echo "  --list Mostrar lista de modelos"
        echo "  -h     Mostrar esta ayuda"
        echo
        echo "Ejemplos:"
        echo "  $0 2        # Descargar Gemma 4 E4B-IT Q4_K_M (recomendado)"
        echo "  $0 1        # Descargar Gemma 4 E2B-IT (ligero)"
        exit 0
    fi
    
    if [ "$1" == "--list" ]; then
        show_menu
        exit 0
    fi
    
    # Si se proporciona número directamente
    if [ -n "$1" ] && [ "$1" -eq "$1" ] 2>/dev/null; then
        choice="$1"
    else
        # Mostrar menú interactivo
        show_menu
        read -p "Selecciona una opción (0-7): " choice
    fi
    
    # Validar opción
    if [ "$choice" == "0" ]; then
        echo "Saliendo..."
        exit 0
    fi
    
    if [ "$choice" -lt 1 ] || [ "$choice" -gt 7 ]; then
        print_error "Opción inválida"
        exit 1
    fi
    
    # Obtener información del modelo
    MODEL_URL=$(get_model_url "$choice")
    MODEL_NAME=$(get_model_name "$choice")
    MODEL_DESC=$(get_model_desc "$choice")
    
    # Estimar tamaño
    case $choice in
        1) REQUIRED_GB=2 ;;
        2) REQUIRED_GB=3 ;;
        3) REQUIRED_GB=4 ;;
        4) REQUIRED_GB=3 ;;
        5) REQUIRED_GB=4 ;;
        6) REQUIRED_GB=8 ;;
        7) REQUIRED_GB=2 ;;
    esac
    
    echo
    print_status "Modelo seleccionado: $MODEL_DESC"
    print_status "Directorio destino: $MODELS_DIR"
    
    # Verificar espacio
    if ! check_space "$REQUIRED_GB"; then
        print_error "No hay suficiente espacio para descargar el modelo"
        exit 1
    fi
    
    # Confirmar descarga
    echo
    read -p "¿Comenzar descarga? (s/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        print_status "Descarga cancelada"
        exit 0
    fi
    
    # Descargar
    echo
    OUTPUT_FILE="$MODELS_DIR/$MODEL_NAME"
    
    if download_model "$MODEL_URL" "$OUTPUT_FILE" "$MODEL_DESC"; then
        echo
        print_success "¡Modelo descargado exitosamente!"
        print_status "Ubicación: $OUTPUT_FILE"
        
        # Crear enlace simbólico como modelo por defecto
        DEFAULT_LINK="$MODELS_DIR/gemma-default.gguf"
        ln -sf "$MODEL_NAME" "$DEFAULT_LINK" 2>/dev/null || true
        print_success "Modelo configurado como predeterminado"
        
        # Verificar integridad (tamaño mínimo)
        FILE_SIZE=$(stat -c%s "$OUTPUT_FILE" 2>/dev/null || stat -f%z "$OUTPUT_FILE" 2>/dev/null)
        if [ "$FILE_SIZE" -lt 100000000 ]; then
            print_warning "El archivo parece muy pequeño. Posible error en la descarga."
        fi
        
        echo
        print_status "Para usar el modelo, ejecuta: gemma"
    else
        echo
        print_error "La descarga falló"
        print_status "Puedes intentar descargar manualmente:"
        echo "  wget $MODEL_URL -O $OUTPUT_FILE"
        exit 1
    fi
}

# Ejecutar
main "$@"
