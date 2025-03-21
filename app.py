import requests
import streamlit as st
import os
import json
import csv
import re
import time  # Importar la librería time para el retraso
from dotenv import load_dotenv
from translate import Translator
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
import spacy
from itertools import combinations
from responses import generate_game_response, generate_no_results_response, generate_end_conversation_response

nlp = spacy.load("es_core_news_sm")

# Cargar las variables del archivo .env
load_dotenv()

# Obtener las claves de API
API_KEY = os.getenv("GIANT_BOMB_API_KEYS", "").split(",")  # Claves separadas por comas en .env

OCR_API_KEYS = os.getenv("OCR_API_KEYS", "").split(",")
# Eliminar claves vacías o None en caso de que falten
OCR_API_KEYS = [key.strip() for key in OCR_API_KEYS if key.strip()]

# Cache for the last successful API key
last_successful_api_key = None

def get_valid_api_key(api_keys, url, params, headers={}):
    global last_successful_api_key
    # Try the last successful API key first
    if last_successful_api_key:
        params["api_key"] = last_successful_api_key
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()

    for api_key in api_keys:
        params["api_key"] = api_key
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            last_successful_api_key = api_key  # Cache this key
            return response.json()
        elif response.status_code == 403 or response.status_code == 429:
            print(f"API key {api_key} ha excedido el límite, probando la siguiente...")
            continue

    print("Todas las API keys han excedido el consumo.")
    return None

# Configurar el traductor al español
translator = Translator(to_lang="es")

# Crear la carpeta 'data' si no existe
if not os.path.exists("data"):
    os.makedirs("data")

# Función para la animación de escritura
def typewriter_effect(text, delay=0.01):
    """Muestra el texto con un efecto de máquina de escribir."""
    placeholder = st.empty()  # Crear un espacio reservado para el texto
    current_text = ""
    for char in text:
        current_text += char
        placeholder.markdown(current_text)  # Actualizar el texto en el espacio reservado
        time.sleep(delay)  # Retraso entre caracteres

# Función para mejorar la imagen antes de enviarla al OCR
def enhance_image(image_bytes):
    try:
        with Image.open(image_bytes) as img:
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

            # Guardar la imagen procesada en BytesIO
            enhanced_bytes = BytesIO()
            img.save(enhanced_bytes, format="JPEG")
            enhanced_bytes.seek(0)
            return enhanced_bytes
    except Exception as e:
        st.error(f"Error al procesar la imagen: {e}")
        return None

def extract_text_ocr_space(image_bytes):
    enhanced_bytes = enhance_image(image_bytes)
    if not enhanced_bytes:
        return "No se pudo procesar la imagen."

    headers = {"User-Agent": "Mozilla/5.0"}

    for api_key in OCR_API_KEYS:  # Intentar con cada API Key
        for language in ["spa", "eng"]:  # Primero español, luego inglés
            response = requests.post(
                "https://api.ocr.space/parse/image",
                files={"image": enhanced_bytes},
                data={
                    "apikey": api_key,
                    "language": language,
                    "isOverlayRequired": False,
                    "filetype": "JPG",
                    "OCREngine": 2
                },
                headers=headers
            )

            if response.status_code != 200:
                print(f"Error en la API (HTTP {response.status_code}): {response.text}")
                continue  # Intentar con la siguiente clave API

            try:
                result = response.json()
                if isinstance(result, str):  # Si `result` es una cadena, convertirla a diccionario
                    result = eval(result)
            except (ValueError, SyntaxError):
                st.error(f"Respuesta no válida de OCR.space: {response.text}")
                continue

            if isinstance(result, dict) and "ParsedResults" in result:
                extracted_text = result["ParsedResults"][0].get("ParsedText", "").replace("\n", " ")
                return extracted_text if extracted_text else "No se detectó texto en la imagen."

        print(f"La clave API {api_key[:5]}... falló o alcanzó su límite.")  # Mostrar solo parte de la clave

    st.error("Todas las claves API fallaron o se agotaron.")
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
    platform_keywords = [
        "playstation", "xbox", "pc", "nintendo", "switch", "steam", "mobile", "android", 
        "ios", "mac", "xbox 360", "playstation 3", "xbox 360 games store", "playstation network (ps3)", 
        "iphone", "ipad", "windows phone", "playstation vita", "wii u", "browser", "playstation network (vita)", 
        "xbox one", "playstation 4", "linux", "amazon fire tv", "new nintendo 3ds", "nintendo switch", 
        "xbox series x|s"
    ]

    # Palabras que no aportan valor para los filtros (palabras basura)
    stop_words = {"todos", "juegos", "dame", "quiero", "información", "podrías", "darme", "consultar", "de", "en", "sobre", "para", "con", "y", "la", "el", "los", "las", "un", "una", "que", "quisiera", "saber", "quiero", "hablame", "acerca", "del", "alrededor", "acerca"}

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
    #print(f"Filtros aplicados: {filters}")
    
    return filters

