import json
import SutomTry
from datetime import timedelta
from operator import itemgetter

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
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = []
    return data

def compute_avg_time(new_time: int, avg_time: int) -> str:
    times = [new_time, avg_time]
    # @src https://stackoverflow.com/questions/12033905/using-python-to-create-an-average-out-of-a-list-of-times
    return str(timedelta(seconds=sum(map(lambda f: int(f[0])*3600 + int(f[1])*60 + int(f[2]), map(lambda f: f.split(':'), times)))/len(times)))
    

def compute_top(data: dict, top_3 = False) -> str:
    response = "🏆 Here's the scoreboard 🏆\n"
    top = []
    for record in data:
        if not any(d.get("user_id", None) == record.user_id for d in top):
            top.append({"id": record.user_id, "one_try": 0, "two_try": 0, "three_try": 0, "four_try": 0, "five_try": 0, "six_try": 0, "failed": 0, "avg_time": None})
            top[len(top)-1][f"{record.number_of_try}"] = 1
        else:
            top[top.index(record.user_id)][f"{record.number_of_try}"] += 1
            top[top.index(record.user_id)]["avg_time"] = compute_avg_time(top[top.index(record.user_id)]["avg_time"], record.time_to_guess)
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
        response += f"\t{player.user_id}\n"
        response += f"\t\t{player.one}/6\n"
        response += f"\t\t{player.two}/6\n"
        response += f"\t\t{player.three}/6\n"
        response += f"\t\t{player.four}/6\n"
        response += f"\t\t{player.five}/6\n"
        response += f"\t\t{player.six}/6\n"
        response += f"\t\t{player.failed}/6\n"
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
    commands = "\t/h or /help  Cet aide \
                \t/top         Top 3 des meilleurs joueurs par nombre de tentative\n \
                \t/list        Liste tous les joueurs et leurs stats\n \
                \t/yesterday   Liste des parties d'hier\n \
                \t/me          Mes stats\n"
    response = ""
    if command == "/h" or command == "/help":
        response = commands
    if command == "/top":
        response = compute_top(read_results(SutomTry.FILE_RESULTS_PATH), True)
    if command == "/list":
        response = compute_top(read_results(SutomTry.FILE_RESULTS_PATH))
    if command == "/yesterday":
        pass
    if command == "/me":
        pass
    return f"```Commande non valide. Liste des commandes (/h ou /help) :\n \
                {commands}\
            ```" 