import boto3
import sys
import json
import os
from WordSearch import WordSearch
import urllib

s3 = boto3.client('s3')

def handler(event, context):
  DIMENSION = 20

  # read in environment variables
  BUCKET_OUTPUT_DIR = os.environ['OUTPUT_DIR']

  if not BUCKET_OUTPUT_DIR:
    print("BUCKET_OUTPUT_DIR not set")
    raise Exception("BUCKET_OUTPUT_DIR not set")

  BUCKET_NAME = event['Records'][0]['s3']['bucket']['name']
  s3_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

  file_ext = s3_key.split('.')[-1].lower()
  if file_ext != 'json':
    print(f'Invalid file type - {s3_key}')
    raise Exception("Invalid file type")

  filename_with_ext = s3_key.split('/')[-1]
  filename = filename_with_ext.split('.')[0]
  INPUT_PATH = f'/tmp/{filename_with_ext}'
  OUTPUT_PATH = f'/tmp/{filename}.md'

  print(f'Pulling list of words from S3 - {filename_with_ext}')
  s3.download_file(BUCKET_NAME, s3_key, INPUT_PATH)

  words = []

  # read the words from the file content (json)
  try:
    with open(INPUT_PATH, 'r') as f:
      content = json.load(f)
      keys = content.keys()
      for key in keys:
        if key != 'title':
          words.append(content[key].upper())
  except Exception as e:
    print(f'Error reading file content - {e}')
    raise e

  print(f'Generating Puzzle...({len(words)} words)')
  print(words)
  w = WordSearch(words, DIMENSION, 15)

  # Redirect print output to OUTPUT_PATH
  sys.stdout = open(OUTPUT_PATH, 'a')
  print("## Puzzle")
  for line in w.grid:
      l = ''
      for letter in line:
          l += letter
          l += ' '
      print(l)
  # Restore the original stdout
  sys.stdout = sys.__stdout__

  print("Uploading Puzzle to S3")
  if BUCKET_OUTPUT_DIR.endswith('/'):
    BUCKET_OUTPUT_DIR = BUCKET_OUTPUT_DIR[:-1]
  response = s3.upload_file(OUTPUT_PATH, BUCKET_NAME, f'{BUCKET_OUTPUT_DIR}/{filename}.md')

  os.remove(INPUT_PATH)
  os.remove(OUTPUT_PATH)

  print("Done")

  # path to uploaded S3 puzzle file (in MD format)
  return f'{BUCKET_OUTPUT_DIR}/{filename}.md'