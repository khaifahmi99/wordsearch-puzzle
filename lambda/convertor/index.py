import boto3
import os
import urllib
import io
import markdown

s3 = boto3.client('s3')

# event: S3EventTrigger
def handler(event, context):
  # read in environment variables
  BUCKET_OUTPUT_DIR = os.environ['OUTPUT_DIR']

  if not BUCKET_OUTPUT_DIR:
    print("BUCKET_OUTPUT_DIR not set")
    raise Exception("BUCKET_OUTPUT_DIR not set")

  BUCKET_NAME = event['Records'][0]['s3']['bucket']['name']
  s3_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

  file_ext = s3_key.split('.')[-1].lower()
  if file_ext != 'md':
    print(f'Invalid file type - {s3_key}')
    raise Exception("Invalid file type")

  filename_with_ext = s3_key.split('/')[-1]
  filename = filename_with_ext.split('.')[0]
  INPUT_PATH = f'/tmp/{filename_with_ext}'
  OUTPUT_PATH = f'/tmp/{filename}.html'

  print(f'Downloading puzzle file from S3 - {filename_with_ext}')
  s3.download_file(BUCKET_NAME, s3_key, INPUT_PATH)

  print("Converting md to pdf")
  output = ''
  with open(INPUT_PATH) as f:
    markdown_content = f.read()
    markdown_content = markdown_content.replace('\n', '\n\n')
    output = markdown.markdown(markdown_content)
    output = output.replace('<h2>', '<h2 style="font-family: Courier">')
    output = output.replace('<p>', '<p style="font-family: Courier">')
    output = output.replace('<li>', '<li style="font-family: Courier">')

  with open(OUTPUT_PATH, 'w') as f:
    f.write(output)

  print("Uploading html to S3")
  if BUCKET_OUTPUT_DIR.endswith('/'):
    BUCKET_OUTPUT_DIR = BUCKET_OUTPUT_DIR[:-1]
  response = s3.upload_file(OUTPUT_PATH, BUCKET_NAME, f'{BUCKET_OUTPUT_DIR}/{filename}.html')

  os.remove(INPUT_PATH)
  os.remove(OUTPUT_PATH)


  print("Done")

  # path to uploaded S3 puzzle file (in MD format)
  return f'{BUCKET_OUTPUT_DIR}/{filename}.pdf'

# if __name__ == '__main__':
#   output = ''
#   with open('/tmp/test.md') as f:
#     markdown_content = f.read()

#     markdown_content = markdown_content.replace('\n', '\n\n')
#     output = markdown.markdown(markdown_content)
#     output = output.replace('<p>', '<p style="font-family: Courier">')
  
#   # save the output as a html file
#   with open('/tmp/test.html', 'w') as f:
#     f.write(output)
