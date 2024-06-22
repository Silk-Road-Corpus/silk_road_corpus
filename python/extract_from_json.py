import json
import re

from google.cloud import storage


def extract_from_json(gcs_destination_uri):
  storage_client = storage.Client()
  match = re.match(r"gs://([^/]+)/(.+)", gcs_destination_uri)
  bucket_name = match.group(1)
  prefix = match.group(2)
  bucket = storage_client.get_bucket(bucket_name)
  # List objects with the given prefix, filtering out folders.
  blob_list = [
    blob
    for blob in list(bucket.list_blobs(prefix=prefix))
    if not blob.name.endswith("/")
  ]
  print("Output files:")
  for blob in blob_list:
    print(blob.name)
    try:
      json_string = blob.download_as_bytes().decode("utf-8")
      response = json.loads(json_string)
      first_page_response = response["responses"][0]
      annotation = first_page_response["fullTextAnnotation"]
      print("Full text:\n")
      print(annotation["text"])
    except:
      print("Exception occurred")


if __name__ == '__main__':
  extract_from_json("gs://silk-road-corpus-content/conze_e._the_prajnaparamita_literature")