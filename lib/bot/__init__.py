from asyncio import sleep
from datetime import datetime
from glob import glob

from ..db import db
import discord
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import *
from discord import Embed, File, Intents
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


# intents = discord.Intents.default()
# intents.members = True
# intents.presences = True

PREFIX = "!"
OWNER_IDS = [261133484209340417]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]

class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog ready")

    def all_ready(self):
        return all([getattr(self,cog) for cog in COGS])

class Bot(BotBase):
    def __init__(self):
        self.prefix=PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        self.scheduler=AsyncIOScheduler()

        db.autosave(self.scheduler)

        super().__init__(command_prefix=PREFIX, 
                         owner_ids=OWNER_IDS,
                         intents=Intents.all())

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} cog loaded")

        print("setup complete")

    def run(self, version):
        self.VERSION = version

        print("running setup...")
        self.setup()

        with open("./lib/bot/token2.0", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("Running Bot...")
        super().run(self.TOKEN, reconnect=True)

    async def print_message(self):
        await self.stdout.send("I am a timed notification!")

    async def on_connect(self):
        print("Bot Connected")

    async def on_disconnect(self):
        print("Bot Disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong.")

        raise 

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, NotOwner):
            pass

        elif isinstance(exc, BadArgument):
            pass

        elif isinstance(exc, CommandOnCooldown):
            pass

        elif hasattr(exc, "original"):
            raise exc.original

        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.scheduler.start()
            self.stdout = self.get_channel(963948681713827891)

            # embed = Embed(title="Now Online", description="Bedby is now online", 
            #               colour=0x00FF00, timestamp=datetime.utcnow())
            # fields = [("Name", "Value", True),
            #           ("Another field", "This field is next", True),
            #           ("Third tuple of fields", "This will be non-inline", False)]
            # for name, value, inline in fields:
            #     embed.add_field(name=name, value=value, inline=inline)
            # embed.set_author(name="Bluepengie")
            # embed.set_footer(text="This is a footer")
            # await channel.send(embed=embed)

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True
            print("bot ready")

            meta = self.get_cog("Meta")
            await meta.set()
        else:
            print("bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

bot = Bot()
