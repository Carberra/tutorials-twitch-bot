from twitchio.ext import commands


class Help:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx: commands.bot.Context) -> None:
        await ctx.send(
            "Commands: {}".format(
                " • ".join(
                    "|".join([cmd.name, *(cmd.aliases or [])])
                    for cmd in self.bot.commands.values()
                )
            )
        )


def prepare(bot: commands.Bot) -> None:
    bot.add_cog(Help(bot))
