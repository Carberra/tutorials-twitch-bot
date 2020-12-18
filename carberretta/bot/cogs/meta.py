import datetime as dt

from twitchio.ext import commands


class Meta:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="uptime")
    async def uptime_command(self, ctx: commands.bot.Context) -> None:
        data = await ctx.get_stream()

        if data is None:
            return await ctx.send("This channel is not currently live.")

        uptime = dt.datetime.utcnow() - dt.datetime.fromisoformat(data["started_at"][:-1])
        await ctx.send(f"{uptime}")


def prepare(bot: commands.Bot) -> None:
    bot.add_cog(Meta(bot))
