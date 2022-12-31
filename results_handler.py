import json
from SutomRecord import SutomRecord, FILE_RESULTS_PATH
from leet import LEET
from discord import File
import random
from datetime import timedelta, datetime
from operator import itemgetter
import textwrap

from dotenv import load_dotenv
import os

import matplotlib.pyplot as plt

"""
 Returns -1 if record for the day and the user already exist
"""


def write_results(file_path: str, sutom_results: SutomRecord) -> int:
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = []

    for record in data:
        if (
            record.get("date_of_try") == sutom_results.date_of_try
            and record.get("user_id") == sutom_results.user_id
        ):
            return -1

    record = dict()
    record["user_id"] = sutom_results.user_id
    record["sutom_number"] = sutom_results.sutom_number
    record["number_of_try"] = sutom_results.number_of_try
    record["time_to_guess"] = sutom_results.time_to_guess
    record["date_of_try"] = sutom_results.date_of_try

    data.append(record)

    with open(file_path, "w") as f:
        json.dump(data, f)
    return 0


def read_results(file_path) -> dict:
    all_records = []
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            for r in data:
                read_record = SutomRecord(
                    r["user_id"],
                    r["sutom_number"],
                    r["number_of_try"],
                    r["date_of_try"],
                    r["time_to_guess"],
                )
                all_records.append(read_record)

    except json.JSONDecodeError:
        print("RESULTS FILE IS CORRUPTED")
        all_records = []
    return all_records


def compute_avg_time_from_str_timestamp(new_time: int, avg_time: int) -> str:
    times = [new_time, avg_time]
    # @src https://stackoverflow.com/questions/12033905/using-python-to-create-an-average-out-of-a-list-of-times
    return str(
        timedelta(
            seconds=sum(
                map(
                    lambda f: int(f[0]) * 3600 + int(f[1]) * 60 + int(f[2]),
                    map(lambda f: f.split(":"), times),
                )
            )
            / len(times)
        )
    ).partition(".")[0]


def compute_avg_time(number_ocr: int, total_time: int) -> str:
    try:
        return str(timedelta(seconds=(total_time / number_ocr)))
    except ZeroDivisionError:
        return "00:00:00"
    """ args : {"user_id": user_id, "one_try": 0, "two_try": 0, "three_try": 0, "four_try": 0, "five_try": 0, "six_try": 0, "failed": 0, "avg_time": 0}
    """


def compute_avg_score(player: dict) -> float:
    number_of_game = (
        player["one_try"]
        + player["two_try"]
        + player["three_try"]
        + player["four_try"]
        + player["five_try"]
        + player["six_try"]
        + player["failed"]
    )

    tot = (
        player["one_try"]
        + player["two_try"] * 2
        + player["three_try"] * 3
        + player["four_try"] * 4
        + player["five_try"] * 5
        + player["six_try"] * 6
    )

    return tot / number_of_game


# This one is a ChatGPT result
def return_string_index(index: str) -> str:
    return {
        "1": "one_try",
        "2": "two_try",
        "3": "three_try",
        "4": "four_try",
        "5": "five_try",
        "6": "six_try",
    }.get(index, "failed")


def get_results_by_date(today: bool, data, client) -> str:
    response = ""
    if today:
        t_delta = timedelta(days=0)
    else:
        t_delta = timedelta(days=1)
    for player in data:
        if player.date_of_try == str(datetime.now().date() - t_delta):
            try:
                response += f"**{(client.get_user(player.user_id)).display_name}**   \n"
            except AttributeError:
                response += f"**{player.user_id}** (est ce qu'il/elle a quitté le serveur ? 👀) \n"
            response += f"\t{player.number_of_try}/6 in {str(timedelta(seconds=(player.time_to_guess)))}\n"
            response += "\n"
    if response:
        return response
    return "Pas de résultat 😒"


def contruct_result_message(player, client, graph=False) -> str:
    avg_time = "00:00:00"
    response = ""
    # Possible only if called by .me
    if player == None:
        return "Pas (encore) de résultat pour toi! 🤖"
    try:
        response += f"**{(client.get_user(player['user_id'])).display_name}**   \n"
    except AttributeError:
        response += (
            f"{(player['user_id'])} (est ce qu'il/elle a quitté le serveur ? 👀) \n"
        )
    response += f"\t\t{player['one_try']} : 1/6\n"
    response += f"\t\t{player['two_try']} : 2/6\n"
    response += f"\t\t{player['three_try']} : 3/6\n"
    response += f"\t\t{player['four_try']} : 4/6\n"
    response += f"\t\t{player['five_try']} : 5/6\n"
    response += f"\t\t{player['six_try']} : 6/6\n"
    response += f"\t\t{player['failed']} : -/6\n"
    response += f"\t\tScore moyen : {player['avg_score']:.2f}\n"
    avg_time = str(player["avg_time"]).partition(".")[0]
    response += f"\t\tTemps moyen : 🕜 {avg_time} 🕜\n\n"
    if graph:
        plt.bar(
            [1, 2, 3, 4, 5, 6],
            height=[
                player["one_try"],
                player["two_try"],
                player["three_try"],
                player["four_try"],
                player["five_try"],
                player["six_try"],
            ],
            color="red",
        )
        plt.xticks([1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6])
        plt.xlabel("Score")
        plt.savefig("graph.png")

    return response


