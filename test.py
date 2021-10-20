from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import datetime

gauth = GoogleAuth()
gauth.LoadCredentialsFile("credentials.json")
if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()
gauth.SaveCredentialsFile("credentials.json")

# Create GoogleDrive instance with authenticated GoogleAuth instance
drive = GoogleDrive(gauth)

# Auto-iterate through all files in the root folder.
file_list = drive.ListFile(
    {'q': "mimeType='image/jpeg' and trashed=false"}).GetList()
print("LATEST: ", file_list[0]["id"])
media_url = ("https://drive.google.com/uc?export=view&id=" +
             str(file_list[0]["id"]))
media_date = datetime.now()
print({"media": media_url}, {"media_date": media_date.isoformat()})
for file1 in file_list:
    print('title: %s, id: %s' % (file1['title'], file1['id']))
