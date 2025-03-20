import random

def generate_game_response(game_name):
    responses = [
        f"¡Prepárate, jugador! Estás a punto de descubrir todos los secretos sobre {game_name}. 🕹️",
        f"Cargando datos de {game_name}... Espero que tu barra de HP esté llena, porque esto será épico. 🎮",
        f"¡Alerta de misión! Has solicitado información sobre {game_name}. Aquí viene una oleada de datos. 🚀",
        f"¡Power-Up! Desbloqueando detalles sobre {game_name}, no olvides equipar tu mejor estrategia. 🏆",
        f"Revisando la base de datos de videojuegos... {game_name} encontrado. ¡Vamos a explorarlo juntos! 🔎",
        f"¡Atención! {game_name} está a punto de ser desvelado. Prepárate para la aventura. 🧙‍♂️",
        f"¡Cuidado! {game_name} está lleno de sorpresas. ¿Estás listo para enfrentarlas? ⚔️"
    ]
    return random.choice(responses)

def generate_no_results_response():
    responses = [
        "Oh no... Parece que este juego está escondido en una mazmorra secreta. ¡Intenta con otro nombre! ⚔️",
        "404: Juego no encontrado. Pero no te preocupes, sigue explorando y seguro que lo encontramos. 🚀",
        "Tu búsqueda ha caído en un portal dimensional vacío... ¿Quizás una ortografía diferente ayudaría? ✨",
        "Misión fallida... No encontramos ese juego. ¡Inténtalo de nuevo con otro título! 🎮",
        "Este juego parece tan raro como un easter egg bien escondido. ¡Prueba con otro! 🥚",
        "Parece que este juego está en otra dimensión. ¡Intenta de nuevo! 🌌",
        "No hay rastro de este juego en nuestras bases. ¿Quizás un nombre diferente? 🔍"
    ]
    return random.choice(responses)

def generate_end_conversation_response():
    responses = [
        "Gracias por jugar con nosotros. ¡Hasta la próxima! 🎉",
        "Fue un placer ayudarte. ¡Que tengas un gran día! 🌟",
        "Nos vemos en la próxima aventura. ¡Cuídate! 👋",
        "Espero que hayas encontrado lo que buscabas. ¡Adiós! 🖐️",
        "¡Hasta luego! Recuerda que siempre estamos aquí para ayudarte. 🛡️"
    ]
    return random.choice(responses)
