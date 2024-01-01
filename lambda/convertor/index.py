def handler(event, context):
  
  print(event)
  print(context)

  print("Pulling the puzzle from S3")
  print("Converting md to pdf")
  print("Uploading pdf to S3")
  print("Done")

  # path to uploaded S3 puzzle file (in MD format)
  return "/puzzle/example.pdf"