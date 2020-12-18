import random

from twitchio.ext import commands

from carberretta import Config


class Fun:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="dice", aliases=["roll"])
    async def dice_command(self, ctx: commands.bot.Context, sides: int = 6) -> None:
        if not 0 < sides < 101:
            return await ctx.send(f"{ctx.author.name}, you can only roll dice of between 1 and 100 sides inclusive.")

        await ctx.send(f"{ctx.author.name}, you rolled a {random.randint(1, sides)}.")

    @commands.command(name="coinflip", aliases=["coin", "flip"])
    async def coinflip_command(self, ctx: commands.bot.Context, bet: int, guess: str) -> None:
        bal: int = await self.bot.db.field("SELECT Credits FROM economy WHERE User = ?", ctx.author.name)
        if bet > bal:
            return await ctx.send(
                f"{ctx.author.name}, you do not have enough credits to make that bet; you only have {bal:,}."
            )

        if (guess := guess.lower()) not in ("heads", "tails", "h", "t"):
            return await ctx.send(f"{ctx.author.name}, you need to guess either 'heads' or 'tails'.")

        if guess[0] != random.choice("ht"):
            await ctx.send(f"Too bad {ctx.author.name}, you were wrong! {bet:,} credits have been added to the bank.")
            await self.bot.db.execute("UPDATE economy SET Credits = Credits - ? WHERE User = ?", bet, ctx.author.name)
            return await self.bot.db.execute("UPDATE economy SET Credits = Credits + ? WHERE User = 'bank'", bet)

        await ctx.send(f"Congratulations {ctx.author.name}, you were right! You've won {bet*2:,} credits!")
        await self.bot.db.execute("UPDATE economy SET Credits = Credits + ? WHERE User = ?", bet, ctx.author.name)


def prepare(bot: commands.Bot) -> None:
    bot.add_cog(Fun(bot))
