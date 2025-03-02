import requests
import streamlit as st
import os
import json
import csv
import re
from dotenv import load_dotenv
from translate import Translator
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO

# Cargar las variables del archivo .env
load_dotenv()

# Obtener las claves de API
API_KEY = os.getenv("GIANT_BOMB_API_KEY")
OCR_API_KEY = os.getenv("OCR_API_KEY")  # Mueve la clave de OCR al archivo .env

# Configurar el traductor al español
translator = Translator(to_lang="es")

# Crear la carpeta 'data' si no existe
if not os.path.exists("data"):
    os.makedirs("data")

# Función para mejorar la imagen antes de enviarla al OCR
def enhance_image(image_path):
    try:
        with Image.open(image_path) as img:
            # Convertir a escala de grises
            img = img.convert("L")
            
            # Mejorar el contraste
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)  # Aumentar el contraste

            # Mejorar el brillo
            brightness = ImageEnhance.Brightness(img)
            img = brightness.enhance(1.5)  # Aumentar el brillo

            # Reducir el ruido
            img = img.filter(ImageFilter.MedianFilter(size=3))

            # Guardar la imagen procesada
            enhanced_path = image_path.replace(".", "_enhanced.")
            img.save(enhanced_path)
            return enhanced_path
    except Exception as e:
        st.error(f"Error al procesar la imagen: {e}")
        return None

# Función para extraer texto usando OCR
def extract_text_ocr_space(image_path):
    enhanced_image_path = enhance_image(image_path)
    if not enhanced_image_path:
        return "No se pudo procesar la imagen."

    # Intentar primero con español
    with open(enhanced_image_path, "rb") as image_file:
        response = requests.post(
            "https://api.ocr.space/parse/image",
            files={"image": image_file},
            data={
                "apikey": OCR_API_KEY,
                "language": "spa",  # Español
                "isOverlayRequired": False,
                "filetype": "JPG",  # Asegurar que el tipo de archivo sea correcto
                "OCREngine": 2  # Usar el motor OCR más avanzado
            }
        )

    try:
        result = response.json()
    except ValueError:
        st.error("Error al procesar la respuesta de OCR.")
        return "No se pudo procesar la respuesta."

    # Si no hay resultados con español, intentar con inglés
    if not result.get("ParsedResults"):
        with open(enhanced_image_path, "rb") as image_file:
            response = requests.post(
                "https://api.ocr.space/parse/image",
                files={"image": image_file},
                data={
                    "apikey": OCR_API_KEY,
                    "language": "eng",  # Inglés
                    "isOverlayRequired": False,
                    "filetype": "JPG",
                    "OCREngine": 2
                }
            )
        
        try:
            result = response.json()
        except ValueError:
            st.error("Error al procesar la respuesta de OCR.")
            return "No se pudo procesar la respuesta."

    # Verificar si se detectó texto
    if result.get("ParsedResults"):
        return result["ParsedResults"][0]["ParsedText"]
    else:
        st.error(f"Error OCR: {result}")
        return "No se detectó texto en la imagen."

# Función para extraer el nombre del juego y otros detalles en lenguaje natural
def extract_game_name(user_input):
    # Patrones para detectar consultas comunes
    patterns = [
        r"(?:háblame de|dime información sobre|qué sabes de|quiero saber sobre|busca)\s+(.+)",
        r"(?:juegos de|juegos para)\s+(.+)",
        r"(?:juegos de)\s+(.+)\s+(?:lanzados en|del año)\s+(\d{4})",
        r"(?:juegos de)\s+(.+)\s+(?:en)\s+(.+)"  # Ejemplo: "juegos de acción en PlayStation"
    ]

    for pattern in patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            return match.groups()  # Devuelve una tupla con los grupos capturados

    # Si no se encuentra ningún patrón, devolver la entrada completa
    return (user_input.strip(),)

# Función para interpretar la consulta
def interpret_query(query_components):
    query_type = "general"  # Por defecto, busca por nombre
    filters = {}

    if len(query_components) == 1:
        # Consulta simple: "háblame de Mario"
        filters["name"] = query_components[0]
    elif len(query_components) == 2:
        # Consulta con dos componentes: "juegos de acción en PlayStation"
        if "en" in query_components[1].lower():
            filters["platform"] = query_components[1]
            filters["genre"] = query_components[0]
        elif "lanzados en" in query_components[1].lower():
            filters["release_year"] = query_components[1]
            filters["genre"] = query_components[0]
    elif len(query_components) == 3:
        # Consulta con tres componentes: "juegos de acción lanzados en 2020"
        filters["genre"] = query_components[0]
        filters["release_year"] = query_components[2]

    return query_type, filters

