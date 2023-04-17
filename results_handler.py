import json
from SutomRecord import SutomRecord, FILE_RESULTS_PATH
from leet import LEET
from discord import File
import random
from datetime import timedelta, datetime
from operator import itemgetter
import textwrap
import math

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
        json.dump(data, f, indent=4)
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
        # print("total_time", total_time)
        # print("number_ocr", number_ocr)
        return str(timedelta(seconds=(total_time / number_ocr)))
    except ZeroDivisionError:
        return "00:00:00"

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


def construct_result_message(player, client, graph=False) -> str:
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
    response += f"\t\tScore moyen : {player['mean_total_score']:.2f}\n"
    avg_time = str(player["avg_time"]).partition(".")[0]
    response += f"\t\tTemps moyen : 🕜 {avg_time} 🕜\n"
    response += f"\t*🏆 RANK 🏆 : {player['rank']}*\n"
    response += f"\t*Alternative rank : {player['rank']}*\n"

    # Display total number of games based on the score sum 
    response += f"\t\tNombre de parties jouées : {player['one_try'] + player['two_try'] + player['three_try'] + player['four_try'] + player['five_try'] + player['six_try'] + player['failed']}\n\n"

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


def compute_top(client, data, top_3=False, me=None, graph=False, time_delta=-1) -> str:
    response = "--- TABLEAU DES SCORES ---\n"
    top = []

    for record in data:
        # Skip the record if it's from more than 30 days
        if time_delta >= 0:
            date_format = "%Y-%m-%d"
            a = datetime.strptime(record.date_of_try, date_format)
            b = datetime.strptime(str(datetime.now().date()), date_format)
            # print((b - a).days)
            if (b - a).days > time_delta:
                continue
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
                    "mean_total_score" : 0,
                    "rank" : 0,
                    "alt_rank" : 0,
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
                top[index_of_user_id]["non_zero_avg_time"] += 1

    # Compute average time based on total time in each player
    for player in top:
        player["avg_time"] = compute_avg_time(
            player["non_zero_avg_time"], player["avg_time"]
        )
    
    # Compute new sorted score (number of game played / total score) key=mean_total_score
    for player in top:
        # mean_total_score 
        scores = [player[return_string_index(str(i))] * i for i in range(1, 7)]
        total_score = sum(scores)
        total_games_played = sum(player[return_string_index(str(i))] for i in range(1, 7))
        player["mean_total_score"] = total_score / total_games_played if total_games_played > 0 else 0
        player["rank"] = compute_rank(player, total_games_played)
        player["alt_rank"] = compute_alt_rank(player, total_games_played)

    # V1 : Sort by each type of score
    # top = sorted(top, key=itemgetter("one_try", "two_try", "three_try", "four_try", "five_try", "six_try"), reverse=True)
    # V2 : Sort by average score 
    # top = sorted(top, key=itemgetter("avg_score"))
    # V3 : Sort by mean score per game, deleted compute_avg_score function
    
    top = sorted(top, key=itemgetter("rank"), reverse=True)

    if me:
        if type(me) == str:  # Lance une Exception si non-existant
            me = int(me[2:-1])
        return construct_result_message(
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
        response += construct_result_message(player, client, graph)
        i += 1
        if top_3 and i > 2:
            break
    return response

def get_seconds(time_str):
    time_parts = time_str.split(':')
    seconds = float(time_parts[-1])
    if len(time_parts) > 2:
        minutes = int(time_parts[-2])
        seconds += minutes * 60
    if len(time_parts) > 2:
        hours = int(time_parts[-3])
        seconds += hours * 3600
    return int(seconds)

def compute_rank(player, total_games_played) -> int:
    if total_games_played == 0:
        return 0
    ## SCORE BY TRIES
    score = \
    player["one_try"] * 6 + \
    player["two_try"] * 5 + \
    player["three_try"] * 4 + \
    player["four_try"] * 3 + \
    player["five_try"] * 2 + \
    player["six_try"] * 1
    
    score = score / total_games_played

    ## SCORE BY AVERAGE TIME
    # bonus_by_time : percentage of boost despending of the average time in seconds, from 1 to 10 800 (3 hours)
    bonus_by_time = { 600 : 1.33, 1200 : 1.25, 1800 : 1.20, 2400 : 1.15, 3000 : 1.10, 3600 : 1.09, 4200 : 1.08, 4800 : 1.07, 5400 : 1.06, 6000 : 1.05, 6600 : 1.04, 8400 : 1.03, 9600 : 1.02, 10800 : 1.01}
    for time in bonus_by_time:
        if get_seconds(player["avg_time"]) <= time:
            score = score * bonus_by_time[time]
            # print("Attribution de bonus de temps : " + str(bonus_by_time[time]) + "pour un temps de " + player["avg_time"])
            break

    ## SCORE BY NUMER OF GAMES PLAYED
    # score = score + (score * total_games_played / 100)
    # More smooth version, the higher the number of games played, the less the score is impacted
    score = score + (score * math.log(total_games_played + 10))

    ## SCORE BY STREAKS
    ## TODO

    return math.trunc(score * 1000)

def compute_alt_rank(player, total_games_played) -> int:
    if total_games_played == 0:
        return 0
    ## SCORE BY TRIES
    score = \
    player["one_try"] * 6 + \
    player["two_try"] * 5 + \
    player["three_try"] * 4 + \
    player["four_try"] * 3 + \
    player["five_try"] * 2 + \
    player["six_try"] * 1
    
    score = score / total_games_played

    ## SCORE BY AVERAGE TIME
    # bonus_by_time : percentage of boost despending of the average time in seconds, from 1 to 10 800 (3 hours)
    # bonus_by_time = { 600 : 1.33, 1200 : 1.25, 1800 : 1.20, 2400 : 1.15, 3000 : 1.10, 3600 : 1.09, 4200 : 1.08, 4800 : 1.07, 5400 : 1.06, 6000 : 1.05, 6600 : 1.04, 8400 : 1.03, 9600 : 1.02, 10800 : 1.01}
    # for time in bonus_by_time:
    #     if get_seconds(player["avg_time"]) <= time:
    #         score = score * bonus_by_time[time]
    #         # print("Attribution de bonus de temps : " + str(bonus_by_time[time]) + "pour un temps de " + player["avg_time"])
    #         break

    ## Penality when total_games_played < 50
    score = score * math.sqrt(min(total_games_played/50,1))

    return math.trunc(score * 1000)

def print_console_results(file_path: str):
    with open(file_path, "r") as f:
        data = json.load(f)
    for record in data:
        print(record)


# TODO: number of game played, .player [player_name]
async def send_results_command(command: str, client, channel_sutom, me=None):

    arg = ""

    # Casse le code en fonction du message parsé
    """if command[2] != "":
        arg = command[2]
    command = command[0] """
    print(command)
    help = textwrap.dedent(
        """```
.h or .help     Aide\n \
.top            Top 3 des meilleurs joueurs\n \
.list           Liste tous les joueurs et leurs stats\n \
.today          Liste des parties d'aujourd'hui\n \
.yesterday      Liste des parties d'hier\n \
.week           Liste des parties de la semaine\n \
.month          Liste des parties du mois\n \
.me             Mes stats\n \
.player @player Stats du joueur\n \
.rank           Explication du rank score\n \
.bonus_temps    Explication du bonus de temps utilisé dans le rank score\n \
.graph          Affiche un graph des parties jouées\n \
.takeda         takeda\n \
.leet           is it ? 👾```"""
    )
    rank_message = textwrap.dedent(
        """```
Le classement est calculé à l'aide de trois critères : le nombre d'essais moyen du joueur pour terminer une partie, le temps moyen pris pour terminer ces parties et le nombre total de parties jouées.\n
Le premier critère est le nombre d'essais. Le score est calculé en multipliant le nombre d'essais de chaque type (un, deux, trois, quatre, cinq et six essais) par un poids correspondant (respectivement 6, 5, 4, 3, 2 et 1).\n
La fonction calcule ensuite le score moyen par partie en divisant le score total par le nombre total de parties jouées.\n
Le deuxième critère est le score par temps moyen. La fonction applique un bonus au score du joueur en fonction de son temps moyen, mesuré en secondes. Le bonus est un pourcentage d'augmentation qui dépend du temps moyen, allant de 1 % à 33 %. Plus le temps moyen est long, plus le bonus est faible. Vous pouvez utiliser .bonus_temps pour obtenir les multiplicateurs.\n
Le troisième critère est le score en fonction du nombre total de parties jouées. La fonction applique un bonus au score du joueur en fonction du nombre de parties jouées. Le bonus est une fonction logarithmique qui augmente avec le nombre de parties jouées, mais qui a un rendement décroissant. Cela signifie que plus un joueur a joué de parties, moins chaque partie supplémentaire a d'impact sur son score.\n
Le résultat final de la fonction est le rang du joueur, exprimé sous la forme d'un nombre entier. Plus le rang est élevé, meilleure est la performance du joueur.\n

```"""
    )
    # TODO : hardcodé, à changer dans une fonction qui compute le dict mis en général
    bonus_time = textwrap.dedent(
        """```
Si en dessous de : bonus ajouté
\thh:mm:ss : %
\t00:10:00 : 1.33%
\t00:20:00 : 1.25%
\t00:30:00 : 1.20%
\t00:40:00 : 1.15%
\t00:50:00 : 1.10%
\t01:00:00 : 1.09%
\t01:10:00 : 1.08%
\t01:20:00 : 1.07%
\t01:30:00 : 1.06%
\t01:40:00 : 1.05%
\t01:50:00 : 1.04%
\t02:20:00 : 1.03%
\t02:40:00 : 1.02%
\t03:00:00 : 1.01%
        ```""")

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

    if command == ".month":
        await channel_sutom.send(
            compute_top(client, read_results(FILE_RESULTS_PATH), False, None, False, 30)
        )
        return

    if command == ".week":
        await channel_sutom.send(
            compute_top(client, read_results(FILE_RESULTS_PATH), False, None, False, 7)
        )
        return

    if command == ".me":
        await channel_sutom.send(
            compute_top(client, read_results(FILE_RESULTS_PATH), False, me)
        )
        return

    if command == ".player":
        # print(arg)
        await channel_sutom.send(
            "Commande non fonctionnelle : désactivée"
            # compute_top(client, read_results(FILE_RESULTS_PATH), False, arg)
        )
        return

    if command == ".rank":
        await channel_sutom.send(rank_message)
        return

    if command == ".bonus_temps":
        await channel_sutom.send(bonus_time)
        return

    if command == ".graph":
        await channel_sutom.send(
            # compute_top(client, read_results(FILE_RESULTS_PATH), False, arg, True)
            "Commande non fonctionnelle : désactivée"
        )
        await channel_sutom.send(file=File("graph.png"))
        return

    if command == ".status":
        latency = str(client.latency).partition(".")[2]
        latency = latency[0:3] + "ms"
        await channel_sutom.send(f"Time : {str(datetime.now()).partition('.')[0]} ping : {latency}")
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
