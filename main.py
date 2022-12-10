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
    def __init__(self, user_id, sutom_number, number_of_try, word_len, date_of_try, time_of_try, time_to_guess = '00:00:00'):
        self.user_id = user_id
        self.sutom_number = sutom_number
        self.number_of_try = number_of_try
        self.word_len = word_len
        self.time_to_guess = time_to_guess
        self.date_of_try = date_of_try
        self.time_of_try = time_of_try


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

def handle_sutom_message(sutom_message: discord.message):
    # Parse the message
    sutom_try = SutomTry()
    


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

    @client.event
    async def on_message(message):
        if (message.author == client.user):
            return
        if (message.content[0:6] == "#SUTOM"):
            handle_sutom_message(message)


    client.run(TOKEN)


if __name__ == "__main__":
    main()