from __future__ import print_function
import pickle, os.path, pprint
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

fileList = []
filePermissions = []
parentFolder = 'PARENT_FOLDER_ID'
ingore_domain = 'ignoreDomain.com'
knownFolders = []
list1 = []

def get_files_in_folder(service, folder_id):
  global fileList
  page_token = None
  while True:
    try:
      param = {}
      if page_token:
        param['pageToken'] = page_token
      children = service.children().list(folderId=folder_id, **param).execute()
      for child in children.get('items', []):
        fileList.append(child['id'])
      page_token = children.get('nextPageToken')
      if not page_token:break
    except errors.HttpError:
        print('An error occurred')
        break

def remove_permissions(service, file_id, permission_id):
  try:
    service.permissions().delete(fileId=file_id, permissionId=permission_id).execute()
    print(f"Removing Permissions for File with ID: {file_id}")
  except errors.HttpError:
    print(f"UNABLE TO REMOVE PERMISSIONS: {file_id}")

def get_file_permissions(service, file_id):
  try:
    file = service.permissions().list(fileId=file_id).execute()
    for f in file['items']:
      permissionId = f['id']
      # email = f['emailAddress']
      try:
        domain = f['domain']
      except KeyError:
        continue
      if domain.lower() == ignore_domain:
        print(f"Not removing INTERNAL permissions")
      else:
        print(f"Removing permissions for: {file_id}")
        remove_permissions(service,file_id,permissionId)
  except errors.HttpError:
    print(f"An error occurred: {error}")


def main():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('drive', 'v2', credentials=creds)
    get_files_in_folder(service,parentFolder)
    list1 = fileList
    for l in list1:
        print(f"Current Working File: {l}")
        get_files_in_folder(service,l)
    for f in fileList:
      print(f"Getting Permissions for: {f}")
      get_file_permissions(service,f)


if __name__ == '__main__':
    main()
