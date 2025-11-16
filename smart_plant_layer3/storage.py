from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes pour Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Crée le flow OAuth
flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json', SCOPES)
creds = flow.run_local_server(port=0)  # ouvre le navigateur pour te connecter

# Crée le service Drive
service = build('drive', 'v3', credentials=creds)

# Uploader un fichier
file_metadata = {'name': 'pic.png'}  # nom sur Drive
media = MediaFileUpload('pic.png', mimetype='image/png')

file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id'
).execute()

print(f"Fichier uploadé avec succès, ID: {file.get('id')}")
