import random

def generate_game_response(game_name):
    responses = [
        f"¡Prepárate, jugador! Estás a punto de descubrir todos los secretos sobre {game_name}. 🕹️",
        f"Cargando datos de {game_name}... Espero que tu barra de HP esté llena, porque esto será épico. 🎮",
        f"¡Alerta de misión! Has solicitado información sobre {game_name}. Aquí viene una oleada de datos. 🚀",
        f"¡Power-Up! Desbloqueando detalles sobre {game_name}, no olvides equipar tu mejor estrategia. 🏆",
        f"Revisando la base de datos de videojuegos... {game_name} encontrado. ¡Vamos a explorarlo juntos! 🔎",
        f"¡Atención! {game_name} está a punto de ser desvelado. Prepárate para la aventura. 🧙‍♂️",
        f"¡Cuidado! {game_name} está lleno de sorpresas. ¿Estás listo para enfrentarlas? ⚔️",
        f"¡Listo para el desafío! {game_name} te espera con nuevas aventuras. 🗺️",
        f"¡Aventurero detectado! {game_name} está cargando, prepara tus habilidades. 🧭",
        f"¡En marcha! {game_name} está listo para ser explorado. ¡Buena suerte! 🍀",
        f"¡Espada en mano! {game_name} te espera con misterios por resolver. 🗡️",
        f"¡Desbloqueando niveles de {game_name}! Prepárate para lo inesperado. 🎲",
        f"¡Listo para una nueva misión! {game_name} tiene secretos que descubrirás. 🔍",
        f"¡Entra en el mundo de {game_name}! Tus habilidades serán puestas a prueba. 🛡️",
        f"¡Hora de jugar! {game_name} está cargando. ¿Estás listo para comenzar? 🎯",
        f"¡Ajusta tu equipo! {game_name} está listo para la acción. ⚙️",
        f"¡Listo para la aventura! {game_name} te espera con desafíos épicos. 🌟",
        f"¡Enciende tus motores! {game_name} está a punto de comenzar. 🚗",
        f"¡Prepara tus reflejos! {game_name} está por comenzar. 🏃‍♂️",
        f"¡Luz verde! {game_name} está listo para ser jugado. 🟢",
        f"¡Despega hacia {game_name}! La aventura te espera. 🚀",
        f"¡Hora de la verdad! {game_name} te desafía a ser el mejor. 🏆",
        f"¡Ajusta tu cinturón! {game_name} está a punto de comenzar. 🎢",
        f"¡Prepárate para el combate! {game_name} te espera. ⚔️",
        f"¡Explora lo desconocido! {game_name} tiene sorpresas para ti. 🗺️",
        f"¡Lucha por la victoria! {game_name} está a punto de comenzar. 🏅",
        f"¡Entra en el campo de batalla! {game_name} te espera. ⚔️",
        f"¡Aventura épica! {game_name} está listo para ser jugado. 🌄",
        f"¡Prepara tus habilidades! {game_name} está a punto de comenzar. 🛡️",
        f"¡Desafío aceptado! {game_name} te espera con grandes retos. 🏆",
        f"¡Entra en la arena! {game_name} está listo para la acción. 🏟️",
        f"¡Listo para la batalla! {game_name} te desafía. ⚔️",
        f"¡Explora nuevos mundos! {game_name} está cargando. 🌍",
        f"¡Ajusta tu visor! {game_name} está a punto de comenzar. 🎮",
        f"¡Prepara tu estrategia! {game_name} te espera con sorpresas. 🎯",
        f"¡Prepárate para la acción! {game_name} está listo para ser jugado. 🚀",
        f"¡Desbloquea tus habilidades! {game_name} te espera con desafíos. 🔓",
        f"¡Entra en el juego! {game_name} está listo para la aventura. 🎮",
        f"¡Listo para el reto! {game_name} te desafía a ser el mejor. 🏆",
        f"¡Explora el mundo de {game_name}! Sorpresas y aventuras te esperan. 🌍",
        f"¡Prepara tus armas! {game_name} está listo para la batalla. ⚔️",
        f"¡Desafío épico! {game_name} te espera con grandes retos. 🏆",
        f"¡Entra en la misión! {game_name} está listo para ser jugado. 🎮",
        f"¡Listo para la exploración! {game_name} te espera con sorpresas. 🔍"
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
        "No hay rastro de este juego en nuestras bases. ¿Quizás un nombre diferente? 🔍",
        "¡Vaya! Este juego es más esquivo que un fantasma. Prueba otra búsqueda. 👻",
        "No hemos podido encontrar ese juego. ¿Está seguro de que existe? 🤔",
        "Este título parece estar fuera de nuestro radar. ¡Inténtalo nuevamente! 📡",
        "No encontramos nada bajo ese nombre. ¿Podrías verificar la ortografía? 📝",
        "¡Juego no localizado! Tal vez esté usando un nombre alternativo. 🔄",
        "El juego que buscas es tan raro como un unicornio. ¡Prueba con otro! 🦄",
        "No hay señales de ese juego aquí. ¿Quizás un nombre diferente? 🔄",
        "Este juego parece estar oculto en las sombras. ¡Intenta de nuevo! 🌑",
        "¡Oh, no! Parece que este juego se ha perdido en el tiempo. ⏳",
        "No hemos encontrado el juego. ¿Podría ser un error tipográfico? 🖋️",
        "Este juego es tan escurridizo como un ninja. ¡Prueba con otro nombre! 🥷",
        "No hay rastro de este juego. ¿Quizás un nombre alternativo? 🔄",
        "¡Juego no encontrado! Tal vez esté usando un alias. 🕵️‍♂️",
        "El juego que buscas parece haber desaparecido. ¡Intenta de nuevo! 🌫️",
        "No hay señales de ese juego en nuestra galaxia. 🌌",
        "Este juego parece haber sido tragado por un agujero negro. 🕳️",
        "No encontramos el juego. ¿Podrías intentar otra búsqueda? 🔍",
        "¡Vaya! Este juego es más esquivo que un tesoro pirata. 🏴‍☠️",
        "Parece que este juego está en un mundo paralelo. ¡Intenta de nuevo! 🌐",
        "No hay información sobre este juego. ¿Quizás un nombre diferente? 📚",
        "Este juego parece estar en una dimensión desconocida. ¡Prueba con otro! 🔮",
        "No hemos encontrado el juego. ¿Podría ser un juego nuevo? 🎮",
        "Este juego parece estar en una realidad alternativa. ¡Intenta de nuevo! 🔀",
        "No hay señales de este juego en nuestro universo. 🌌",
        "Parece que este juego está en un estado de sueño. ¡Despiértalo! 😴",
        "No hemos encontrado el juego. ¿Quizás un nombre alternativo? 🔄",
        "Este juego parece estar en un laberinto infinito. ¡Explóralo! 🗺️",
        "No hay información sobre este juego. ¿Quizás un nombre diferente? 📊"
    ]
    return random.choice(responses)