# Función para construir la URL de la API
def build_api_url(filters):
    base_url = f"https://www.giantbomb.com/api/games/?api_key={API_KEY}&format=json&limit=10"
    
    if "name" in filters:
        base_url += f"&filter=name:{filters['name']}"
    if "platform" in filters:
        base_url += f"&filter=platform:{filters['platform']}"
    if "genre" in filters:
        base_url += f"&filter=genre:{filters['genre']}"
    if "release_year" in filters:
        base_url += f"&filter=original_release_date:{filters['release_year']}-01-01|{filters['release_year']}-12-31"

    return base_url

# Función para guardar los datos en CSV
def save_game_info_csv(game):
    header = ['name', 'description', 'release_date', 'platforms']
    game_data = {
        'name': game['name'],
        'description': game.get('deck', 'Descripción no disponible'),
        'release_date': game.get('original_release_date', 'No disponible'),
        'platforms': [platform['name'] for platform in game.get('platforms', [])]
    }

    file_exists = os.path.isfile('data/game_info.csv')

    with open('data/game_info.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        if not file_exists:
            writer.writeheader()
        writer.writerow(game_data)

# Función para guardar los datos en JSON
def save_game_info_json(game):
    game_data = {
        'name': game['name'],
        'description': game.get('deck', 'Descripción no disponible'),
        'release_date': game.get('original_release_date', 'No disponible'),
        'platforms': [platform['name'] for platform in game.get('platforms', [])]
    }

    json_path = 'data/game_info.json'
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    else:
        data = []

    data.append(game_data)

    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Función para obtener la información del juego desde Giant Bomb
def get_game_info(user_input):
    # Extraer componentes de la consulta
    query_components = extract_game_name(user_input)
    
    # Interpretar la consulta
    query_type, filters = interpret_query(query_components)
    
    # Construir la URL de la API
    api_url = build_api_url(filters)
    
    # Realizar la solicitud a la API
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al acceder a la API: {e}")
        return

    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            st.write("### Juegos sugeridos:")
            for game in data["results"]:
                description = game.get('deck', 'Descripción no disponible')
                if description:
                    translated_description = translator.translate(description)
                else:
                    translated_description = 'Descripción no disponible'

                # Mostrar la imagen del juego si está disponible
                col1, col2 = st.columns([2, 5])

                with col1:
                    if game.get('image', {}).get('small_url'):
                        st.image(game['image']['small_url'], caption="Imagen del juego", use_container_width=True)

                with col2:
                    st.markdown(f"#### {game['name']}")
                    st.write(f"**Descripción:** {translated_description}")

                    release_date = game.get('original_release_date', 'No disponible')
                    if release_date != 'No disponible' and release_date:
                        st.write(f"**Fecha de lanzamiento:** {release_date[:10]}")
                    else:
                        st.write(f"**Fecha de lanzamiento:** {release_date}")

                    platforms = game.get('platforms', [])
                    platform_names = ', '.join([platform['name'] for platform in platforms]) if platforms else "No disponible"
                    st.write(f"**Plataformas:** {platform_names}")
                    st.write("----")

            # Guardar información de los juegos sugeridos
            save_game_info_csv(game)
            save_game_info_json(game)
        else:
            st.write("No se encontró información sobre el juego.")
    else:
        st.write(f"Error al acceder a la API: {response.status_code}")

# Interfaz de Streamlit
def main():
    st.title("ReviewGameIA")

    # Opción para escribir el nombre del juego
    user_input = st.text_input("Escribe tu consulta (por ejemplo, 'juegos de Mario' o 'juegos de acción en PlayStation'):")

    # Opción para subir una imagen
    uploaded_file = st.file_uploader("O sube una imagen con el nombre del juego", type=["png", "jpg", "jpeg"])

    if user_input:
        get_game_info(user_input)
    elif uploaded_file:
        # Guardar la imagen temporalmente
        image_path = f"temp_image.{uploaded_file.name.split('.')[-1]}"
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Procesar la imagen con retroalimentación visual
        with st.spinner("Procesando imagen..."):
            extracted_text = extract_text_ocr_space(image_path)
            st.write(f"**Texto detectado:** {extracted_text}")

            # Intentar buscar el juego si se detecta texto
            if extracted_text.strip():
                get_game_info(extracted_text.strip())
            else:
                st.warning("No se pudo detectar texto en la imagen.")

        # Eliminar la imagen temporal
        os.remove(image_path)
        if os.path.exists(image_path.replace(".", "_enhanced.")):
            os.remove(image_path.replace(".", "_enhanced."))

if __name__ == "__main__":
    main()