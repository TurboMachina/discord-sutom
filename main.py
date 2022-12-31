import os, sys, getopt
import discord
from dotenv import load_dotenv
from datetime import datetime
import git

from SutomRecord import SutomRecord, FILE_RESULTS_PATH
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


def timestamp_to_second(timestamp: str) -> int:
    h = int(timestamp.partition(":")[0])
    m = int(timestamp.partition(":")[2].partition(":")[0])
    s = int(timestamp.partition(":")[2].partition(":")[2])
    seconds = (3600 * h) + (60 * m) + s
    return seconds


# TODO : use this
def print_if_last_commit():
    repo = git.Repo(search_parent_directories=True, path=".")
    github_head_commit = repo.head.commit
    current_commit = repo.git.rev_parse("HEAD")
    print("Last commit: " + str(github_head_commit))
    print("Current commit: " + str(current_commit))
    # display if the current commit is the last one
    print("Is last commit: " + str(github_head_commit == current_commit))


def sutom_message_validator(message, author, sutom_record: SutomRecord):
    # -> discord id
    sutom_record.user_id = author
    sutom_record.date_of_try = str(datetime.now().date())

    try:
        if message[7] != "#":
            return (-1, None)

        # -> sutom number
        s_number = ""
        digit_in_sutom_number = 8

        while message[digit_in_sutom_number].isnumeric():
            s_number = s_number + message[digit_in_sutom_number]
            digit_in_sutom_number += 1
        sutom_record.sutom_number = s_number

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

        # -> number of try
        sutom_record.number_of_try = message[1 + digit_in_sutom_number]

        # -> game time
        # --> no time in message
        if not message.contains(":"):
            sutom_record.time_to_guess = 0
            return (1, sutom_record)

        # --> time in message with hour (1h00:00 or 10h:00:00)
        if message.partition("\n")[0].count("h") == 1:
            tmp_str_time_to_guess = sutom_date_formater(
                message[5 + digit_in_sutom_number : 13 + digit_in_sutom_number]
            )
        else:
            # --> time in message without hour (00:00)
            tmp_str_time_to_guess = (
                "00:" + message[5 + digit_in_sutom_number : 10 + digit_in_sutom_number]
            )
        # Strip: depending if 1h00:00 or 10h:00:00 the \n is taken
        sutom_record.time_to_guess = timestamp_to_second(tmp_str_time_to_guess.strip())
        return (2, sutom_record)
    except IndexError as ie:
        print(
            f"Error in sutom_message_validator.\nMessage is {message} \nwith exception{ie}"
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
        channel_sutom = guild.get_channel(int(SUTOM_CHANNEL))
        if channel_sutom is None:
            print(
                "Error while getting the Sutom channel. Please check the channel ID in the .env file. You can copy a channel's ID by enabeling the dev mode in discord and right\
            clicking on the channel."
            )
            sys.exit(2)
        l = client.latency
        l = str(l).partition(".")[2]
        l = l[0:3] + "ms"
        print(l)
        await channel_sutom.send(f"Online 🤖 . {l}")
        print(f"Ready. Connected to : {guild.name} in {l}")


def main(argv):

    load_dotenv()
    TOKEN, SUTOM_CHANNEL, SUTOM_GUILD = None, None, None
    client = None

    # Argument and python call handeling

    set_mode = False
    debug_mode = False
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
            debug_mode = True
            TOKEN = os.getenv("DISCORD_TOKEN_TEST")
            SUTOM_CHANNEL = os.getenv("TEST_CHANNEL_ID")
            SUTOM_GUILD = os.getenv("TEST_GUILD_ID")
        elif opt in ("-r", "--run"):
            print("Run mode")
            set_mode = True
            TOKEN = os.getenv("DISCORD_TOKEN")
            SUTOM_CHANNEL = os.getenv("SUTOM_CHANNEL_ID")
            SUTOM_GUILD = os.getenv("MAGENOIR_GUILD_ID")

    if TOKEN is None or SUTOM_CHANNEL is None or SUTOM_GUILD is None:
        print("Environment variables not set. Please check .env-example file.")
        sys.exit(2)

    if not set_mode:
        print(HELP_MSG)
        sys.exit()

    # Discord Intents setup
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)
    if client is None or client.guilds is None:
        print(
            "Error while creating discord.Client. Enable trace with discord.Client(intents=intents, enable_debug_events=True)"
        )
        sys.exit(2)

    # Print latency and connected Server
    if debug_mode:
        print_status(client, SUTOM_CHANNEL, SUTOM_GUILD)

    @client.event
    async def on_message(message):
        for guild in client.guilds:
            if str(guild.id) == str(SUTOM_GUILD):
                break

        channel_sutom = guild.get_channel(int(SUTOM_CHANNEL))
        if channel_sutom is None:
            print(
                "Error while getting the Sutom channel. Please check the channel ID in the .env file. You can copy a channel's ID by enabeling the dev mode in discord and right\
            clicking on the channel."
            )
            sys.exit(2)

        # To avoid the bot replying to himself in an infinite loop
        if message.author == client.user:
            return

        try:
            # TODO: partion(" ")[0] in [sutom, SUTOM, ...] + if # missing, message too short (should be partition selector instead of slicing)
            # SUTOM message
            if message.content[0:6] == "#SUTOM" or message.content[0:6] == "#sutom":

                print(
                    f"Sutom message detected from {str(message.author.display_name)} at {str(datetime.now())}"
                )

                sutom_record = SutomRecord()

                res = sutom_message_validator(
                    message.author.id, message.content, sutom_record
                )
                status = res[0]
                sutom_record = res[1]

                if status == 1:
                    await channel_sutom.send(
                        "N'oublie pas d'activer le compteur de temps dans les paramètres du jeu 👀🕜"
                    )

                if status == -1:
                    await channel_sutom.send(
                        "#SUTOM message mal formé! Template : #SUTOM #999 X/6 (1h13m37s)"
                    )
                    sys.exit(2)

                print(
                    f"Status {status} and try {sutom_record} from {message.author.display_name}"
                )

                status = rd.write_results(FILE_RESULTS_PATH, sutom_record)
                if status == -1:
                    await channel_sutom.send(
                        f"Hey, {message.author.mention}, t'as déjà un résultat enregistré pour aujourd'hui"
                    )

                if status == 0:
                    await channel_sutom.send(
                        f"Résultat enregistré, {message.author.mention}."
                    )

            # .command
            if message.content[0] == ".":
                await rd.send_results_command(
                    # Envoie un tuple dans un str -> Exception deballage tuple
                    # message.content.partition(" "),
                    message.content.partition(" ")[0],
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
