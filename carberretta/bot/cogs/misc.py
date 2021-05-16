from twitchio.ext import commands


class Misc:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="shoutout", aliases=["so"])
    async def shoutout_command(self, ctx: commands.bot.Context, channel: str) -> None:
        if ctx.author.name != next(iter(self.bot.initial_channels)):
            return await ctx.send("You cannot shout out other channels.")

        channel = channel.strip("@").lower()
        await ctx.send(
            f"Check out {channel}'{'' if channel.endswith('s') else 's'} channel: https://twitch.tv/{channel}"
        )


def prepare(bot: commands.Bot) -> None:
    bot.add_cog(Misc(bot))
