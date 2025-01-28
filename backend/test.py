import requests
import os

# Test uploading an image
url = 'http://127.0.0.1:5000/upload'
image_path = '/Users/urishamir/Desktop/GitHub/_ai_model_api/backend/assets/test_images/2100.jpg'

try:
    # Test server connection first
    health_check = requests.get('http://127.0.0.1:5000/predictions')
    print(f"Server connection test: {health_check.status_code}")

    # Upload image
    print(f"\nUploading image from: {image_path}")
    with open(image_path, 'rb') as img:
        files = {'file': ('2100.jpg', img, 'image/jpeg')}
        response = requests.post(url, files=files, timeout=30)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

except requests.exceptions.ConnectionError:
    print("Connection Error: Could not connect to server")
except Exception as e:
    print(f"Error: {str(e)}")
