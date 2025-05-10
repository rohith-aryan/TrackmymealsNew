
import requests

API_URL = 'https://api.calorieninjas.com/v1/nutrition?query='
API_KEY = 'q8UiarWsa84Pnq3zvKSU2g==u4syZNhrKcbEQB0d'  # Make sure to replace this with your actual API key

def fetch_nutrition_from_api(query):
    response = requests.get(API_URL + query, headers={'X-Api-Key': API_KEY})
    if response.status_code == requests.codes.ok:
        return response.json()  # Return the parsed JSON response
    else:
        print("Error:", response.status_code, response.text)
        return None  # Return None if there was an error
