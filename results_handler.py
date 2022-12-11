import json
import SutomTry

"""
 Returns -1 if record for the day and the user already exist
"""
def write_results(file_path: str, sutom_results: SutomTry) -> int:
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = []
    
    for record in data:
        if (record.get("date_of_try") == sutom_results.date_of_try and record.get("user_id") == sutom_results.user_id):
            return -1

    record = dict()
    record["user_id"] = sutom_results.user_id
    record["sutom_number"] = sutom_results.sutom_number
    record["number_of_try"] = sutom_results.number_of_try
    record["word_len"] = sutom_results.word_len
    record["time_to_guess"] = sutom_results.time_to_guess
    record["date_of_try"] = sutom_results.date_of_try

    data.append(record)

    with open(file_path, 'w') as f:
        json.dump(data, f)
    return 0

def print_console_results(file_path: str):
    with open(file_path, 'r') as f:
        data = json.load(f)
    for record in data:
        print(record)

def send_results_command(command: str):
  if command == "":
    pass