def build_api_url(filters, api_key):
    base_url = f"https://www.giantbomb.com/api/games/?api_key={api_key}&format=json&limit=5"
    query_params = []

    # Add filters to the query parameters
    if "name" in filters:
        query_params.append(f"filter=name:{filters['name']}")
    if "genre" in filters:
        query_params.append(f"filter=genres:{filters['genre']}")
    if "platform" in filters:
        query_params.append(f"filter=platforms:{filters['platform']}")
    if "release_year" in filters:
        query_params.append(f"filter=original_release_date:{filters['release_year']}-01-01|{filters['release_year']}-12-31")

    # Combine base URL with query parameters
    if query_params:
        base_url += "&" + "&".join(query_params)

    return base_url

def save_game_info_csv(game):
    print(f"Tipo de 'game': {type(game)}")
    print(f"Contenido de 'game': {game}")
    # Verificar si 'game' es un diccionario o una lista de diccionarios
    if isinstance(game, dict):
        game_data = game  # Si es un diccionario, usarlo directamente
    elif isinstance(game, list) and len(game) > 0 and isinstance(game[0], dict):
        game_data = game[0]  # Si es una lista de diccionarios, tomar el primer diccionario
    else:
        raise TypeError(f"Se esperaba un diccionario o una lista de diccionarios, pero se recibió {type(game)}")

    # Definir las cabeceras que deben ser las mismas para todos los registros
    header = ['name', 'description', 'release_date', 'platforms']
    
    # Verificación segura de la lista 'platforms'
    platforms = game_data.get('platforms', [])
    if not isinstance(platforms, list):
        platforms = []  # Si 'platforms' no es una lista, se asigna una lista vacía

    # Crear el diccionario con los datos que se escribirán en el archivo CSV
    row = {
        'name': game_data.get('name', 'Nombre no disponible'),
        'description': game_data.get('deck', 'Descripción no disponible'),
        'release_date': game_data.get('original_release_date', 'No disponible'),
        'platforms': ', '.join([platform.get('name', 'Desconocida') for platform in platforms if isinstance(platform, dict)])
    }

    # Ruta del archivo donde se guardarán los datos
    file_path = 'data/game_info.csv'
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Crear directorio si no existe

    # Comprobar si el archivo ya existe y tiene contenido
    file_exists = os.path.isfile(file_path) and os.path.getsize(file_path) > 0

    # Abrir el archivo en modo append ('a') para agregar nuevos registros
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        
        # Escribir el encabezado solo si el archivo no existe o está vacío
        if not file_exists:
            writer.writeheader()
        
        # Escribir la fila con los datos del juego
        writer.writerow(row)

    return file_path  # Retornar la ruta del archivo guardado (opcional)

