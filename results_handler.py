import json
from SutomTry import SutomTry, FILE_RESULTS_PATH
from datetime import timedelta
from operator import itemgetter
import textwrap

from dotenv import load_dotenv
import os

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

def read_results(file_path) -> dict:
    try:
        file_result = []
        with open(file_path, 'r') as f:
            data = json.load(f)
            for r in data:
                    data_result = SutomTry(r["user_id"], r["sutom_number"], r["number_of_try"], r["word_len"], r["date_of_try"], r["time_to_guess"])
                    file_result.append(data_result)

    except json.JSONDecodeError:
        data = []
    return file_result

def compute_avg_time(new_time: int, avg_time: int) -> str:
    times = [new_time, avg_time]
    # @src https://stackoverflow.com/questions/12033905/using-python-to-create-an-average-out-of-a-list-of-times
    return str(timedelta(seconds=sum(map(lambda f: int(f[0])*3600 + int(f[1])*60 + int(f[2]), map(lambda f: f.split(':'), times)))/len(times))).partition(".")[0]
    
# This one is a ChatGPT result
def return_string_index(index: int) -> str:
      return {
        "1": "one_try",
        "2": "two_try",
        "3": "three_try",
        "4": "four_try",
        "5": "five_try",
        "6": "six_try"
  }.get(index, "failed")

# TODO: record every game in second and compute the average based in these instead of recomputing the mean
def compute_top(data: dict, top_3 = False) -> str:
    at = "@"
    response = "🏆 Here's the scoreboard 🏆\n"
    top = []
    for record in data:
        if not any(d.get("user_id", None) == record.user_id for d in top):
            top.append({"user_id": record.user_id, "one_try": 0, "two_try": 0, "three_try": 0, "four_try": 0, "five_try": 0, "six_try": 0, "failed": 0, "avg_time": record.time_to_guess})
            top[len(top)-1][return_string_index(record.number_of_try)] = 1
        else:
            index_of_user_id = next((i for i, item in enumerate(top) if item["user_id"] == record.user_id), None)
            top[index_of_user_id][return_string_index(record.number_of_try)] += 1
            if record.time_to_guess != "00:00:00":
                top[index_of_user_id]["avg_time"] = compute_avg_time(top[index_of_user_id]["avg_time"], record.time_to_guess)
    # Sort
    top = sorted(top, key=itemgetter("one_try", "two_try", "three_try", "four_try", "five_try", "six_try"), reverse=True)
    i = 0
    for player in top:
        if i == 0:
            response += "🥇"
        if i == 1:
            response += "🥈"
        if i == 2:
            response += "🥉"
        if i not in [0,1,2]:
            response += f"{i}. "
        response += f"\t<{at}{player['user_id']}>\n"
        response += f"\t\t{player['one_try']} : 1/6\n"
        response += f"\t\t{player['two_try']} : 2/6\n"
        response += f"\t\t{player['three_try']} : 3/6\n"
        response += f"\t\t{player['four_try']} : 4/6\n"
        response += f"\t\t{player['five_try']} : 5/6\n"
        response += f"\t\t{player['six_try']} : 6/6\n"
        response += f"\t\t{player['failed']} : -/6\n"
        response += f"\t\tAverage time to guess : 🕜 {player['avg_time']} 🕜\n"
        i += 1
        if (top_3 and i < 2):
            break
    return response


def print_console_results(file_path: str):
    with open(file_path, 'r') as f:
        data = json.load(f)
    for record in data:
        print(record)

    """ List of commands:
    /h or /help
    /top
    /list
    /yesterday
    /me

    """
    # TODO: Implement a more beautiful way than the if pick
    # TODO: Graph with pyplot
def send_results_command(command: str):
    HIDDEN_COMMAND_1 = os.getenv('HIDDEN_COMMAND_1')
    HIDDEN_COMMAND_2 = os.getenv('HIDDEN_COMMAND_2')
    HIDDEN_COMMAND_3 = os.getenv('HIDDEN_COMMAND_3')
    commands = textwrap.dedent("""```
     .h or .help    Cet aide\n \
    .top           Top 3 des meilleurs joueurs par nombre de tentative\n \
    .list          Liste tous les joueurs et leurs stats\n \
    .yesterday     Liste des parties d'hier\n \
    .me            Mes stats\n```""")
    if command == ".h" or command == ".help":
        return commands
    if command == ".top":
        return compute_top(read_results(FILE_RESULTS_PATH), True)
    if command == ".list":
        return compute_top(read_results(FILE_RESULTS_PATH))
    if command == ".yesterday":
        return "```Not yet implemented```"
    if command == ".me":
        return "```Not yet implemented```"
    return f"Commande non valide. Liste des commandes (.h ou .help) :\n{commands}" 