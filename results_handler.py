import json
import SutomTry

def write_json(file_path, sutom_results):
  with open(file_path, 'r') as f:
    data = json.load(f)

  data['discord_id'] = '1234567890'
  data['results'] = [1, 2, 3]
  data['time'] = '12:00:00'
  data['date'] = '2022-12-10'

  with open(file_path, 'w') as f:
    json.dump(data, f)

def read_results(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)