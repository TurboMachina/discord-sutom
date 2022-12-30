import os, sys, getopt
import discord
from dotenv import load_dotenv
from datetime import datetime
import git

from SutomTry import SutomTry, FILE_RESULTS_PATH
import results_handler as rd

HELP_MSG = "main.py -t --test / -r --run"


# Example of fetched message :
""" 
#SUTOM #999 4/6 13:37
#SUTOM #999 -/6 1h37:37
#SUTOM #999 0/6 13h37:37
#SUTOM #9999 -/6 1h37:37

🟥🟦🟡🟡🟡🟦🟡
🟥🟥🟦🟡🟡🟡🟦
🟥🟥🟡🟡🟡🟦🟡
🟥🟥🟥🟥🟥🟥🟥

https://sutom.nocle.fr
"""


def timestamp_to_second(timestamp: int) -> str:
    h = int(timestamp.partition(":")[0])
    m = int(timestamp.partition(":")[2].partition(":")[0])
    s = int(timestamp.partition(":")[2].partition(":")[2])
    seconds = (3600 * h) + (60 * m) + s
    return seconds


def is_last_commit():
    repo = git.Repo(search_parent_directories=True)
    head_commit = repo.head.commit
    current_commit = repo.git.rev_parse("HEAD")

    return head_commit == current_commit


def message_handler_validator(message_d: discord.message, sutom_try: SutomTry):
    # -> discord id
    sutom_try.user_id = message_d.author.id
    message = message_d.content
    # -> sutom number
    try:
        if message[7] != "#":
            return (-1, None)
        s_number = ""
        digit_in_sutom_number = 8
        while message[digit_in_sutom_number].isnumeric():
            s_number = s_number + message[digit_in_sutom_number]
            digit_in_sutom_number += 1
        sutom_try.sutom_number = s_number
        # -> number of try (result is different than n/n or -/n)
        # TODO compare char with [1,2,3,4,5,6,7,8,9,-] array
        if (
            (
                not (
                    message[1 + digit_in_sutom_number].isnumeric()
                    or message[1 + digit_in_sutom_number] == "-"
                )
            )
            or ((message[2 + digit_in_sutom_number]) != "/")
            or (not message[3 + digit_in_sutom_number].isnumeric())
        ):
            return (-1, None)
        sutom_try.number_of_try = message[1 + digit_in_sutom_number]
        sutom_try.word_len = message[3 + digit_in_sutom_number]
        # -> game time
        if (len(message.partition("\n")[0])) < 19:
            sutom_try.time_to_guess = "00:00:00"
            return (1, sutom_try)
        if message.partition("\n")[0].count("h") == 1:
            sutom_try.time_to_guess = sutom_date_formater(
                message[5 + digit_in_sutom_number : 13 + digit_in_sutom_number]
            )
        else:
            sutom_try.time_to_guess = (
                "00:" + message[5 + digit_in_sutom_number : 10 + digit_in_sutom_number]
            )
        # TODO: depending if 1h00:00 or 10h:00:00 the \n is taken
        sutom_try.time_to_guess = sutom_try.time_to_guess.strip()
        return (2, sutom_try)
    except IndexError as ie:
        print(
            f"Error in MESSAGE_HANDLER_VALIDATOR.\nMessage is {message} \nwith exception{ie}"
        )
        return (-1, None)


# TODO: replace the "h" by ":" and format with zfill(x)
def sutom_date_formater(sutom_date: str):
    formated_date = sutom_date.partition("h")[0]
    return formated_date.zfill(2) + ":" + sutom_date.partition("h")[2]


def print_status(client, SUTOM_CHANNEL, SUTOM_GUILD):
    @client.event
    async def on_ready():
        for guild in client.guilds:
            if str(guild.id) == str(SUTOM_GUILD):
                break
        gen_channel = guild.get_channel(int(SUTOM_CHANNEL))
        l = client.latency
        l = str(l).partition(".")[2]
        l = l[0:3] + "ms"
        print(l)
        await gen_channel.send(f"Online 🤖 V2.2 (C-DEL edition). {l}")
        print("Connected to : ", guild.name)


