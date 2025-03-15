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
import spacy
from itertools import combinations

nlp = spacy.load("es_core_news_sm")

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

    if result.get("ParsedResults"):
        extracted_text = result["ParsedResults"][0]["ParsedText"].replace("\n", " ")
        return extracted_text
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

def interpret_query(user_query):
    """Analiza la consulta del usuario y extrae los filtros relevantes."""

    # Si user_query es una tupla, convertirla en una cadena
    if isinstance(user_query, tuple):
        user_query = " ".join(user_query)
    
    # Asegurarse de que user_query sea una cadena y convertirla a minúsculas
    user_query = str(user_query).lower()

    # Procesar el texto con spaCy
    doc = nlp(user_query)

    # Lista de palabras clave para género y plataforma
    genre_keywords = ["acción", "aventura", "estrategia", "rpg", "deportes", "carreras", "simulación", "misterio", "terror", "plataformas"]
    platform_keywords = ["playstation", "xbox", "pc", "nintendo", "switch", "steam", "mobile", "android", "ios"]

    # Palabras que no aportan valor para los filtros (palabras basura)
    stop_words = {"dame", "quiero", "información", "podrías", "darme", "consultar", "de", "en", "sobre", "para", "con", "y", "la", "el", "los", "las", "un", "una", "que", "quisiera", "saber", "quiero"}

    # Inicializar el diccionario de filtros
    filters = {}

    # Filtrar las palabras relevantes (eliminamos las palabras vacías y de puntuación)
    filtered_words = [token.text for token in doc if token.text not in stop_words and not token.is_punct]

    # Buscar las palabras clave de género y plataforma
    for word in filtered_words:
        if word in genre_keywords:
            filters["genre"] = word
        elif word in platform_keywords:
            filters["platform"] = word
        elif re.match(r'\d{4}', word):  # Si es un año
            filters["release_year"] = word
        else:  # El resto se considera nombre del juego
            if "name" not in filters:
                filters["name"] = word
            else:
                filters["name"] += f" {word}"

    # Si no se ha asignado ningún nombre, asumimos que todo el texto es el nombre del juego
    if "name" not in filters:
        filters["name"] = " ".join(filtered_words)

    # Mostrar los filtros aplicados
    print(f"Filtros aplicados: {filters}")
    
    return filters

def build_api_url(filters):
    base_url = f"https://www.giantbomb.com/api/games/?api_key={API_KEY}&format=json&limit=10"
    urls = set()  # Usamos un conjunto para evitar URLs duplicadas

    if isinstance(filters, dict):  # Asegurar que filters sea un diccionario
        # Consultas basadas en name
        if "name" in filters and isinstance(filters["name"], str):
            words = filters["name"].split()
            for word in words:
                url = f"{base_url}&filter=name:{word}"
                urls.add(url)  # Agregar la URL al conjunto

        # Consultas adicionales para platform, genre y release_year
        if "platform" in filters and isinstance(filters["platform"], str):
            url = f"{base_url}&filter=platform:{filters['platform']}"
            urls.add(url)

        if "genre" in filters and isinstance(filters["genre"], str):
            url = f"{base_url}&filter=genre:{filters['genre']}"
            urls.add(url)

        if "release_year" in filters and isinstance(filters["release_year"], str):
            url = f"{base_url}&filter=original_release_date:{filters['release_year']}-01-01|{filters['release_year']}-12-31"
            urls.add(url)

    return tuple(urls)  # Convertir el conjunto en tupla

# Función para guardar los datos en CSV
def save_game_info_csv(game):
    # Convertir dict_values en una lista si es necesario
    if isinstance(game, dict):
        game_data = game  # Es un diccionario, usarlo directamente
    elif isinstance(game, list) and len(game) > 0 and isinstance(game[0], dict):
        game_data = game[0]  # Si es una lista de diccionarios, tomar el primero
    else:
        raise TypeError(f"Se esperaba un diccionario o una lista de diccionarios, pero se recibió {type(game)}")

    header = ['name', 'description', 'release_date', 'platforms']

    # Manejo seguro de plataformas
    platforms = game_data.get('platforms', [])
    if not isinstance(platforms, list):
        platforms = []

    row = {
        'name': game_data.get('name', 'Nombre no disponible'),
        'description': game_data.get('deck', 'Descripción no disponible'),
        'release_date': game_data.get('original_release_date', 'No disponible'),
        'platforms': ', '.join([platform['name'] for platform in platforms if isinstance(platform, dict)])
    }

    file_path = 'data/game_info.csv'
    file_exists = os.path.isfile(file_path)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