def save_game_info_json(data):
    file_path = 'data/game_info.json'

    # Crear directorio si no existe
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Si el archivo no existe o está vacío, crear uno nuevo con el contenido
    if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    else:
        # Leer el archivo existente y agregar los nuevos datos
        try:
            with open(file_path, 'r+', encoding='utf-8') as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = []  # Si el archivo está vacío o corrupto, iniciar una lista vacía

                # Agregar los nuevos datos a la lista existente
                existing_data.extend(data)

                # Volver a escribir el archivo con los datos actualizados
                file.seek(0)
                json.dump(existing_data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error al procesar el archivo JSON: {e}")

# Función para obtener la información del juego desde Giant Bomb con manejo de múltiples API keys
def get_game_info(user_input):
    query_components = extract_game_name(user_input)
    
    if user_input:
        if isinstance(user_input, str):
            filters = interpret_query(user_input)
            #typewriter_effect(f"Filtros aplicados: {filters}")  # Animación de escritura
        else:
            st.error("La entrada del usuario no es válida. Debe ser una cadena de texto.")
            return
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    all_results = []
    
    # Construir la URL base y los parámetros
    api_url = build_api_url(filters, API_KEY[0])  # Generar URL para la consulta
    params = {}  # Otros parámetros fijos
    
    # Intentar obtener una respuesta válida usando get_valid_api_key
    response_data = get_valid_api_key(API_KEY, api_url, params, headers)
        
    if response_data:
        if "results" in response_data:
            all_results.extend(response_data["results"])  # Agregar los resultados a la lista
    else:
        st.error("Todas las API keys han excedido el consumo o no se encontraron resultados.")
        typewriter_effect(generate_no_results_response())  # Animación de escritura
        return
    
    # Asegurar que los resultados sean únicos por ID
    unique_results = {game["id"]: game for game in all_results}.values()
    unique_results = list(unique_results)
    typewriter_effect(generate_game_response(str(user_input)))  # Animación de escritura
    typewriter_effect("### Juegos sugeridos:")  # Animación de escritura
    for game in unique_results:
        if not isinstance(game, dict):
            print(f"Elemento no es diccionario: {game}")
        description = game.get('deck', 'Descripción no disponible')

        col1, col2 = st.columns([2, 5])

        with col1:
            if game.get('image', {}).get('small_url'):
                st.image(game['image']['small_url'], caption="Imagen del juego", use_container_width=True)

        with col2:
            typewriter_effect(f"#### {game['name']}")  # Animación de escritura
            typewriter_effect(f"**Descripción:** {description}")  # Animación de escritura

            release_date = game.get('original_release_date', 'No disponible')
            typewriter_effect(f"**Fecha de lanzamiento:** {release_date[:10] if isinstance(release_date, str) else 'No disponible'}")  # Animación de escritura

            platforms = game.get('platforms', [])
            platform_names = ', '.join([platform['name'] for platform in platforms]) if platforms else "No disponible"
            typewriter_effect(f"**Plataformas:** {platform_names}")  # Animación de escritura
            typewriter_effect("----")  # Animación de escritura
    end_message = generate_end_conversation_response()
    typewriter_effect(end_message)  # Animación de escritura
    if unique_results:
     save_game_info_csv(unique_results)
    save_game_info_json(list(unique_results))

# Interfaz de Streamlit
def main():
    st.title("ReviewGameIA")

    # Display results at the top
    if 'results' in st.session_state and st.session_state.results:
        for result in st.session_state.results:
            st.write(result)

    # Input options at the bottom
    st.write("---")  # Separator
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""
    user_input = st.text_input("Escribe tu consulta (por ejemplo, 'juegos de Mario' o 'juegos de acción en PlayStation'):", value=st.session_state.user_input)
    uploaded_file = st.file_uploader("O sube una imagen con el nombre del juego", type=["png", "jpg", "jpeg"])

    if user_input:
        results = get_game_info(user_input)
        st.session_state.results = results
        st.session_state.user_input = ""  # Clear the input field
    elif uploaded_file:
        with st.spinner("Procesando imagen..."):
            image_bytes = BytesIO(uploaded_file.getbuffer())
            extracted_text = extract_text_ocr_space(image_bytes)
            if extracted_text.strip():
                results = get_game_info(extracted_text.strip())
                st.session_state.results = results
            else:
                st.warning("No se pudo detectar texto en la imagen.")
                st.write(generate_end_conversation_response())

if __name__ == "__main__":
    main()