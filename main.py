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
            print(f"\nNombre: {game['name']}")
            print(f"Descripción: {game.get('deck', 'Descripción no disponible.')}")
            
            # Mostrar la fecha de lanzamiento
            release_date = game.get('original_release_date', None)
            if release_date:
                print(f"Fecha de lanzamiento: {release_date[:10]}")  # Mostramos solo la fecha (YYYY-MM-DD)
            else:
                print("Fecha de lanzamiento: No disponible")
            
            # Obtener las plataformas disponibles (si las hay)
            platforms = game.get('platforms', [])
            if platforms:
                platform_names = [platform['name'] for platform in platforms]
                print(f"Plataformas: {', '.join(platform_names)}")
            else:
                print("Plataformas: No disponible")
        else:
            print("\nNo se encontró información sobre el juego.")
    else:
        print(f"\nError al acceder a la API: {response.status_code}")

def main():
    while True:
        # Ingresar el nombre del juego que se quiere buscar
        game_name = input("\nIngrese el nombre del juego o 'salir' para terminar: ")

        # Si el usuario ingresa 'salir', termina el programa
        if game_name.lower() == "salir":
            print("Saliendo del programa.")
            break
        
        # Llamar a la función para obtener la información del juego
        get_game_info(game_name)

if __name__ == "__main__":
    main()
