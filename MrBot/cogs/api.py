from discord.ext import commands
from .utils import formatting
import discord


class Api(commands.Cog):
    """
    Image manipulation commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="osu", invoke_without_command=True)
    async def osu(self, ctx):
        return await ctx.send("Please choose a valid subcommand.")

    @osu.command(name="user")
    async def osu_user(self, ctx, *, user):
        user = await self.bot.osu.get_user(user)
        if not user:
            return await ctx.send("No user found with that name/id.")
        embed = discord.Embed(
            color=discord.Color.magenta(),
            title=f"{user.name}'s osu! stats.",
            description=""
        )
        embed.set_thumbnail(url=f"https://a.ppy.sh/{user.id}")
        embed.set_footer(text=f"ID: {user.id}")
        embed.description += f"**Level:** {user.level}\n" \
                             f"**Accuracy:** {round(user.accuracy, 2)}%\n" \
                             f"**Playcount:** {user.playcount}\n" \
                             f"**PP Rank:** #{user.pp_rank}\n" \
                             f"**PP:** {user.pp_raw}\n" \
                             f"**Country rank:** #{user.pp_country_rank}\n" \
                             f"**Time played:** {formatting.get_time_friendly(user.total_seconds_played)}\n"
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Api(bot))
