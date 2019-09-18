from discord.ext import commands
from .utils import formatting
from aiOsu import OsuClient
import discord
import typing


class Api(commands.Cog):
    """
    Image manipulation commands.
    """

    def __init__(self, bot):
        self.bot = bot
        self.bot.osu = OsuClient(self.bot.config.OSU_API, session=self.bot.session, loop=self.bot.loop)

    @commands.group(name="osu", invoke_without_command=True)
    async def osu(self, ctx):
        """
        Base command for all other osu commands.
        """
        return await ctx.send("Please choose a valid subcommand.")

    @osu.command(name="user")
    async def osu_user(self, ctx, *, user: typing.Union[int, str]):
        """
        Get an osu! user based on their username/id.

        `user`: Can be the users id, or username.
        """
        # Find osu users with the users search term.
        users = await self.bot.osu.get_user(user)

        # If no users were found.
        if not users:
            return await ctx.send("No user found with that name/id.")

        # Paginate whatever users we do find.
        embeds = []
        for user in users:
            embed = discord.Embed(
                color=discord.Color.magenta(),
                title=f"{user.name}'s osu! stats.",
                url=f"https://osu.ppy.sh/users/{user.id}",
                description=""
            )
            embed.add_field(name=f"General information:", value=f"**Name:** {user.name}\n"
                                                                f"**Country:** {user.country}\n"
                                                                f"**Level:** {round(float(user.level), 2)}\n"
                                                                f"**Accuracy:** {round(float(user.accuracy), 2)}%\n"
                                                                f"**Time played:** {formatting.get_time_friendly(int(user.total_seconds_played))}\n", inline=False)
            embed.add_field(name=f"Stats:", value=f"**Total score:** {format(int(user.total_score), ',')}\n"
                                                  f"**Ranked score:** {format(int(user.ranked_score), ',')}\n"
                                                  f"**Playcount:** {format(int(user.play_count), ',')}\n"
                                                  f"**PP:** {format(int(round(float(user.pp))), ',')}\n"
                                                  f"**PP Rank:** #{format(int(user.pp_rank), ',')}\n"
                                                  f"**PP Country rank:** #{format(int(user.pp_country_rank), ',')}\n", inline=False)
            embed.add_field(name=f"Beatmap stats:", value=f"```py\n"
                                                          f"SS   |SSH  |S    |SH   |A\n"
                                                          f"{user.count_ss}{' ' * int((5 - len(user.count_ss)))}|{user.count_ssh}{' ' * int((5 - len(user.count_ssh)))}|{user.count_s}{' ' * int((5 - len(user.count_s)))}|{user.count_sh}{' ' * int((5 - len(user.count_sh)))}|{user.count_a}"
                                                          f"```", inline=False)
            embed.set_footer(text=f"ID: {user.id}")
            embed.set_thumbnail(url=f"https://a.ppy.sh/{user.id}")
            embeds.append(embed)
        return await ctx.paginate_embeds(entries=embeds)

    @osu.command(name="beatmap")
    async def osu_beatmap(self, ctx, beatmap_id: int):
        """
        Get an osu! beatmap from its id/set id.
        """

        # Get all beatmaps matching the search term.
        beatmaps = await self.bot.osu.get_beatmaps(beatmapset_id=beatmap_id, limit=10)

        # If none were found
        if not beatmaps:
            beatmaps = await self.bot.osu.get_beatmaps(beatmap_id=beatmap_id, limit=10)
            if not beatmaps:
                return await ctx.send("No beatmaps/beatmap-sets were found with that id.")

        # Paginate whatever beatmaps we do find.
        embeds = []
        for beatmap in beatmaps:
            embed = discord.Embed(
                color=discord.Color.magenta(),
                title=f"{beatmap.title}",
                url=f"https://osu.ppy.sh/beatmapsets/{beatmap.set_id}#osu/{beatmap.id}",
                description=""
            )
            embed.add_field(name=f"Set information:", value=f"**Title:** {beatmap.title}\n"
                                                            f"**Artist:** {beatmap.artist}\n"
                                                            f"**Source:** {beatmap.source}\n"
                                                            f"**Creator:** {beatmap.creator}\n"
                                                            f"**Rating:** {round(float(beatmap.rating), 2)}\n"
                                                            f"**Mode:** {beatmap.mode}\n"
                                                            f"**Playcount:** {beatmap.play_count}\n")
            embed.add_field(name=f"Map information:", value=f"**Difficulty:** {beatmap.difficulty_name} - {round(float(beatmap.difficulty_rating), 2)}\n"
                                                            f"**Total length:** {formatting.get_time_friendly(int(beatmap.total_length))}\n"
                                                            f"**BPM:** {beatmap.bpm}\n"
                                                            f"**Circles:** {beatmap.circle_count}\n"
                                                            f"**Spinners:** {beatmap.spinner_count}\n"
                                                            f"**Sliders:** {beatmap.slider_count}\n"
                                                            f"**Max combo:** {beatmap.max_combo}\n")
            embed.set_image(url=f"https://assets.ppy.sh/beatmaps/{beatmap.set_id}/covers/cover.jpg")
            embed.set_footer(text=f"SET ID: {beatmap.set_id} | ID: {beatmap.id}")
            embeds.append(embed)
        return await ctx.paginate_embeds(entries=embeds)


def setup(bot):
    bot.add_cog(Api(bot))
