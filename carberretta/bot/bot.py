import sys
import typing as t
from pathlib import Path

import twitchio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc
from twitchio.ext import commands

from carberretta import Config
from carberretta.db import Database


class Bot(commands.Bot):
    def __init__(self) -> None:
        self._cogs: t.List[str] = [
            p.stem for p in Path(".").glob("./carberretta/bot/cogs/*.py")
        ]
        self.scheduler = AsyncIOScheduler()
        self.scheduler.configure(timezone=utc)
        self.db = Database(self)

        super().__init__(
            irc_token=Config.IRC_TOKEN,
            api_token=Config.API_TOKEN,
            client_id=Config.CLIENT_ID,
            client_secret=Config.CLIENT_SECRET,
            prefix=Config.PREFIX,
            nick=Config.NICK,
            initial_channels=Config.INITIAL_CHANNELS,
        )

    def setup(self) -> None:
        print("Running setup...")

        for cog in self._cogs:
            self.load_module(f"carberretta.bot.cogs.{cog}")
            print(f" Loaded `{cog}` cog.")

        print("Setup complete.")

    def run(self) -> None:
        self.setup()

        print("Running bot...")
        super().run()

    async def event_ready(self) -> None:
        await self.db.connect()
        print(" Connected to database.")

        self.scheduler.start()
        print(
            f" Scheduler started ({len(self.scheduler.get_jobs()):,} job(s))."
        )

        self.channel: twitchio.Channel = self.get_channel(
            next(iter(self.initial_channels))
        )
        await self.channel.send(f"{Config.NICK} is now online!")
        print("Bot ready. Do NOT use CTRL+C to shut the bot down!")

    @commands.command(name="shutdown")
    async def shutdown_command(self, ctx: commands.bot.Context) -> None:
        if ctx.author.name != next(iter(self.initial_channels)):
            return await ctx.send("You cannot shut the bot down.")

        await self.channel.send(f"{Config.NICK} is now shutting down.")
        self.scheduler.shutdown()
        await self.db.close()
        sys.exit(0)

    async def on_error(self, error, data=None) -> None:
        raise

    async def event_command_error(
        self, ctx: commands.bot.Context, exc: twitchio.ClientError
    ) -> None:
        if isinstance(exc, commands.CommandNotFound):
            return await ctx.send(
                f"That is not a registered command. "
                "Type {Config.PREFIX}help for a list."
            )

        if isinstance(exc, commands.MissingRequiredArgument):
            return await ctx.send(
                f"No `{exc.param.name}` argument was passed, "
                "despite being required."
            )

        if isinstance(exc, commands.BadArgument):
            return await ctx.send("One or more arguments are invalid.")

        raise

    async def handle_commands(self, message: twitchio.Message) -> None:
        elem = message.content.split(maxsplit=1)
        message.content = f"{elem[0].lower()} {' '.join(elem[1:])}"
        await super().handle_commands(message)

    async def event_message(self, message: twitchio.Message) -> None:
        if message.author.name in (Config.NICK, "restreambot"):
            return

        await self.handle_commands(message)

    def get_user(self, name: str) -> t.Optional[twitchio.User]:
        for user in self.channel.chatters:
            if name == user.name:
                return user
        return None
