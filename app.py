import streamlit as st
import requests
from dotenv import load_dotenv
import os

# Cargar las variables del archivo .env
load_dotenv()

# Obtener la clave de API desde el archivo .env
API_KEY = os.getenv("GIANT_BOMB_API_KEY")

def get_game_info(game_name):
    # URL base de la API de Giant Bomb
    url = f"https://www.giantbomb.com/api/games/?api_key={API_KEY}&format=json&limit=1&filter=name:{game_name}"

    # Agregar encabezado User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Realizar la solicitud a la API
    response = requests.get(url, headers=headers)

    # Verificar el código de estado de la respuesta
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            # Obtener el primer juego de los resultados
            game = data["results"][0]
            return game
        else:
            return None
    else:
        return None

def main():
    # Título de la app
    st.title("Información sobre Videojuegos")
    st.write("Escribe el nombre de un juego para obtener información:")

    # Entrada de texto para el nombre del juego
    game_name = st.text_input("Nombre del juego")

    # Si se ingresa un nombre, mostrar la información
    if game_name:
        game_info = get_game_info(game_name)
        if game_info:
            st.subheader(f"Nombre: {game_info['name']}")
            st.write(f"Descripción: {game_info.get('deck', 'Descripción no disponible.')}")
            st.write(f"Fecha de lanzamiento: {game_info.get('original_release_date', 'No disponible')}")
            platforms = game_info.get('platforms', [])
            if platforms:
                st.write("Plataformas: " + ", ".join([platform['name'] for platform in platforms]))
            else:
                st.write("Plataformas: No disponible")
        else:
            st.write("No se encontró información sobre este juego.")

if __name__ == "__main__":
    main()
