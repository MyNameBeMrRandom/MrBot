from discord.ext import commands
from .utils import formatting
from .utils import botUtils
import discord
import inspect
import psutil
import time
import os


start_time = time.time()


class Utilities(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="about", aliases=["info"])
    async def about(self, ctx):
        """
        Get information about the bot.
        """

        # Get bot information.
        typingms, latencyms, discordms, average = await botUtils.ping(self.bot, ctx)
        files, functions, comments, lines = botUtils.linecount()
        uptime = time.time() - start_time

        # Create embed
        embed = discord.Embed(
            colour=0xFF0000,
        )
        embed.set_author(icon_url=self.bot.user.avatar_url_as(format="png"), name=f"{self.bot.user.name}'s Info")
        embed.set_thumbnail(url=self.bot.user.avatar_url_as(format="png"))
        embed.set_footer(text=f"ID: {self.bot.user.id}")
        embed.set_image(url=await self.bot.dblpy.generate_widget_large(bot_id=627491967391236097, cert=botUtils.random_colour()))
        embed.add_field(name="__**Bot info:**__", value=f"**Uptime:** {formatting.get_time_friendly(uptime)}\n"
                                                        f"**Total users:** {len(self.bot.users)}\n"
                                                        f"**Guilds:** {len(self.bot.guilds)}\n")
        embed.add_field(name="__**Stats:**__", value=f"**Discord.py Version:** {str(discord.__version__)}\n"
                                                     f"**Commands:** {len(self.bot.commands)}\n"
                                                     f"**Cogs:** {len(self.bot.cogs)}\n")
        embed.add_field(name="__**Code:**__", value=f"**Comments:** {comments}\n **Functions:** {functions}\n"
                                                    f"**Lines:** {lines}\n **Files:** {files}\n")
        embed.add_field(name="__**Ping:**__", value=f"**Typing:** {typingms}ms\n**Latency:** {latencyms}ms\n"
                                                    f"**Discord:** {discordms}ms\n**Average:** {average}ms")
        embed.add_field(name="__**Links:**__", value=f"**[Bot Invite](https://discordapp.com/oauth2/authorize?client_id=627491967391236097&scope=bot)** | "
                                                     f"**[DBL Upvote](https://discordbots.org/bot/627491967391236097/vote)** | "
                                                     f"**[Support server](https://discord.gg/XejxSqT)** | "
                                                     f"**[Source code](https://github.com/MyNameBeMrRandom/MrBot)**", inline=False)
        return await ctx.send(embed=embed)

    @commands.command(name="system", aliases=["sys"])
    async def system(self, ctx):
        """
        Get information about the system the bot is running on.
        """

        process = psutil.Process()
        embed = discord.Embed(
            colour=0xFF0000,
        )
        embed.set_author(icon_url=self.bot.user.avatar_url_as(format="png"), name=f"{self.bot.user.name}'s system stats")
        embed.set_thumbnail(url=self.bot.user.avatar_url_as(format="png"))
        embed.add_field(name="__**System CPU:**__", value=f"**Cores:** {psutil.cpu_count()}\n"
                                                          f"**Usage:** {psutil.cpu_percent(interval=0.1)}%\n"
                                                          f"**Frequency:** {round(psutil.cpu_freq().current, 2)} Mhz")
        embed.add_field(name="__**System Memory:**__", value=f"**Total:** {round(psutil.virtual_memory().total/1048576)} mb\n"
                                                             f"**Used:** {round(psutil.virtual_memory().used/1048576)} mb\n"
                                                             f"**Available:** {round(psutil.virtual_memory().available/1048576)} mb")
        embed.add_field(name="__**System Disk:**__", value=f"**Total:** {round(psutil.disk_usage('/').total/1073741824, 2)} GB\n"
                                                           f"**Used:** {round(psutil.disk_usage('/').used/1073741824, 2)} GB\n"
                                                           f"**Free:** {round(psutil.disk_usage('/').free/1073741824, 2)} GB")
        embed.add_field(name="__**Process information:**__", value=f"**Memory usage:** {round(process.memory_full_info().rss/1048576, 2)} mb\n"
                                                                   f"**CPU usage:** {process.cpu_percent()}%\n"
                                                                   f"**Threads:** {process.num_threads()}")
        return await ctx.send(embed=embed)

    @commands.command(name="upvote")
    async def upvote(self, ctx):
        """
        Get a link to the bots upvote page.
        """

        embed = discord.Embed(
            colour=0xFF0000,
            description=f"[Click here](https://discordbots.org/bot/627491967391236097/vote) to upvote."
        )
        embed.set_image(url=await self.bot.dblpy.generate_widget_large(bot_id=627491967391236097, cert=botUtils.random_colour()))
        await ctx.send(embed=embed)

    @commands.command(name="code_info", aliases=["ci"])
    async def code_info(self, ctx):
        """
        Get information about the bots code.
        """

        files, functions, comments, lines = botUtils.linecount()
        return await ctx.send(f"**Comments:** {comments}\n"
                              f"**Functions:** {functions}\n"
                              f"**Lines:** {lines}\n"
                              f"**Files:** {files}\n")

    @commands.command(name="ping")
    async def ping(self, ctx):
        """
        Gets the bots ping.
        """

        typingms, latencyms, discordms, average = await botUtils.ping(self.bot, ctx)
        return await ctx.send(f"**Typing:** {typingms}ms\n**Latency:** {latencyms}ms\n"
                              f"**Discord:** {discordms}ms\n**Average:** {average}ms")

    @commands.command(name="uptime")
    async def uptime(self, ctx):
        """
        Get the bots uptime.
        """

        uptime = time.time() - start_time
        return await ctx.send(f"{formatting.get_time_friendly(uptime)}")

    @commands.command(name="source")
    async def source(self, ctx, *, command: str = None):
        """
        Get a github link for the source of a command.

        `command`: The name of the command you want the source for.
        """

        github_url = "https://github.com/MyNameBeMrRandom/MrBot"
        if command is None:
            return await ctx.send(f"<{github_url}>")
        obj = self.bot.get_command(command.replace(".", " "))
        if obj is None:
            return await ctx.send("I could not find that command.")
        src = obj.callback.__code__
        lines, firstlineno = inspect.getsourcelines(src)
        location = ""
        if not obj.callback.__module__.startswith("discord"):
            location = os.path.relpath(src.co_filename).replace("\\", "/")
        final_url = f"<{github_url}/blob/master/MrBot/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>"
        await ctx.send(final_url)

    @commands.command(name="screenshare", aliases=["ss"])
    async def screenshare(self, ctx, channel: discord.VoiceChannel = None):
        """
        Get a link for screensharing in the specified voice channel.

        `channel`: The channel you want to screeshare in. Can be an ID, mention or name.
        """

        if not channel:
            if not ctx.author.voice:
                return await ctx.send("There is no voice channel to create a screenshare from, join one or specify one.")
            channel = ctx.author.voice.channel
        link = f"<http://www.discordapp.com/channels/{ctx.guild.id}/{channel.id}>"
        return await ctx.send(f"Clicking on this link while in the voice channel `{channel.name}` will start a guild screenshare in that channel.\n\n{link}")

    @commands.command(name="avatar")
    async def avatar(self, ctx, *, user: discord.Member = None):
        """
        Get yours or a specified users avatar.


        `user`: The user who you want the avatar of. Can be an ID, mention or name.
        """

        # If the user didnt choose someone.
        if not user:
            user = ctx.author

        embed = discord.Embed(
            colour=0xFF0000,
        )
        embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
        if user.is_avatar_animated():
            embed.add_field(name=f"{user.name}'s Avatar", value=f"[GIF]({user.avatar_url_as(size=1024, format='gif')}) | "
                                                                f"[PNG]({user.avatar_url_as(size=1024, format='png')}) | "
                                                                f"[JPEG]({user.avatar_url_as(size=1024, format='jpeg')}) | "
                                                                f"[WEBP]({user.avatar_url_as(size=1024, format='webp')})", inline=False)
            embed.set_image(url=f"{user.avatar_url_as(size=1024, format='gif')}")
        else:
            embed.add_field(name=f"{user.name}'s Avatar", value=f"[PNG]({user.avatar_url_as(size=1024, format='png')}) | "
                                                                f"[JPEG]({user.avatar_url_as(size=1024, format='jpeg')}) | "
                                                                f"[WEBP]({user.avatar_url_as(size=1024, format='webp')})", inline=False)
            embed.set_image(url=f"{user.avatar_url_as(size=1024, format='png')}")
        return await ctx.send(embed=embed)

    @commands.command(name="serverinfo")
    async def serverinfo(self, ctx):
        """
        Get information about the current server.
        """

        online, offline, idle, dnd = botUtils.guild_user_status_count(ctx.guild)
        embed = discord.Embed(
            colour=0xFF0000,
            title=f"{ctx.guild.name}'s Stats and Information."
        )
        embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
        embed.set_footer(text=f"ID: {ctx.guild.id}")
        embed.add_field(name="__**General information:**__", value=f"**Owner:** {ctx.guild.owner}\n"
                                                                   f"**Server created at:** {ctx.guild.created_at.__format__('%A %d %B %Y at %H:%M')}\n"
                                                                   f"**Members:** {ctx.guild.member_count} |"
                                                                   f"<:online:608059247099379732>{online} |"
                                                                   f"<:idle:608059272923709441>{idle} |"
                                                                   f"<:dnd:608059261678911582>{dnd} |"
                                                                   f"<:offline:608059228191719424>{offline}\n"
                                                                   f"**Verification level:** {botUtils.guild_verification_level(ctx.guild)}\n"
                                                                   f"**Content filter level:** {botUtils.guild_content_filter_level(ctx.guild)}\n"
                                                                   f"**2FA:** {botUtils.guild_mfa_level(ctx.guild)}\n", inline=False)
        embed.add_field(name="__**Channels:**__", value=f"**Text channels:** {len(ctx.guild.text_channels)}\n"
                                                        f"**Voice channels:** {len(ctx.guild.voice_channels)}\n"
                                                        f"**Voice region:** {botUtils.guild_region(ctx.guild)}\n"
                                                        f"**AFK timeout:** {int(ctx.guild.afk_timeout/60)} minutes\n"
                                                        f"**AFK channel:** {ctx.guild.afk_channel}\n", inline=False)
        embed.add_field(name="__**Role information:**__", value=f"**Roles:** {' '.join([r.mention for r in ctx.guild.roles[1:]])}\n"
                                                                f"**Count:** {len(ctx.guild.roles)}\n", inline=False)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        return await ctx.send(embed=embed)

    @commands.command(name="userinfo")
    async def userinfo(self, ctx, *, user: discord.Member = None):
        """
        Get information about you, or a specified user.

        `user`: The user who you want information about. Can be an ID, mention or name.
        """

        if not user:
            user = ctx.author
        user = ctx.guild.get_member(user.id)
        embed = discord.Embed(
            colour=botUtils.embed_color(user),
            title=f"{user.name}'s Stats and Information."
        )
        embed.set_author(icon_url=user.avatar_url, name=user.name)
        embed.set_footer(text=f"ID: {user.id}")
        embed.add_field(name="__**General information:**__", value=f"**Discord Name:** {user}\n"
                                                                   f"**Account created:** {user.created_at.__format__('%A %d %B %Y at %H:%M')}\n"
                                                                   f"**Status:** {botUtils.user_status(user)}\n"
                                                                   f"**Activity:** {botUtils.user_activity(user)}", inline=False)
        embed.add_field(name="__**Server-related information:**__", value=f"**Nickname:** {user.nick}\n"
                                                                          f"**Joined server:** {user.joined_at.__format__('%A %d %B %Y at %H:%M')}\n"
                                                                          f"**Roles:** {' '.join([r.mention for r in user.roles[1:]])}")
        embed.set_thumbnail(url=user.avatar_url)
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utilities(bot))