# Función para guardar los datos en JSON
def save_game_info_json(game):
    # Asegúrate de que 'game' es un diccionario y no un dict_values
    if isinstance(game, dict):
        game_data = {
            'name': game['name'],
            'description': game.get('deck', 'Descripción no disponible'),
            'release_date': game.get('original_release_date', 'No disponible'),
            # Asegúrate de que platforms sea una lista de diccionarios con 'name'
            'platforms': [platform.get('name', 'Plataforma no disponible') for platform in game.get('platforms', []) or []]
        }
    elif isinstance(game, list):  # Si es una lista de diccionarios
        game_data = [{
            'name': item['name'],
            'description': item.get('deck', 'Descripción no disponible'),
            'release_date': item.get('original_release_date', 'No disponible'),
            # Asegúrate de que platforms sea una lista de diccionarios con 'name'
            'platforms': [platform.get('name', 'Plataforma no disponible') for platform in (item.get('platforms', []) or [])]
        } for item in game]
    else:
        raise TypeError(f"Se esperaba un diccionario o una lista de diccionarios, pero se recibió {type(game)}")

    json_path = 'data/game_info.json'
    # Cargar los datos existentes si el archivo ya existe
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    else:
        data = []

    # Agregar los nuevos datos
    if isinstance(game, list):  # Si es una lista, añadir todos los juegos
        data.extend(game_data)
    else:  # Si es un solo juego, añadir uno solo
        data.append(game_data)

    # Guardar los datos actualizados en el archivo JSON
    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Función para obtener la información del juego desde Giant Bomb
def get_game_info(user_input):
    # Extraer componentes de la consulta
    query_components = extract_game_name(user_input)
    
    # Interpretar la consulta
    #query_type, filters = interpret_query(query_components) -> así estaba antes xd

    if user_input:
        # Asegúrate de que user_input sea una cadena
        if isinstance(user_input, str):
            filters = interpret_query(user_input)
            st.write(f"Filtros aplicados: {filters}")
        else:
            st.error("La entrada del usuario no es válida. Debe ser una cadena de texto.")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    all_results = []

    for api_url in build_api_url(filters):
        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            st.error(f"Error al acceder a la API: {e}")
            continue  # Saltar esta URL y seguir con la siguiente

        if response.status_code == 200:
            data = response.json()
            if "results" in data:
                all_results.extend(data["results"])  # Agregar los resultados a la lista

    # Eliminar duplicados basados en el ID del juego
    unique_results = {game["id"]: game for game in all_results}.values()

    if unique_results:
        st.write("### Juegos sugeridos:")
        for game in unique_results:
            description = game.get('deck', 'Descripción no disponible')

            # Mostrar la imagen del juego si está disponible
            col1, col2 = st.columns([2, 5])

            with col1:
                if game.get('image', {}).get('small_url'):
                    st.image(game['image']['small_url'], caption="Imagen del juego", use_container_width=True)

            with col2:
                st.markdown(f"#### {game['name']}")
                st.write(f"**Descripción:** {description}")

                release_date = game.get('original_release_date', 'No disponible')
                if release_date and isinstance(release_date, str):  
                    st.write(f"**Fecha de lanzamiento:** {release_date[:10]}")
                else:
                    st.write("**Fecha de lanzamiento:** No disponible")

                platforms = game.get('platforms', [])
                platform_names = ', '.join([platform['name'] for platform in platforms]) if platforms else "No disponible"
                st.write(f"**Plataformas:** {platform_names}")
                st.write("----")

        # Guardar información de los juegos sugeridos
        save_game_info_csv(list(unique_results))
        save_game_info_json(list(unique_results))
    else:
        st.write("No se encontró información sobre el juego.")

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