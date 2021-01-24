from __future__ import print_function
import pickle
import os.path
import io
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors
from operator import itemgetter, attrgetter
from apiclient.http import MediaIoBaseDownload
from monkeylearn import MonkeyLearn

# If modifying these scopes, delete the file drive.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/drive.readonly']


def retrieve_all_files(service):
    """Retrieve a list of File resources.

    Args:
      service: Drive API service instance.
    Returns:
      List of File resources.
    """
    result = []
    page_token = None
    while True:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token
            param['corpora'] = 'user'
            # param['driveId'] = 'root'
            # param['shared'] = 'false'  #  get API error when using this or "trashed"
            param['includeItemsFromAllDrives'] = 'false'
            param['supportsAllDrives'] = 'false'
            param['orderBy'] = 'name'
            param['fields'] = '*'
            param['q'] = "trashed = false"  # "mimeType contains '.folder' and trashed = false"

            files = service.files().list(**param).execute()

            result.extend(files['files'])
            page_token = files.get('nextPageToken')
            if not page_token:
                break
        except errors.HttpError as error:
            print('An error occurred: %s' % error)
            break
    return result


def download_file(service, file_id, mimeType, filename):
    if "google-apps" in mimeType:
        return
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(filename, 'wb')  # io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    return  # use with io.BytesIO  fh.getvalue()


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the files the user has access to.
    """
    creds = None
    # The file drive.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('drive.pickle'):
        with open('drive.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'driveCredentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('drive.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    # results = service.files().list(
    #     pageSize=10, fields="nextPageToken, files(id, name)").execute()

    f = retrieve_all_files(service)

    for item in f:
        if item['id'] == '1ht6PMhI5JIcaQLqgsMBQhwOIIlHYr455':
            download_file(service, item['id'], item['mimeType'], 'temp.txt')
            tf = open('temp.txt', 'r')
            txt = tf.read()
            tf.close()
            ml = MonkeyLearn('ed48b60fefe026fce0c8220fbbfbdad812c5a7c0')
            data = [txt]
            model_id = 'ex_YCya9nrn'
            result = ml.extractors.extract(model_id, data)
            # json_data = json.loads(result)
            json_data = result.body[0]
            for keyword in json_data['extractions']:
                print(keyword['parsed_value'])

            print("that's it")

            return

        dtype = item['mimeType']  # get the mime type
        try:
            p = item['parents']
        except:
            p = ['NONE']
        print('%s: \t %s ' % (item['id'], item['name']))  # item['id']))
    print("%d Document(s)" % len(f))
    # print(f[0])


if __name__ == '__main__':
    main()
