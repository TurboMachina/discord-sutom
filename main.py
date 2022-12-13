import os, sys
import discord
from dotenv import load_dotenv
from datetime import datetime

from SutomTry import SutomTry, FILE_RESULTS_PATH
import results_handler as rd



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

def message_handler_validator(message_d: discord.message, sutom_try: SutomTry):
    # -> discord id
    sutom_try.user_id = message_d.author.id
    message = message_d.content
    # -> sutom number
    try:
        if (message[7] != '#'):
            return (-1, None)
        s_number = ""
        digit_in_sutom_number = 8
        while (message[digit_in_sutom_number].isnumeric()):
            s_number = s_number + message[digit_in_sutom_number]
            digit_in_sutom_number += 1
        sutom_try.sutom_number = s_number
        # -> number of try (result is different than n/n or -/n)
        # TODO compare char with [1,2,3,4,5,6,7,8,9,-] array
        if ((not (message[1 + digit_in_sutom_number].isnumeric() or message[1 + digit_in_sutom_number] == '-')) or
            ((message[2 + digit_in_sutom_number]) != '/') or 
            (not message[3 + digit_in_sutom_number].isnumeric())):
            return (-1, None)
        sutom_try.number_of_try = message[1 + digit_in_sutom_number]
        sutom_try.word_len = message[3 + digit_in_sutom_number]
        # -> game time
        if (len(message.partition("\n")[0])) < 19:
            return (1, sutom_try)
        if (message.partition("\n")[0].count('h') == 1):
            sutom_try.time_to_guess = sutom_date_formater(message[5 + digit_in_sutom_number:13 + digit_in_sutom_number])
        else:
            sutom_try.time_to_guess = "00:" + message[5 + digit_in_sutom_number:10 + digit_in_sutom_number]
        # TODO: depending if 1h00:00 or 10h:00:00 the \n is taken
        sutom_try.time_to_guess = sutom_try.time_to_guess.strip()
        return (2, sutom_try)
    except IndexError as ie:
        print(f"Error in MESSAGE_HANDLER_VALIDATOR.\nMessage is {message} \nwith exception{ie}")
        return (-1, None)
    
# TODO: replace the "h" by ":" and format with zfill(x)
def sutom_date_formater(sutom_date: str):
    formated_date = sutom_date.partition("h")[0]
    return (formated_date.zfill(2)+":"+sutom_date.partition("h")[2])

def test_bot_connection(client):
    SUTOM_CHANNEL = os.getenv('SUTOM_CHANNEL_ID')
    SUTOM_GUILD = os.getenv('MAGENOIR_GUILD_ID')
    @client.event
    async def on_ready():
        for guild in client.guilds:
            if str(guild.id) == str(SUTOM_GUILD):
                print("BREAKING")
                break
        gen_channel = guild.get_channel(int(SUTOM_CHANNEL))
        l = client.latency
        print(l)
        l = str(l).partition(".")[2]
        l = l[0:3] + "ms" 
        #await gen_channel.send(f"ONLINE, ping {l}")
        #await gen_channel.send(" 🟥🟥🟥🟥🟥🟥 SUTOM BOT IS UP 🤖 ")

def main():
    
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    intents = discord.Intents.all()
    #intents.messages = True
    #intents.message_content = True
    client = discord.Client(intents=intents)

    SUTOM_CHANNEL = os.getenv('SUTOM_CHANNEL_ID')
    SUTOM_GUILD = os.getenv('MAGENOIR_GUILD_ID')

    test_bot_connection(client)

    @client.event
    async def on_message(message):
        for guild in client.guilds:
            if str(guild.id) == str(SUTOM_GUILD):
                break
        channel_sutom = guild.get_channel(int(SUTOM_CHANNEL))
        if (message.author == client.user):
            return
        try:
            if (message.content[0:6] == "#SUTOM"):
                print("Sutom detected")
                sutom_try = SutomTry()
                res = message_handler_validator(message, sutom_try)
                status = res[0]
                sutom_try = res[1]
                if status == -1:
                    return
                sutom_try.date_of_try = str(datetime.now().date())
                print(f"|Status {status} and try {sutom_try}|")
                status = rd.write_results(FILE_RESULTS_PATH, sutom_try)
                if status == -1:
                    await channel_sutom.send(f"Hey, {message.author.mention}, t'as déjà un résultat enregistré pour aujourd'hui")
            if (message.content[0] == '.'):
                response = rd.send_results_command(message.content.partition(" ")[0])
                await channel_sutom.send(response)
            else:
                pass
        except IndexError as ex:
            print(ex.with_traceback)
    
    client.run(TOKEN)


if __name__ == "__main__":
    main()