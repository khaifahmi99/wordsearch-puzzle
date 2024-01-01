def handler(event, context):

  print(event)
  print(context)

  print("Pulling list of words from S3")
  print("Generating Puzzle...")
  print("Uploading Puzzle to S3")
  print("Done")

  # path to uploaded S3 puzzle file (in MD format)
  return "/generated/example.md"