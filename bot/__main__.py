import discord
import os
from discord.ext import commands
import asyncio
import logging
from dotenv import load_dotenv
load_dotenv()


log = logging.getLogger(__name__)

extensions = (
    'bot.core',
    'bot.novelimage'

)
class MissingConfigurationException(Exception):
    pass

def assert_envs_exist():
    envs = (
        ('TOKEN', 'The Bot Token', str),
        ('NAI_USERNAME', 'Your login for NovelAPI. This must be lowercase email or exactly how you registered as.', str),
        ('NAI_PASSWORD', 'Your Novel API Password', str),


    )

    for e in envs:
        ident = f"{e[0]}/{e[1]}"
        value = os.environ.get(e[0])
        if value is None:
            raise MissingConfigurationException(f"{ident} needs to be defined")
        try:
            _ = e[2](value)
        except ValueError:
            raise MissingConfigurationException(f"{ident} is not the required type of {e[2]}")


def bot_task_callback(future: asyncio.Future):
    if future.exception():
        raise future.exception()


async def run_bot():
    assert_envs_exist()
    token = os.environ['TOKEN']
    intents = discord.Intents.all()
    intents.message_content = True
    intents.members = True
    bot = commands.Bot(
        intents=intents,
        command_prefix='!',
        slash_commands=True,
    )
    try:
        for ext in extensions:
            await bot.load_extension(ext)
            log.debug(f"Extension {ext} loaded")

        await bot.start(token)
    finally:
        await bot.close()

loop = asyncio.new_event_loop()
try:
    future = asyncio.ensure_future(
        run_bot(),
        loop=loop
    )
    future.add_done_callback(bot_task_callback)
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.close()
