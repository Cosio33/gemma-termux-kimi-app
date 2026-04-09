# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.0.0] - 2024-01-XX

### Añadido
- Implementación inicial de Gemma Termux App
- Inferencia local usando llama.cpp
- Soporte para modelos Gemma 2B, 4B y 7B
- Sistema de memoria persistente con SQLite
- Sistema de skills extensible con carga dinámica
- Sandbox de archivos seguro
- Interfaz de chat interactiva
- Modo no interactivo para scripts

### Skills Incluidos
- **calculator**: Operaciones matemáticas y conversiones
- **system**: Utilidades del sistema Android/Termux
- **code_utils**: Análisis y manipulación de código
- **network**: Herramientas de red y conectividad
- **time_utils**: Fechas, horas y temporizadores
- **weather**: Información meteorológica
- **fun**: Juegos y utilidades divertidas

### Comandos
- `recuerda`, `busca`, `memorias` - Gestión de memoria
- `archivo [crear|leer|escribir|listar|eliminar|info]` - Sandbox
- `ayuda`, `limpiar`, `modelo`, `stats`, `reload` - Control

### Características
- Historial de conversaciones persistente
- Búsqueda en memoria a largo plazo
- Estadísticas de uso
- Configuración flexible
- Colores en terminal
- Scripts de instalación y actualización

### Documentación
- README completo en español
- Guía de instalación manual y automática
- Documentación de comandos
- Guía para crear skills personalizados
- Solución de problemas

## [Unreleased]

### Planeado
- [ ] Soporte para más modelos (Llama, Mistral, Phi)
- [ ] Interfaz web opcional
- [ ] Sincronización entre dispositivos
- [ ] Exportar/importar conversaciones
- [ ] Integración con APIs de Termux adicionales
- [ ] Soporte para plugins en otros lenguajes
- [ ] Modo servidor API REST
- [ ] Aplicación complementaria para GUI
