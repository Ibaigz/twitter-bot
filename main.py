import time
from dotenv import load_dotenv
import os

import requests
import tweepy
import emoji
from threading import Timer

# Cargar las variables de entorno desde el archivo .env

load_dotenv()
# Obtener las credenciales de la API de Twitter desde las variables de entorno
TWITTER_API_KEY_V2 = os.getenv("TWITTER_API_KEY_V2")
TWITTER_API_SECRET_V2 = os.getenv("TWITTER_API_SECRET_V2")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
client = tweepy.Client(BEARER_TOKEN, TWITTER_API_KEY_V2, TWITTER_API_SECRET_V2, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

auth = tweepy.OAuth1UserHandler(TWITTER_API_KEY_V2, TWITTER_API_SECRET_V2, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)



def get_coaster_data(required_keys):
    """
    Fetches random coaster data from the external API and ensures it contains required keys.

    Args:
        required_keys (list): A list of required keys (e.g., ["height", "speed"]).

    Returns:
        dict: A dictionary containing coaster data if all required keys are present, None otherwise.
    """
    #API FROM https://github.com/fabianrguez/rcdb-api
    
    url = "https://rcdb-api.vercel.app/api/coasters/random"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        # Check for required keys within the "stats" dictionary
        stats = data.get("stats", {})  # Handle missing "stats" key gracefully
        if all(key in stats for key in required_keys):
            return data
        else:
            print(f"Data missing required keys in 'stats': {', '.join(set(required_keys) - set(stats.keys()))}")
    else:
        print("Error fetching data from the API")
    return None

def post_to_twitter(data):
    """
    Posts a tweet about the roller coaster data.

    Args:
        data (dict): The dictionary containing coaster data.
    """
    imgurl = requests.get(data["pictures"][0]["url"])
    with open ('img/asd.jpeg','wb') as f:
        f.write(imgurl.content)
    media_id = api.media_upload(filename='img/asd.jpeg').media_id_string
    # Print the media_id
    print(media_id)
    # Get the height from the data, handling missing "stats" and "height" keys
    height = data.get("stats", {}).get("height")  # Handle missing "stats" and "height" keys
    
    # Get the speed from the data, handling missing "stats" and "speed" keys
    speed = data.get("stats", {}).get("speed")   # Handle missing "stats" and "speed" keys
    # Check if either height or speed is None
    if height is None or speed is None:
        # Print a message and return if either is missing
        print("Required keys 'height' or 'speed' missing in 'stats'. Skipping tweet.")
        return
    # Print the media_id
    print(media_id)
    #Quitar espacios del nombre para el hastag
    
    DataParkName ={data['park']["name"]}
    print(DataParkName)
    DataParkName = data['park']["name"]
    print(DataParkName)

    # Eliminar los espacios del nombre del parque
    DataParkName = DataParkName.replace(" ", "")
    DataParkName = DataParkName.replace("'", "")
    print(DataParkName)
    
    # Construct the tweet text
    text = f"\n {emoji.emojize(':backhand_index_pointing_right_light_skin_tone: ')}RANDOM COASTER OF THE DAY \n \n {emoji.emojize(':roller_coaster: ')}{data['name']} \n \n {emoji.emojize(':round_pushpin:')}in {data['park']['name']}, {data['country']} \n \n {emoji.emojize(':chains:')} A {height}m tall roller coaster with a top speed of {speed} km/h. \n \n (via RCDB) \n #RollerCoaster #CoasterBot #{DataParkName}"
     # Create the tweet
    client.create_tweet(text=text, media_ids=[media_id])
    
    
# Function to run every 2 hours
def run_every_2_hours():
    required_keys = ["height", "speed"]
    coaster_data = get_coaster_data(required_keys)
    
    # Retry loop to get data with all required keys
    while coaster_data is None:
        coaster_data = get_coaster_data(required_keys)

    # Now that data has all required keys, proceed to tweet
    post_to_twitter(coaster_data)

    # Schedule the next run in 2 hours using threading.Timer
    timer = Timer(4 * 60 * 60, run_every_2_hours)
    timer.start()
    print("Next run scheduled in 4 hours")
# Run the program initially
run_every_2_hours()

# Keep the program running indefinitely (optional)
while True:
    time.sleep(1)
       
    