def compute_top(client, data, top_3=False, me=None, graph=False) -> str:
    response = "🏆 TABLEAU DES SCORES 🏆\n"
    top = []

    for record in data:

        # Adding new user to the top list
        if not any(d.get("user_id", None) == record.user_id for d in top):
            top.append(
                {
                    "user_id": record.user_id,
                    "one_try": 0,
                    "two_try": 0,
                    "three_try": 0,
                    "four_try": 0,
                    "five_try": 0,
                    "six_try": 0,
                    "failed": 0,
                    "avg_time": record.time_to_guess,
                    "non_zero_avg_time": 0,
                }
            )

            # Adding his first try
            top[len(top) - 1][return_string_index(record.number_of_try)] = 1
            if record.time_to_guess != 0:
                top[len(top) - 1]["non_zero_avg_time"] = 1

        else:
            # Adding his try  ( top[index_of_user_id] )  to the top list
            index_of_user_id = next(
                (i for i, item in enumerate(top) if item["user_id"] == record.user_id),
                None,
            )

            index_of_user_id = int(index_of_user_id)
            top[index_of_user_id][return_string_index(record.number_of_try)] += 1
            if record.time_to_guess != 0:
                top[index_of_user_id]["avg_time"] += record.time_to_guess

    # Compute average time based on total time in each player
    for player in top:
        player["avg_time"] = compute_avg_time(
            player["non_zero_avg_time"], player["avg_time"]
        )

    # Sort by each type of score
    # top = sorted(top, key=itemgetter("one_try", "two_try", "three_try", "four_try", "five_try", "six_try"), reverse=True)

    for player in top:
        player["avg_score"] = compute_avg_score(player)
    top = sorted(top, key=itemgetter("avg_score"))

    if me:
        if type(me) == str:  # Lance une Exception si non-existant
            me = int(me[2:-1])
        return contruct_result_message(
            next((p for p in top if p["user_id"] == me), None), client, graph
        )

    i = 0
    for player in top:
        if i == 0:
            response += "🥇"
        if i == 1:
            response += "🥈"
        if i == 2:
            response += "🥉"
        if i not in [0, 1, 2]:
            response += f"{i+1}. "
        response += contruct_result_message(player, client, graph)
        i += 1
        if top_3 and i > 2:
            break
    return response


def print_console_results(file_path: str):
    with open(file_path, "r") as f:
        data = json.load(f)
    for record in data:
        print(record)


# TODO: number of game played, .player [player_name]
async def send_results_command(command: str, client, channel_sutom, me=None):

    arg = ""

    if command[2] != "":
        arg = command[2]
    command = command[0]

    help = textwrap.dedent(
        """```
     .h or .help    Aide\n \
    .top            Top 3 des meilleurs joueurs par nombre de
                     tentative\n \
    .list           Liste tous les joueurs et leurs stats\n \
    .today          Liste des parties d'aujourd'hui\n \
    .yesterday      Liste des parties d'hier\n \
    .me             Mes stats\n \
    .player @player Stats du joueur\n \
    .graph          Affiche un graph des parties jouées \
    .takeda         takeda\n \
    .leet           is it ? 👾```"""
    )

    if command == ".h" or command == ".help":
        await channel_sutom.send(help)
        return

    if command == ".top":
        await channel_sutom.send(
            compute_top(client, read_results(FILE_RESULTS_PATH), True)
        )
        return

    if command == ".today":
        await channel_sutom.send(
            get_results_by_date(True, read_results(FILE_RESULTS_PATH), client)
        )
        return

    if command == ".list":
        await channel_sutom.send(compute_top(client, read_results(FILE_RESULTS_PATH)))
        return

    if command == ".yesterday":
        await channel_sutom.send(
            get_results_by_date(False, read_results(FILE_RESULTS_PATH), client)
        )
        return

    if command == ".me":
        await channel_sutom.send(
            compute_top(client, read_results(FILE_RESULTS_PATH), False, me)
        )
        return

    if command == ".player":
        print(arg)
        await channel_sutom.send(
            "Commande non fonctionnelle : désactivée"
            # compute_top(client, read_results(FILE_RESULTS_PATH), False, arg)
        )
        return

    if command == ".graph":
        await channel_sutom.send(
            # compute_top(client, read_results(FILE_RESULTS_PATH), False, arg, True)
            "Commande non fonctionnelle : désactivée"
        )
        await channel_sutom.send(file=File("graph.png"))
        return

    if command == ".status":
        await channel_sutom.send(f"Time : {datetime.now()} ping : {client.latency}")
        return

    if command == ".leet":
        if datetime.now().hour == 13 and datetime.now().minute == 37:
            leet_index = random.randint(0, 3)
            await channel_sutom.send(LEET[leet_index])
            return

        else:
            await channel_sutom.send("It's not leet... 🤖")
            return

    # TODO : Vrai systeme d'un joker/semaine (ne modifie pas la moyenne) et pennaliser les joueurs qui ne postent pas tous les jours
    if command == ".joker":
        await channel_sutom.send("ses luient 🤡 🃏")
        return

    if command == ".takeda":
        await channel_sutom.send(file=File("takeda.png"))
        return

    await channel_sutom.send(f"Commande non valide 🙄 Liste des commandes .h ou .help\n")
    return
