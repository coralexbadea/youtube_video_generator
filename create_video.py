import os
import requests
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import yt_dlp
from upload_video import auth_and_upload 
import numpy as np

# Define the folder for saving files
BASE_DIR = r'C:\\Users\\user\\Desktop\\ProramFiles\\create_video'

def download_audio_from_youtube(youtube_url, output_path=os.path.join(BASE_DIR, 'audio.mp3')):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(BASE_DIR, 'audio'),  # Changed this line to avoid .mp3 extension
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,  # Set to False to see detailed output
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        
        # Rename the downloaded file to audio.mp3
        os.rename(os.path.join(BASE_DIR, 'audio.mp3'), output_path)  # Rename the original file to audio.mp3

        print(f"Downloaded audio file: {output_path}")

        # Check if the audio file exists
        if os.path.exists(output_path):
            print("Audio file exists.")
        else:
            print("Audio file not found after download.")

        return output_path
    except Exception as e:
        print(f"An error occurred while downloading the audio: {e}")
        return None


# Step 2: Fetch random Bible verses
def get_random_bible_verse():
    url = "https://bible-api.com/?random=verse"  # Updated to the correct URL
    try:
        response = requests.get(url)
        verse_data = response.json()
        
        if 'verses' in verse_data and len(verse_data['verses']) > 0:
            verse = verse_data['verses'][0]['text'].strip()
            reference = verse_data['reference']
            return f"{verse} - {reference}"
        else:
            return "Bible verse not found"
    except Exception as e:
        print(f"Error fetching Bible verse: {e}")
        return "Bible verse not found"

# Fetch random images using Unsplash API
UNSPLASH_ACCESS_KEY = 'ozrdOshlxxmVF1qxcZBlQsFv7C6guWp-S4tU_bq5K_o'  # Replace with your Unsplash API Key

def get_random_image_url():
    headers = {
        'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'
    }
    params = {
        'query': 'nature',
        'orientation': 'landscape',
        'per_page': 1
    }
    response = requests.get('https://api.unsplash.com/photos/random', headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Error fetching image: {response.status_code}, {response.text}")
        return "Image not found"

    image_data = response.json()
    
    # Check if 'urls' key exists
    if 'urls' in image_data:
        return image_data['urls'].get('regular', "Image not found")
    else:
        print("Unexpected response format:", image_data)
        return "Image not found"

def wrap_text(text, max_words):
    """Wrap the text into lines with a maximum number of words."""
    words = text.split()
    wrapped_lines = []
    
    for i in range(0, len(words), max_words):
        line = ' '.join(words[i:i + max_words])
        wrapped_lines.append(line)
    
    return '\n'.join(wrapped_lines)


def calculate_brightness(img):
    # Convert the image to grayscale
    grayscale_image = img.convert('L')  # 'L' mode is for grayscale
    
    # Get the image dimensions
    width, height = grayscale_image.size
    
    # Define the coordinates to crop the middle horizontal part
    top = height // 3
    bottom = 2 * height // 3
    
    # Crop the image to get the middle third
    middle_part = grayscale_image.crop((0, top, width, bottom))
    
    # Convert the cropped middle part to a numpy array
    np_image = np.array(middle_part)
    
    # Calculate the average pixel intensity (brightness)
    brightness = np.mean(np_image)
    
    return brightness

def render_text_on_image(image_path, text, output_path, padding=40):
    img = Image.open(image_path)

    # Create a new image with padding
    new_width = img.width + padding * 2
    new_height = img.height + padding * 2

    padded_img = Image.new("RGB", (new_width, new_height), (255, 255, 255))  # Black background
    padded_img.paste(img, (padding, padding))  # Paste original image onto the padded image

    draw = ImageDraw.Draw(padded_img)

    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except IOError:
        font = ImageFont.load_default()
  
    # Wrap the text into multiple lines
    wrapped_text = wrap_text(text, 15)

    # Calculate text bounding box
    text_bbox = draw.textbbox((padding, padding), wrapped_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # New image dimensions
    padded_img_width, padded_img_height = padded_img.size

    # Calculate the position for centering the text within the padded image
    text_position = ((padded_img_width - text_width) // 2, (padded_img_height - text_height) // 2)

    # Adjust the text position to account for padding
    text_position = (text_position[0], text_position[1] + padding)  # Add padding to the y-position

    # Draw the wrapped text on the padded image
    brightness = int(calculate_brightness(img))
    print(brightness)
    color = "yellow" if brightness < 125 else "black"
    draw.text(text_position, wrapped_text, font=font, fill=color)
    padded_img.save(output_path)

def create_bible_verse_video(audio_file, verses, image_urls, output_file=os.path.join(BASE_DIR, 'bible_video.mp4')):
    clips = []
    
    for i in range(len(verses)):
        if image_urls[i] == "Image not found":
            print(f"Skipping image for verse: {verses[i]} (Image not found)")
            continue  # Skip this iteration if the image URL is invalid

        try:
            response = requests.get(image_urls[i])
            img = Image.open(BytesIO(response.content))
            img.save(os.path.join(BASE_DIR, f"image_{i}.png"))
            
            render_text_on_image(os.path.join(BASE_DIR, f"image_{i}.png"), verses[i], os.path.join(BASE_DIR, f"image_with_text_{i}.png"))
            
            image_clip = ImageClip(os.path.join(BASE_DIR, f"image_with_text_{i}.png"), duration=7)
            clips.append(image_clip)
        
        except Exception as e:
            print(f"Error processing image for verse: {verses[i]} - {e}")

    if not clips:
        print("No valid images to create video.")
        return
    
    final_clip = concatenate_videoclips(clips, method="compose")
    audio_background = AudioFileClip(audio_file)
    final_clip = final_clip.set_audio(audio_background)
    final_clip.write_videofile(output_file, fps=24)
    print(f"Video saved as {output_file}")

def main(youtube_url):
    audio_file = download_audio_from_youtube(youtube_url)
    
    if not audio_file:
        print("Failed to download audio. Exiting.")
        return
    
    print("Fetching verses and images...")
    verses = [get_random_bible_verse() for _ in range(1)]
    image_urls = [get_random_image_url() for _ in range(1)]
    
    create_bible_verse_video(audio_file, verses, image_urls)

def final():
    youtube_url = "https://www.youtube.com/watch?v=qg6NwETl2VY"  # Replace with a valid URL
    main(youtube_url)
    auth_and_upload()

if __name__ == "__main__":
    final()
