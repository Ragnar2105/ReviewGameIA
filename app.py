import requests
from dotenv import load_dotenv
import os
import streamlit as st
from translate import Translator

# Cargar las variables del archivo .env
load_dotenv()

# Obtener la clave de API desde el archivo .env
API_KEY = os.getenv("GIANT_BOMB_API_KEY")

# Crear una instancia del traductor para traducir al español
translator = Translator(to_lang="es")

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

            # Traducir la descripción y otros campos al español
            translated_description = translator.translate(game.get('deck', 'Descripción no disponible.'))

            # Mostrar el título del juego con un tamaño mayor
            st.markdown(f"## <span style='font-size: 40px'>{game['name']}</span>", unsafe_allow_html=True)

            # Crear dos columnas: una para la imagen y otra para la información
            col1, col2 = st.columns([2, 5])  # Proporción más ancha para la columna de información

            with col1:
                # Mostrar la imagen del juego si está disponible
                if game.get('image', {}).get('small_url'):
                    st.image(game['image']['small_url'], caption="Imagen principal", use_container_width=True)

            with col2:
                # Espacio para separar un poco la imagen del texto
                st.write(" ")  
                st.write(" ")  # Se añadió más espacio

                # Mostrar la descripción traducida al español
                st.markdown(f"### <span style='font-size: 20px'>**Descripción:** {translated_description}</span>", unsafe_allow_html=True)

                # Mostrar la fecha de lanzamiento
                release_date = game.get('original_release_date', None)
                if release_date:
                    st.markdown(f"### <span style='font-size: 18px'>**Fecha de lanzamiento:** {release_date[:10]}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"### <span style='font-size: 18px'>**Fecha de lanzamiento:** No disponible</span>", unsafe_allow_html=True)
                
                # Obtener las plataformas disponibles (si las hay)
                platforms = game.get('platforms', [])
                if platforms:
                    platform_names = [platform['name'] for platform in platforms]
                    st.markdown(f"### <span style='font-size: 18px'>**Plataformas:** {', '.join(platform_names)}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"### <span style='font-size: 18px'>**Plataformas:** No disponible</span>", unsafe_allow_html=True)
        else:
            st.write("No se encontró información sobre el juego.")
    else:
        st.write(f"Error al acceder a la API: {response.status_code}")

# Streamlit UI
def main():
    st.title("Información de Juegos")

    # Entrada de usuario
    game_name = st.text_input("Ingrese el nombre del juego:")

    if game_name:
        get_game_info(game_name)

if __name__ == "__main__":
    main()
