import os, sys
import discord
from dotenv import load_dotenv
from datetime import datetime

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


def main():
    
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    client = discord.Client(intents=discord.Intents.default())

    SUTOM_CHANNEL = os.getenv('SUTOM_CHANNEL_ID')
    SUTOM_GUILD = os.getenv('SUTOM_GUILD_ID')

    #test_bot_connection(client)

    

    client.run(TOKEN)


if __name__ == "__main__":
    main()