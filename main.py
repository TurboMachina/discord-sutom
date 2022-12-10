import os, sys
import discord
from dotenv import load_dotenv
from datetime import datetime

import results_handler as rd


# Example of fetched message : 
""" 
#SUTOM #999 4/6 13:37

🟥🟦🟡🟡🟡🟦🟡
🟥🟥🟦🟡🟡🟡🟦
🟥🟥🟡🟡🟡🟦🟡
🟥🟥🟥🟥🟥🟥🟥

https://sutom.nocle.fr
"""

class SutomTry:
    def __init__(self, user_id, sutom_number, number_of_try, word_len, date_of_try, time_to_guess = '00:00:00'):
        self.user_id = user_id
        self.sutom_number = sutom_number
        self.number_of_try = number_of_try
        self.word_len = word_len
        self.time_to_guess = time_to_guess
        self.date_of_try = date_of_try

        """
         Return : 
         - -1 : NOK
         -  1 : OK, No timestamp
         -  2 : OK, +  timestamp
        """
def message_handler_validator(message: discord.message, sutom_try: SutomTry) -> int:
    # -> discord id
    sutom_try.user_id = message.author.id
    message = message.content
    # -> sutom number
    # TODO condition != # and delete the else 
    if (message[7] == '#'):
        s_number = ""
        digit_in_sutom_number = 8
        while (message[digit_in_sutom_number].isnumeric()):
            s_number = s_number + message[digit_in_sutom_number]
            digit_in_sutom_number += 1
        sutom_try = s_number
    else:
        return -1
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
        sutom_try.time_to_guess = message[5 + digit_in_sutom_number:13 + digit_in_sutom_number]
    return 2
    

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

    SUTOM_CHANNEL = os.getenv('SUTOM_CHANNEL_ID')
    SUTOM_GUILD = os.getenv('SUTOM_GUILD_ID')

    #test_bot_connection(client)

    sutom_try = SutomTry()

    @client.event
    async def on_message(message):
        if (message.author == client.user):
            return
        if (message.content[0:6] == "#SUTOM"):
            message_handler_validator(message, sutom_try)
            sutom_try.date_of_try = str(datetime.now().date())
        


    client.run(TOKEN)


if __name__ == "__main__":
    main()