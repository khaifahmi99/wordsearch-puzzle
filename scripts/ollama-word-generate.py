'''
$ python ollama-word-generate.py <topic> [options]

Options:
- model: 
    description: the model name that ollama supports. The list of models can be found here: https://ollama.ai/library
    default: llama2:13b
- endpoint:
    description: the endpoint of the ollama server (including the port)
    default: http://localhost:11434
- `--debug`: false (default)

Example Usage:
$ python3 ollama-word-generate.py colours
$ python3 ollama-word-generate.py "board game" "llama2:13b" "http://myserver.com:11434" --debug
'''

import requests
import json
import sys


params = sys.argv
if len(params) >= 2:
    topic=params[1]
else:
    raise Exception("Insufficient argument")

# TODO: Use argparser to parse the arg better
model = "llama2:13b"
if len(params) >= 3:
    model = params[2]

endpoint = "http://localhost:11434"
if len(params) >= 4:
    endpoint = params[3]
if endpoint[-1] == "/":
    endpoint = endpoint[:-1]

debug = False
if len(params) >= 5:
    debug = params[4] == '--debug' or params[4] == '--debug=true' or params[4] == '--debug=1'

template = {
    "title": "{title} Word Search",
    "0": "",
    "1": "",
    "2": "",
    "3": "",
    "4": "",
    "5": "",
    "6": "",
    "7": "",
    "8": "",
    "9": ""
}

rules = """
1. Word should be appropriate for kids
2. Word should be a single word, no spaces or special characters
3. Word should be simple for kids, not too complex
"""

prompt = f"Generate exactly 10 words for kids' word search puzzle based on the topic '{topic}'. \nUse the following template: {json.dumps(template)}.\nIt should follow such rules: {rules}.\nFill in the title with the topic and the words array have 10 items. The generated word should not be too long, maximise it to 10 and the word should not have spaces. Only output the JSON object and nothing else. This is so that the output can easily be ingested into jq or represented as the content for a JSON file"

if debug:
  print(prompt)

data = {
    "prompt": prompt,
    "model": model,
    "format": "json",
    "stream": False,
    "options": {"temperature": 2.5, "top_p": 0.99, "top_k": 100},
}

response = requests.post(f'{endpoint}/api/generate', json=data, stream=False)
json_data = json.loads(response.text)

if debug:
  print(json_data)
  print("")

print(json.dumps(json.loads(json_data["response"]), indent=2))

