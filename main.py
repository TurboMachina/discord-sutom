import os, sys
import discord
from dotenv import load_dotenv
from datetime import datetime

from SutomTry import SutomTry
import results_handler as rd

FILE_RESULTS_PATH = "results.json"

# Example of fetched message : 
""" 
#SUTOM #999 4/6 13:37

🟥🟦🟡🟡🟡🟦🟡
🟥🟥🟦🟡🟡🟡🟦
🟥🟥🟡🟡🟡🟦🟡
🟥🟥🟥🟥🟥🟥🟥

https://sutom.nocle.fr
"""

def message_handler_validator(message: discord.message, sutom_try: SutomTry) -> int:
    # -> discord id
    sutom_try.user_id = message.author.id
    message = message.content
    # -> sutom number
    if (message[7] != '#'):
        return -1
    s_number = ""
    digit_in_sutom_number = 8
    while (message[digit_in_sutom_number].isnumeric()):
        s_number = s_number + message[digit_in_sutom_number]
        digit_in_sutom_number += 1
    sutom_try.number_of_try = s_number
    # -> number of try (result is different than n/n or -/n)
    # TODO compare char with [1,2,3,4,5,6,7,8,9,-] array
    if ((not message[1 + digit_in_sutom_number].isnumeric() or message[1 + digit_in_sutom_number] != '-') or
        ((message[2 + digit_in_sutom_number]) != '/') or 
        (not message[3 + digit_in_sutom_number].isnumeric())):
        return -1
    sutom_try.number_of_try = message[1 + digit_in_sutom_number]
    sutom_try.word_len = message[3 + digit_in_sutom_number]
    # -> game time
    if (print(len(message.partition("\n")[0])) < 19):
        return 1
    if (message.partition("\n")[0].count(':') == 1):
        sutom_try.time_to_guess = message[5 + digit_in_sutom_number:10 + digit_in_sutom_number]
    else:
        sutom_try.time_to_guess = sutom_date_formater(message[5 + digit_in_sutom_number:13 + digit_in_sutom_number])
    return 2
    
# TODO: replace the "h" by ":" and format with zfill(x)
def sutom_date_formater(sutom_date: str):
    formated_date = sutom_date.partition("h")[0]
    return (formated_date.zfill(2)+":"+sutom_date.partition("h")[2])

def test_bot_connection(client):
    TEST_CHANNEL = os.getenv('TEST_CHANNEL_ID')
    TEST_GUILD = os.getenv('TEST_GUILD_ID')
    @client.event
    async def on_ready():
        for guild in client.guilds:
            if guild.name == TEST_GUILD:
                break

        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )
        gen_channel = guild.get_channel(int(TEST_CHANNEL))
        await gen_channel.send("TEST_PASSED_{}".format(datetime.now()))
    @client.event
    async def on_message(message):
        if (message.author == client.user):
            return
        if (message.content[0:6] == "#SUTOM"):
            print("DETECTED")

def main():
    
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    intents = discord.Intents.all()
    #intents.messages = True
    #intents.message_content = True
    client = discord.Client(intents=intents)

    SUTOM_CHANNEL = os.getenv('TEST_CHANNEL_ID')
    SUTOM_GUILD = os.getenv('TEST_GUILD_ID')

    #test_bot_connection(client)

    sutom_try = SutomTry()

    client.commands.Bot(command_prefix="$")

    @client.event
    async def on_message(message):
        for guild in client.guilds:
            if guild.name == SUTOM_GUILD:
                break
        channel_sutom = guild.get_channel(int(SUTOM_CHANNEL))
        if (message.author == client.user):
            return
        if (message.content[0:6] == "#SUTOM"):
            message_handler_validator(message, sutom_try)
            sutom_try.date_of_try = str(datetime.now().date())
            status = rd.write_results(FILE_RESULTS_PATH, sutom_try)
            if status == -1:
                await channel_sutom.send(f"Hey, {message.author.mention}, t'as déjà un résultat enregistré pour aujourd'hui")
        else:
            await channel_sutom.send("He's ready")
    client.run(TOKEN)


if __name__ == "__main__":
    main()