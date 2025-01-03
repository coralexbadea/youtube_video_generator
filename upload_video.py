import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http
from googleapiclient.http import MediaFileUpload
import webbrowser


# Set the necessary scopes for the API
scopes = ["https://www.googleapis.com/auth/youtube.upload"]

# OAuth 2.0 Client Credentials File
client_secrets_file = "C:\\Users\\user\\Desktop\\ProramFiles\\create_video\\client_secret.json"

BASE_DIR = r'C:\\Users\\user\\Desktop\\ProramFiles\\create_video'

# Video file and metadata
video_file = os.path.join(BASE_DIR, 'bible_video.mp4')
video_title = "Bible Verse"
video_description = "Bible Verse Song"
video_category_id = "22"  # For 'People & Blogs' category
video_tags = ["bible", "verse"]

def authenticate_youtube():
    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_local_server(port=8080)  # Launches a local server for OAuth authentication

    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    return youtube


# Function to upload video to YouTube
def upload_video(youtube):
    request_body = {
        "snippet": {
            "title": video_title,
            "description": video_description,
            "tags": video_tags,
            "categoryId": video_category_id
        },
        "status": {
            "privacyStatus": "public",  # Options: 'public', 'private', 'unlisted'
        }
    }

    # Media upload
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)

    # Create upload request
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    response = request.execute()
    video_url = f"https://www.youtube.com/watch?v="+response['id']
    print("Video uploaded successfully: " + video_url)
    webbrowser.open(video_url)


def auth_and_upload():
    youtube_client = authenticate_youtube()
    upload_video(youtube_client)

if __name__ == "__main__":
    auth_and_upload()

