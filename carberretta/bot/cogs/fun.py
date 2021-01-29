import asyncio
import datetime as dt
import random
import typing as t
from enum import Enum

from twitchio.ext import commands

from carberretta import Config

HACK_COST = 100


class GameState(Enum):
    __slots__ = ("STOPPED", "WAITING", "RUNNING")

    STOPPED = 0
    WAITING = 1
    RUNNING = 2


class HackGame:
    __slots__ = ("state", "bot", "participants")

    def __init__(self, bot: commands.Bot) -> None:
        self.state = GameState.STOPPED
        self.bot = bot
        self.participants: t.List[str] = []

    async def start(self, ctx: commands.bot.Context) -> None:
        self.state = GameState.WAITING
        await ctx.send(f"A hacking squad is being set up; use {Config.PREFIX}hack to join!")
        self.bot.scheduler.add_job(
            self.run,
            next_run_time=dt.datetime.utcnow() + dt.timedelta(seconds=60),
            args=[ctx],
        )

    async def run(self, ctx: commands.bot.Context) -> None:
        if len(self.participants) < 3:
            await self.bot.db.executemany(
                "UPDATE economy SET Credits = Credits + ? WHERE User = ?",
                ((HACK_COST, p) for p in self.participants),
            )
            await ctx.send(
                "The hack was cancelled as not enough users joined the squad. Those users that did have been refunded."
            )
            return await self.reset()

        self.state = GameState.RUNNING
        pool = await self.bot.db.field("SELECT Credits FROM economy WHERE User = 'bank'")
        await ctx.send(
            f"The hack has started! The total up for grabs is {pool:,} credits. Who will show their elite hacking skills and get the goods?"
        )
        await asyncio.sleep(random.randint(10, 30))

        winners: t.List[str] = []
        odds = min(len(self.participants) * 10, 75)
        for user in self.participants:
            if random.randint(1, 100) <= odds:
                winners.append(user)

        await self.bot.db.execute("UPDATE economy SET Credits = Credits - ? WHERE User = 'bank'", pool)

        if not winners:
            return await ctx.send("The hack is complete; nobody managed to get anything!")

        winnings = pool // len(self.participants)
        await self.bot.db.executemany(
            "UPDATE economy SET Credits = Credits + ? WHERE User = ?",
            ((winnings, w) for w in winners),
        )
        await ctx.send(
            f"The hack is complete! The following users got their {winnings:,} credit share: {', '.join(winners)}"
        )
        await self.reset()

    async def reset(self) -> None:
        self.state = GameState.STOPPED
        self.participants = []

    async def try_add_participant(self, ctx: commands.bot.Context) -> None:
        if ctx.author.name in self.participants:
            return await ctx.send(f"{ctx.author.name}, you are already good to go.")

        bal: int = await self.bot.db.field("SELECT Credits FROM economy WHERE User = ?", ctx.author.name)
        if bal < 100:
            return await ctx.send(
                f"{ctx.author.name}, you need at least {HACK_COST:,} credits to hack; you have {bal:,}."
            )

        await self.bot.db.execute(
            "UPDATE economy SET Credits = Credits - ? WHERE User = ?",
            HACK_COST,
            ctx.author.name,
        )
        self.participants.append(ctx.author.name)
        await ctx.send(
            f"Welcome to the squad {ctx.author.name}! The {HACK_COST:,} credits needed for the hacking equipment has been taken from your balance."
        )


class Fun:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.hackgame = HackGame(bot)

    @commands.command(name="dice", aliases=["roll"])
    async def dice_command(self, ctx: commands.bot.Context, sides: int = 6) -> None:
        if not 0 < sides < 101:
            return await ctx.send(f"{ctx.author.name}, you can only roll dice of between 1 and 100 sides inclusive.")

        await ctx.send(f"{ctx.author.name}, you rolled a {random.randint(1, sides)}.")

    @commands.command(name="coinflip", aliases=["coin", "flip"])
    async def coinflip_command(self, ctx: commands.bot.Context, bet: int, guess: str) -> None:
        bal: int = await self.bot.db.field("SELECT Credits FROM economy WHERE User = ?", ctx.author.name)

        if bet < 1:
            return await ctx.send(f"{ctx.author.name}, you must bet at least 1 credit.")

        if bet > bal:
            return await ctx.send(
                f"{ctx.author.name}, you do not have enough credits to make that bet; you only have {bal:,}."
            )

        if (guess := guess.lower()) not in ("heads", "tails", "h", "t"):
            return await ctx.send(f"{ctx.author.name}, you need to guess either 'heads' or 'tails'.")

        if guess[0] != random.choice("ht"):
            await ctx.send(f"Too bad {ctx.author.name}, you were wrong! {bet:,} credits have been added to the bank.")
            await self.bot.db.execute(
                "UPDATE economy SET Credits = Credits - ? WHERE User = ?",
                bet,
                ctx.author.name,
            )
            return await self.bot.db.execute("UPDATE economy SET Credits = Credits + ? WHERE User = 'bank'", bet)

        await ctx.send(f"Congratulations {ctx.author.name}, you were right! You've won {bet*2:,} credits!")
        await self.bot.db.execute(
            "UPDATE economy SET Credits = Credits + ? WHERE User = ?",
            bet,
            ctx.author.name,
        )

    @commands.command(name="hack")
    async def hack_command(self, ctx: commands.bot.Context) -> None:
        if self.hackgame.state == GameState.RUNNING:
            return await ctx.send(f"{ctx.author.name}, a hack is already in progress!")

        if self.hackgame.state == GameState.WAITING:
            return await self.hackgame.try_add_participant(ctx)

        if self.hackgame.state == GameState.STOPPED:
            if await self.bot.db.field("SELECT Credits FROM economy WHERE User = 'bank'") < 500:
                return await ctx.send("The bank does not have enough credits to be worth hacking.")

            await self.hackgame.start(ctx)
            await self.hackgame.try_add_participant(ctx)


def prepare(bot: commands.Bot) -> None:
    bot.add_cog(Fun(bot))
