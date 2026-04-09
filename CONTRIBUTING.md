# Contribuir a Gemma Termux App

¡Gracias por tu interés en contribuir a Gemma Termux App! Este documento proporciona guías para contribuir al proyecto.

## Cómo Contribuir

### Reportar Bugs

1. Verifica que el bug no haya sido reportado previamente
2. Abre un issue con el label `bug`
3. Incluye:
   - Descripción clara del problema
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Versión de la app y Termux
   - Logs o mensajes de error

### Sugerir Features

1. Abre un issue con el label `enhancement`
2. Describe claramente la funcionalidad propuesta
3. Explica el caso de uso
4. Considera implementarlo tú mismo

### Pull Requests

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Haz commits con mensajes claros
4. Push a tu fork (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Estilo de Código

### Python
- Sigue PEP 8
- Usa type hints cuando sea posible
- Documenta funciones con docstrings
- Máximo 100 caracteres por línea

### Skills
- Usa el template proporcionado
- Documenta todos los comandos
- Maneja errores gracefully
- No bloquees el hilo principal

## Estructura de Commits

```
tipo(alcance): descripción corta

descripción larga si es necesaria

Closes #123
```

Tipos:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Documentación
- `style`: Cambios de formato
- `refactor`: Refactorización
- `test`: Tests
- `chore`: Tareas de mantenimiento

## Testing

- Prueba tus cambios en Termux real
- Verifica que los skills carguen correctamente
- Comprueba compatibilidad con diferentes modelos

## Documentación

- Actualiza README.md si es necesario
- Documenta nuevos comandos
- Añade ejemplos de uso

## Código de Conducta

- Sé respetuoso
- Acepta críticas constructivas
- Enfócate en lo mejor para la comunidad

## Preguntas

¿Tienes dudas? Abre un issue con el label `question`.

¡Gracias por contribuir! 🎉
