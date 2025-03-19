import random

def generate_game_response(game_name):
    responses = [
        f"¡Prepárate, jugador! Estás a punto de descubrir todos los secretos sobre {game_name}. 🕹️",
        f"Cargando datos de {game_name}... Espero que tu barra de HP esté llena, porque esto será épico. 🎮",
        f"¡Alerta de misión! Has solicitado información sobre {game_name}. Aquí viene una oleada de datos. 🚀",
        f"¡Power-Up! Desbloqueando detalles sobre {game_name}, no olvides equipar tu mejor estrategia. 🏆",
        f"Revisando la base de datos de videojuegos... {game_name} encontrado. ¡Vamos a explorarlo juntos! 🔎"
    ]
    return random.choice(responses)

def generate_no_results_response():
    responses = [
        "Oh no... Parece que este juego está escondido en una mazmorra secreta. ¡Intenta con otro nombre! ⚔️",
        "404: Juego no encontrado. Pero no te preocupes, sigue explorando y seguro que lo encontramos. 🚀",
        "Tu búsqueda ha caído en un portal dimensional vacío... ¿Quizás una ortografía diferente ayudaría? ✨",
        "Misión fallida... No encontramos ese juego. ¡Inténtalo de nuevo con otro título! 🎮",
        "Este juego parece tan raro como un easter egg bien escondido. ¡Prueba con otro! 🥚"
    ]
    return random.choice(responses)