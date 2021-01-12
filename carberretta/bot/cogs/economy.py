import asyncio
import datetime as dt
import random
import typing as t

import twitchio
from twitchio.ext import commands

from carberretta import Config


class Economy:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def process_credits(self, message: twitchio.Message) -> None:
        modified: int = await self.bot.db.execute(
            "INSERT INTO economy (User) VALUES (?) ON CONFLICT DO NOTHING",
            message.author.name,
        )
        if modified:
            await message.channel.send(
                f"Welcome to the channel {message.author.name}! I hope you enjoy your time here!"
            )

        lock: str = await self.bot.db.field("SELECT Lock FROM economy WHERE User = ?", message.author.name)
        if dt.datetime.utcnow() > dt.datetime.fromisoformat(lock):
            await self.bot.db.execute(
                "UPDATE economy SET Credits = Credits + ?, Lock = datetime('now', '+60 seconds') WHERE User = ?",
                random.randint(5, 20),
                message.author.name,
            )

    async def event_message(self, message: twitchio.Message) -> None:
        if message.author.name in (Config.NICK, "restreambot"):
            return

        await self.process_credits(message)

    @commands.command(name="credits", aliases=["economy", "money", "balance", "bal"])
    async def credits_command(self, ctx: commands.bot.Context, target: str = "") -> None:
        await asyncio.sleep(0.25)  # Delay to ensure accuracy.

        target = target.strip("@").lower() or ctx.author.name
        bal: t.Optional[int] = await self.bot.db.field("SELECT Credits FROM economy WHERE User = ?", target)

        if bal is None:
            return await ctx.send(f"{ctx.author.name}, that user is not in the database.")

        if target == ctx.author.name:
            await ctx.send(f"{target}, you have {bal:,} credit(s).")
        else:
            await ctx.send(f"{target} has {bal:,} credit(s).")

    @commands.command(name="leaderboard", aliases=["lb"])
    async def leaderboard_command(self, ctx: commands.bot.Context) -> None:
        await asyncio.sleep(0.25)  # Delay to ensure accuracy.
        table: t.List[t.Tuple[str, int]] = await self.bot.db.records(
            "SELECT User, Credits FROM economy WHERE User != 'bank' ORDER BY Credits DESC LIMIT 10"
        )
        await ctx.send("Displaying top 10: " + " • ".join(f"{user}: {bal}" for user, bal in table))

    @commands.command(name="give")
    async def give_command(self, ctx: commands.bot.Context, amount: int, target: str) -> None:
        target = target.strip("@").lower()

        if amount < 1:
            return await ctx.send(f"{ctx.author.name}, you must give at least 1 credit.")

        if amount > await self.bot.db.field("SELECT Credits FROM economy WHERE User = ?", ctx.author.name):
            return await ctx.send(f"{ctx.author.name}, you do not have the credits to give.")

        if await self.bot.db.field("SELECT Credits FROM economy WHERE User = ?", target) is None:
            return await ctx.send(f"{ctx.author.name}, that user is not in the database.")

        await self.bot.db.execute("UPDATE economy SET Credits = Credits + ? WHERE User = ?", amount, target)
        await self.bot.db.execute(
            "UPDATE economy SET Credits = Credits - ? WHERE User = ?",
            amount,
            ctx.author.name,
        )
        await ctx.send(f"{ctx.author.name} gave {amount:,} credit(s) to {target}!")

    @commands.command(name="bank")
    async def bank_command(self, ctx: commands.bot.Context) -> None:
        bal: int = await self.bot.db.field("SELECT Credits FROM economy WHERE User = 'bank'")
        await ctx.send(f"There are currently {bal:,} credit(s) in the bank.")


def prepare(bot: commands.Bot) -> None:
    bot.add_cog(Economy(bot))
