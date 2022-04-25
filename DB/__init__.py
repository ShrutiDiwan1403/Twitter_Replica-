import os
from google.cloud import datastore


os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
client = datastore.Client("prime-rainfall-340817")