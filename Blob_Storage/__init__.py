import os
from google.cloud import storage

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'C:\Users\shrut\Downloads\prime-rainfall-340817-72736d19063f.json'


def upload_blob(source_file_name, destination_blob_name):
    """Uploads a file to the bucket"""

    storage_client = storage.Client()
    bucket = storage_client.bucket("assignment3-bucket1")
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)