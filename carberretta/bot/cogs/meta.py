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

    @commands.command(name="source")
    async def source_command(self, ctx: commands.bot.Context) -> None:
        await ctx.send("https://github.com/Carberra/tutorials-twitch-bot")

    @commands.command(name="youtube")
    async def youtube_command(self, ctx: commands.bot.Context) -> None:
        await ctx.send("https://youtube.carberra.xyz")

    @commands.command(name="discord")
    async def discord_command(self, ctx: commands.bot.Context) -> None:
        await ctx.send("https://discord.carberra.xyz")

    @commands.command(name="twitter")
    async def twitter_command(self, ctx: commands.bot.Context) -> None:
        await ctx.send("https://twitter.carberra.xyz")

    @commands.command(name="patreon")
    async def patreon_command(self, ctx: commands.bot.Context) -> None:
        await ctx.send("https://patreon.carberra.xyz")
        
    @commands.command(name="plans", aliases=["plan"])
    async def plans_command(self, ctx: commands.bot.Context) -> None:
        await ctx.send("https://plans.carberra.xyz")
        
    @commands.command(name="facebook")
    async def facebook_command(self, ctx: commands.bot.Context) -> None:
        await ctx.send("https://facebook.carberra.xyz")
        
    @commands.command(name="lbry", aliases=["odysee"])
    async def lbry_command(self, ctx: commands.bot.Context) -> None:
        await ctx.send("https://lbry.carberra.xyz")
    
    @commands.command(name="donate", aliases=["tip"])
    async def donate_command(self, ctx: commands.bot.Context) -> None:
        await ctx.send("https://tip.carberra.xyz")
        
    @commands.command(name="docs")
    async def docs_command(self, ctx: commands.bot.Context) -> None:
        await ctx.send("https://docs.carberra.xyz")
  
def prepare(bot: commands.Bot) -> None:
    bot.add_cog(Meta(bot))
