#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill: Diversión y Entretenimiento
Juegos, chistes, y utilidades divertidas
"""

import random
import json
from typing import Any


def roll(dice: str = "1d6") -> str:
    """
    Lanza dados.
    
    Args:
        dice: Formato NdM (N dados de M caras), ej: "2d6", "1d20"
    
    Returns:
        Resultado de la tirada
    """
    try:
        # Parsear formato NdM
        parts = dice.lower().split('d')
        if len(parts) != 2:
            return "Formato inválido. Usa: NdM (ej: 2d6, 1d20)"
        
        num_dice = int(parts[0]) if parts[0] else 1
        num_sides = int(parts[1])
        
        if num_dice < 1 or num_dice > 100:
            return "Número de dados debe ser entre 1 y 100"
        
        if num_sides < 2 or num_sides > 1000:
            return "Número de caras debe ser entre 2 y 1000"
        
        # Lanzar dados
        results = [random.randint(1, num_sides) for _ in range(num_dice)]
        total = sum(results)
        
        if num_dice == 1:
            return f"🎲 {dice}: {total}"
        else:
            return f"🎲 {dice}: {results} = {total}"
            
    except ValueError:
        return "Error: Usa formato NdM (ej: 2d6)"


def coin() -> str:
    """
    Lanza una moneda.
    
    Returns:
        Resultado del lanzamiento
    """
    result = random.choice(['Cara', 'Cruz'])
    emoji = '🪙' if result == 'Cara' else '❌'
    return f"{emoji} {result}"


def random_number(min_val: str = "1", max_val: str = "100") -> str:
    """
    Genera número aleatorio.
    
    Args:
        min_val: Valor mínimo
        max_val: Valor máximo
    
    Returns:
        Número aleatorio
    """
    try:
        min_v = int(min_val)
        max_v = int(max_val)
        
        if min_v >= max_v:
            return "Error: min debe ser menor que max"
        
        result = random.randint(min_v, max_v)
        return f"🎲 Número aleatorio ({min_v}-{max_v}): {result}"
        
    except ValueError:
        return "Error: Los valores deben ser números enteros"


def choose(*options) -> str:
    """
    Elige aleatoriamente entre opciones.
    
    Args:
        options: Opciones a elegir
    
    Returns:
        Opción seleccionada
    """
    if len(options) < 2:
        return "Proporciona al menos 2 opciones"
    
    # Si viene como string separado por comas o espacios
    if len(options) == 1 and isinstance(options[0], str):
        # Intentar separar por comas
        if ',' in options[0]:
            options = [opt.strip() for opt in options[0].split(',')]
        else:
            options = options[0].split()
    
    choice = random.choice(options)
    return f"🎯 Elegido: {choice}"


def joke() -> str:
    """
    Cuenta un chiste.
    
    Returns:
        Chiste aleatorio
    """
    jokes = [
        "¿Por qué los programadores prefieren el frío? Porque tienen muchos problemas con el calor de los servidores.",
        "¿Qué le dice un bit al otro? Nos vemos en el bus.",
        "¿Por qué los desarrolladores web no pueden jugar al escondite? Porque siempre dejan rastros en el DOM.",
        "Un SQL entra a un bar, se acerca a dos mesas y pregunta: '¿Puedo unirme?'",
        "¿Cuántos programadores hacen falta para cambiar una bombilla? Ninguno, es un problema de hardware.",
        "¿Por qué Java no puede ver bien? Porque no tiene C#.",
        "¿Qué es un terapeuta? 1024 gigapeutas.",
        "Hay 10 tipos de personas: las que entienden binario y las que no.",
        "¿Por qué los programadores confunden Halloween con Navidad? Porque OCT 31 = DEC 25.",
        "Un programador va al supermercado. Su mujer le dice: 'Compra una leche y si hay huevos, compra 6.' Vuelve con 6 leches. '¿Por qué 6 leches?' 'Porque había huevos.'",
        "¿Qué hace un pez en la computadora? Nada.",
        "¿Por qué la computadora fue al médico? Porque tenía un virus.",
        "¿Cuál es el animal más antiguo? La cebra, porque está en blanco y negro.",
        "¿Qué le dice una iguana a su hermana gemela? Iguanita.",
        "¿Por qué las focas miran siempre hacia arriba? ¡Porque ahí están los focos!",
    ]
    
    return f"😄 {random.choice(jokes)}"


def fortune() -> str:
    """
    Muestra una fortuna/horóscopo divertido.
    
    Returns:
        Fortuna aleatoria
    """
    fortunes = [
        "Hoy es un buen día para codear. Tu código compilará a la primera.",
        "Un bug aparecerá donde menos lo esperas. Mantén la calma y debuggea.",
        "Grandes cambios vienen en tu próximo commit. Haz push con confianza.",
        "La documentación que buscas está en el código fuente. Léelo.",
        "Un PR será aprobado pronto. Prepara tus tests.",
        "El café de hoy será extraordinario. Aprovéchalo.",
        "Stack Overflow tendrá la respuesta que buscas. Pregunta bien.",
        "Tu próxima reunión será productiva. Toma notas.",
        "Un nuevo framework aparecerá. Evalúalo antes de adoptarlo.",
        "El código legacy te enseñará valiosas lecciones. Respétalo.",
        "Hoy es día de refactoring. Mejora ese código.",
        "Un colega te ayudará con un problema difícil. Acepta la ayuda.",
        "Tu creatividad está en su punto máximo. Dibuja un diagrama.",
        "El cliente finalmente entenderá lo que quiere. Escúchalo.",
        "Un día sin errores de compilación te espera. Disfrútalo.",
    ]
    
    lucky_numbers = [random.randint(1, 99) for _ in range(3)]
    
    result = [
        "🔮 TU FORTUNA DE HOY",
        "═" * 40,
        random.choice(fortunes),
        "",
        f"🍀 Números de la suerte: {', '.join(map(str, lucky_numbers))}",
    ]
    
    return "\n".join(result)


def riddle() -> str:
    """
    Muestra un acertijo.
    
    Returns:
        Acertijo aleatorio
    """
    riddles = [
        ("Tengo agujas pero no coso, tengo números pero no llamo. ¿Qué soy?", "Un reloj"),
        ("Blanco es, gallina lo pone, con aceite se fríe y con pan se come. ¿Qué es?", "Un huevo"),
        ("Oro no es, plata no es, ábreme y verás. ¿Qué es?", "Un huevo"),
        ("Tiene dientes pero no come, tiene cabeza pero no es hombre. ¿Qué es?", "Un ajo"),
        ("Vuela sin alas, silba sin boca, si no la sigues, se pierde en la brota. ¿Qué es?", "El viento"),
        ("Tiene ojos pero no ve, tiene agua pero no bebe. ¿Qué es?", "Una papa"),
        ("¿Qué es lo que cuanto más le quitas, más grande es?", "Un agujero"),
        ("Tiene raíces invisible, es más alta que un árbol. ¿Qué es?", "Una montaña"),
        ("¿Qué pesa más, un kilo de plumas o un kilo de hierro?", "Pesan lo mismo"),
        ("Tiene ciudades pero no casas, montañas pero no árboles, agua pero no peces. ¿Qué es?", "Un mapa"),
    ]
    
    question, answer = random.choice(riddles)
    
    return f"🤔 ACERTIJO:\n{question}\n\n💡 Respuesta: ||{answer}|| (selecciona para ver)"


def ascii_art(text: str = "Gemma") -> str:
    """
    Genera arte ASCII simple.
    
    Args:
        text: Texto a convertir
    
    Returns:
        Arte ASCII
    """
    # Fuente simple de bloques
    font = {
        'A': ['  ██  ', ' ████ ', '██  ██', '██████', '██  ██', '██  ██'],
        'B': ['█████ ', '██  ██', '█████ ', '██  ██', '██  ██', '█████ '],
        'C': [' █████', '██    ', '██    ', '██    ', '██    ', ' █████'],
        'D': ['████  ', '██ ██ ', '██  ██', '██  ██', '██ ██ ', '████  '],
        'E': ['██████', '██    ', '████  ', '██    ', '██    ', '██████'],
        'F': ['██████', '██    ', '████  ', '██    ', '██    ', '██    '],
        'G': [' █████', '██    ', '██ ███', '██  ██', '██  ██', ' █████'],
        'H': ['██  ██', '██  ██', '██████', '██  ██', '██  ██', '██  ██'],
        'I': ['██████', '  ██  ', '  ██  ', '  ██  ', '  ██  ', '██████'],
        'J': ['██████', '   ██ ', '   ██ ', '   ██ ', '██ ██ ', ' ███  '],
        'K': ['██  ██', '██ ██ ', '████  ', '██ ██ ', '██  ██', '██  ██'],
        'L': ['██    ', '██    ', '██    ', '██    ', '██    ', '██████'],
        'M': ['██   ██', '███ ███', '███████', '██ █ ██', '██   ██', '██   ██'],
        'N': ['██  ██', '███ ██', '██████', '██ ███', '██  ██', '██  ██'],
        'O': [' ████ ', '██  ██', '██  ██', '██  ██', '██  ██', ' ████ '],
        'P': ['█████ ', '██  ██', '██  ██', '█████ ', '██    ', '██    '],
        'Q': [' ████ ', '██  ██', '██  ██', '██  ██', '██ ██ ', ' █████'],
        'R': ['█████ ', '██  ██', '██  ██', '█████ ', '██ ██ ', '██  ██'],
        'S': [' █████', '██    ', ' ████ ', '    ██', '    ██', '█████ '],
        'T': ['██████', '  ██  ', '  ██  ', '  ██  ', '  ██  ', '  ██  '],
        'U': ['██  ██', '██  ██', '██  ██', '██  ██', '██  ██', ' ████ '],
        'V': ['██  ██', '██  ██', '██  ██', '██  ██', ' ████ ', '  ██  '],
        'W': ['██   ██', '██   ██', '██   ██', '██ █ ██', '███ ███', '██   ██'],
        'X': ['██  ██', '██  ██', ' ████ ', ' ████ ', '██  ██', '██  ██'],
        'Y': ['██  ██', '██  ██', ' ████ ', '  ██  ', '  ██  ', '  ██  '],
        'Z': ['██████', '   ██ ', '  ██  ', ' ██   ', '██    ', '██████'],
        ' ': ['      ', '      ', '      ', '      ', '      ', '      '],
    }
    
    text = text.upper()
    lines = ['' for _ in range(6)]
    
    for char in text:
        if char in font:
            for i in range(6):
                lines[i] += font[char][i] + '  '
        else:
            for i in range(6):
                lines[i] += '      '
    
    return '\n'.join(lines)


def magic_8ball(question: str = None) -> str:
    """
    Bola 8 mágica.
    
    Args:
        question: Pregunta (opcional)
    
    Returns:
        Respuesta mística
    """
    responses = [
        "🎱 Es cierto",
        "🎱 Es decididamente así",
        "🎱 Sin lugar a dudas",
        "🎱 Sí, definitivamente",
        "🎱 Puedes confiar en ello",
        "🎱 Como yo lo veo, sí",
        "🎱 Lo más probable",
        "🎱 Perspectiva buena",
        "🎱 Sí",
        "🎱 Las señales apuntan a que sí",
        "🎱 Respuesta confusa, intenta de nuevo",
        "🎱 Pregunta de nuevo más tarde",
        "🎱 Mejor no decirte ahora",
        "🎱 No se puede predecir ahora",
        "🎱 Concéntrate y pregunta de nuevo",
        "🎱 No cuentes con ello",
        "🎱 Mi respuesta es no",
        "🎱 Mis fuentes dicen que no",
        "🎱 Las perspectivas no son buenas",
        "🎱 Muy dudoso",
    ]
    
    result = [random.choice(responses)]
    
    if question:
        result.insert(0, f"❓ {question}")
    
    return "\n".join(result)


def rock_paper_scissors(choice: str = None) -> str:
    """
    Juega piedra, papel o tijeras.
    
    Args:
        choice: Tu elección (piedra/papel/tijeras)
    
    Returns:
        Resultado del juego
    """
    options = ['piedra', 'papel', 'tijeras']
    emojis = {'piedra': '✊', 'papel': '✋', 'tijeras': '✌️'}
    
    if choice is None:
        return f"Juega: rock_paper_scissors [{'/'.join(options)}]"
    
    choice = choice.lower()
    
    if choice not in options:
        return f"Opción inválida. Usa: {', '.join(options)}"
    
    computer_choice = random.choice(options)
    
    # Determinar ganador
    if choice == computer_choice:
        result = "¡Empate!"
        emoji = "🤝"
    elif (
        (choice == 'piedra' and computer_choice == 'tijeras') or
        (choice == 'papel' and computer_choice == 'piedra') or
        (choice == 'tijeras' and computer_choice == 'papel')
    ):
        result = "¡Ganaste!"
        emoji = "🎉"
    else:
        result = "¡Perdiste!"
        emoji = "😢"
    
    return f"Tú: {emojis[choice]} {choice}\nYo: {emojis[computer_choice]} {computer_choice}\n\n{emoji} {result}"


def password(length: str = "12") -> str:
    """
    Genera contraseña segura.
    
    Args:
        length: Longitud de la contraseña
    
    Returns:
        Contraseña generada
    """
    try:
        length = int(length)
        if length < 4 or length > 128:
            return "Longitud debe ser entre 4 y 128"
    except ValueError:
        return "Longitud debe ser un número"
    
    import string
    
    # Caracteres para la contraseña
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Asegurar al menos uno de cada tipo
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(special),
    ]
    
    # Rellenar el resto
    all_chars = lowercase + uppercase + digits + special
    for _ in range(length - 4):
        password.append(random.choice(all_chars))
    
    # Mezclar
    random.shuffle(password)
    
    return f"🔐 Contraseña ({length} chars): {''.join(password)}"


# Definición de comandos exportados
COMMANDS = {
    'roll': roll,
    'coin': coin,
    'random_number': random_number,
    'choose': choose,
    'joke': joke,
    'fortune': fortune,
    'riddle': riddle,
    'ascii_art': ascii_art,
    'magic_8ball': magic_8ball,
    'rock_paper_scissors': rock_paper_scissors,
    'password': password,
}


# Información del skill
SKILL_INFO = {
    'name': 'Fun',
    'description': 'Juegos, diversión y utilidades entretenidas',
    'version': '1.0',
    'author': 'Gemma Termux App',
    'commands': list(COMMANDS.keys())
}


def info():
    """Retorna información del skill"""
    return SKILL_INFO