def generate_end_conversation_response():
    responses = [
        "Gracias por jugar con nosotros. ¡Hasta la próxima! 🎉",
        "Fue un placer ayudarte. ¡Que tengas un gran día! 🌟",
        "Nos vemos en la próxima aventura. ¡Cuídate! 👋",
        "Espero que hayas encontrado lo que buscabas. ¡Adiós! 🖐️",
        "¡Hasta luego! Recuerda que siempre estamos aquí para ayudarte. 🛡️",
        "¡Gracias por tu tiempo! Esperamos verte pronto. 🕒",
        "¡Cuídate! Siempre estaremos aquí para tus aventuras futuras. 🌍",
        "¡Fue genial tenerte aquí! ¡Hasta la próxima! 🎊",
        "¡Nos vemos pronto! Que tengas un día increíble. ☀️",
        "¡Gracias por visitarnos! ¡Esperamos verte de nuevo! 🔙",
        "¡Hasta la próxima! Que tus días estén llenos de aventuras. 🏞️",
        "¡Adiós! Que la suerte te acompañe en tus viajes. 🍀",
        "¡Nos vemos! Siempre hay un nuevo juego esperando por ti. 🎮",
        "¡Hasta luego! Recuerda que siempre hay nuevas aventuras por descubrir. 🌌",
        "¡Fue un placer ayudarte! ¡Nos vemos en el próximo desafío! 🏆",
        "¡Gracias por tu visita! Esperamos verte pronto. 👋",
        "¡Cuídate! Que tus días estén llenos de alegría. 😊",
        "¡Hasta la próxima! Que la aventura continúe. 🚀",
        "¡Nos vemos pronto! Que tengas un día lleno de sorpresas. 🎈",
        "¡Adiós! Que cada día sea una nueva aventura. 🌟",
        "¡Gracias por estar con nosotros! Nos vemos en el futuro. 🔮",
        "¡Hasta luego! Que la fuerza te acompañe. 🌌",
        "¡Nos vemos! Que tus días estén llenos de magia. ✨",
        "¡Fue un placer! Que tengas un día espectacular. 🌞",
        "¡Hasta la próxima! Que tus sueños se hagan realidad. 🌠",
        "¡Gracias por compartir tu tiempo con nosotros! 🎉",
        "¡Nos vemos en la próxima! Que tengas un día lleno de éxitos. 🏆",
        "¡Hasta luego! Que la aventura nunca termine. 🌈",
        "¡Fue un honor ayudarte! Hasta la próxima. 🤝",
        "¡Nos vemos pronto! Que la suerte esté de tu lado. 🍀",
        "¡Adiós! Que cada día te traiga nuevas oportunidades. 🌅",
        "¡Gracias por tu visita! Esperamos verte de nuevo. 👋",
        "¡Hasta luego! Que la felicidad te acompañe siempre. 😊",
        "¡Nos vemos! Que tus sueños se hagan realidad. 🌠",
        "¡Fue un placer! Que tengas un día lleno de sorpresas. 🎈",
        "¡Gracias por tu tiempo! Esperamos verte pronto. 🕒",
        "¡Cuídate! Que tus días estén llenos de aventuras. 🏞️",
        "¡Hasta la próxima! Que la aventura continúe. 🚀",
        "¡Nos vemos pronto! Que tengas un día lleno de éxitos. 🏆",
        "¡Adiós! Que cada día sea una nueva aventura. 🌟",
        "¡Gracias por estar con nosotros! Nos vemos en el futuro. 🔮",
        "¡Hasta luego! Que la fuerza te acompañe. 🌌",
        "¡Nos vemos! Que tus días estén llenos de magia. ✨"
    ]
    return random.choice(responses)