def main(argv):

    load_dotenv()

    # Argument and python call handeling

    set_mode = False
    try:
        opts, args = getopt.getopt(argv, "htr", ["test", "run"])
    except getopt.GetoptError:
        print(HELP_MSG)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print(HELP_MSG)
            sys.exit()
        elif opt in ("-t", "--test"):
            print("Test mode")
            set_mode = True
            TOKEN = os.getenv("DISCORD_TOKEN_TEST")
            SUTOM_CHANNEL = os.getenv("TEST_CHANNEL_ID")
            SUTOM_GUILD = os.getenv("TEST_GUILD_ID")
        elif opt in ("-r", "--run"):
            print("Run mode")
            set_mode = True
            TOKEN = os.getenv("DISCORD_TOKEN")
            SUTOM_CHANNEL = os.getenv("SUTOM_CHANNEL_ID")
            SUTOM_GUILD = os.getenv("MAGENOIR_GUILD_ID")

    if not set_mode:
        print(HELP_MSG)
        sys.exit(2)

    # Discord Intents setup

    intents = discord.Intents.all()
    # intents.messages = True
    # intents.message_content = True
    client = discord.Client(intents=intents)

    # Print latency and connected Server
    print_status(client, SUTOM_CHANNEL, SUTOM_GUILD)

    @client.event
    async def on_message(message):
        for guild in client.guilds:
            if str(guild.id) == str(SUTOM_GUILD):
                break

        channel_sutom = guild.get_channel(int(SUTOM_CHANNEL))

        # To avoid the bot reply to himself in an infinite loop
        if message.author == client.user:
            return

        try:
            # TODO: partion(" ")[0] in [sutom, SUTOM, ...] + if # missing, message too short (should be partition selector instead of slicing)

            # SUTOM message
            if message.content[0:6] == "#SUTOM" or message.content[0:6] == "#sutom":

                print("Sutom detected")

                sutom_try = SutomTry()

                res = message_handler_validator(message, sutom_try)
                status = res[0]
                sutom_try = res[1]

                if status == 1:
                    await channel_sutom.send(
                        f"N'oublie pas d'activer le compteur de temps dans les paramètres du jeu 👀🕜"
                    )

                if status == -1:
                    return

                sutom_try.date_of_try = str(datetime.now().date())

                print(f"|Status {status} and try {sutom_try}|")

                sutom_try.time_to_guess = timestamp_to_second(sutom_try.time_to_guess)

                status = rd.write_results(FILE_RESULTS_PATH, sutom_try)
                if status == -1:
                    await channel_sutom.send(
                        f"Hey, {message.author.mention}, t'as déjà un résultat enregistré pour aujourd'hui"
                    )

                if status == 0:
                    await channel_sutom.send(
                        f"Résultat enregistré, {message.author.mention}."
                    )

            # .takeda
            if message.content[0:7] == ".takeda":
                await channel_sutom.send(file=discord.File("takeda.png"))
                return

            # .graph
            if message.content[0:7] == ".graph":
                await rd.send_results_command(
                    (".me", "", ""), client, channel_sutom, message.author.id
                )
                await channel_sutom.send(file=discord.File("graph.png"))
                return

            # .other command
            if message.content[0] == ".":

                await rd.send_results_command(
                    message.content.partition(" "),
                    client,
                    channel_sutom,
                    message.author.id,
                )

            else:
                pass

        except IndexError as ex:
            print("----------------------------------- Main loop exception.\n")
            print(str(datetime.now()))
            print(f"Message : {message.content}\n\nException :\n")
            print(ex)
            print(ex.with_traceback)
            print("----------------------------------- end of exception log")

    client.run(TOKEN)


if __name__ == "__main__":
    main(sys.argv[1:])
