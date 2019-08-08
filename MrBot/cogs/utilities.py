from .utils import get_information
from discord.ext import commands
from .utils import calculations
import inspect
import discord
import psutil
import time
import os


start_time = time.time()
process = psutil.Process()


class Utilities(commands.Cog):
    """
    Server/user/bot utility commands.
    """

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    @commands.command(name='info', aliases=['about'])
    async def info(self, ctx):
        """
        Get information about the bot.
        """

        typingms, latencyms, discordms, average = await get_information.get_ping(ctx, self.bot)
        file_amount, comments, lines, functions = get_information.linecount()
        uptime = time.time() - start_time
        embed = discord.Embed(
            colour=0xFF0000,
            timestamp=ctx.message.created_at,
        )
        embed.set_author(icon_url=self.bot.user.avatar_url_as(format='png'), name='MrBots Info')
        embed.set_footer(text=f'ID: {self.bot.user.id}')
        embed.set_thumbnail(url=self.bot.user.avatar_url_as(format='png'))
        embed.set_image(url=await self.bot.dblpy.generate_widget_large(cert=calculations.random_colour()))
        embed.add_field(name="__**Bot info:**__", value=f"**Uptime:** {calculations.get_time_friendly(uptime)}\n"
                                                        f"**Total users:** {len(self.bot.users)}\n"
                                                        f"**Guilds:** {len(self.bot.guilds)}\n")
        embed.add_field(name="__**Stats:**__", value=f"**Discord.py Version:** {str(discord.__version__)}\n"
                                                     f"**Commands:** {len(self.bot.commands)}\n"
                                                     f"**Cogs:** {len(self.bot.cogs)}\n")
        embed.add_field(name="__**Code:**__", value=f"**Comments:** {comments}\n"
                                                    f"**Functions:** {functions}\n"
                                                    f"**Lines:** {lines}\n"
                                                    f"**Files:** {file_amount}\n")
        embed.add_field(name='__**Ping:**__', value=f'**Typing:** {typingms}ms\n**Latency:** {latencyms}ms\n'
                                                    f'**Discord:** {discordms}ms\n**Average:** {average}ms')
        embed.add_field(name="__**Links:**__", value=f"**[Bot Invite](https://discordapp.com/oauth2/authorize?client_id=424637852035317770&scope=bot&permissions=37080128)** | "
                                                     f"**[DBL Upvote](https://discordbots.org/bot/424637852035317770/vote)** | "
                                                     f"**[Support server](https://discord.gg/fKbeTr4)** | "
                                                     f"**[Source code](https://github.com/MyNameBeMrRandom/MrBot)**", inline=False)
        return await ctx.send(embed=embed)

    @commands.command(name='stats')
    async def stats(self, ctx):
        """
        Get information acount the system the bot is running on and other data.
        """

        embed = discord.Embed(
            colour=0xFF0000,
            timestamp=ctx.message.created_at,
        )
        embed.set_author(icon_url=self.bot.user.avatar_url_as(format='png'), name='MrBots Stats')
        embed.set_thumbnail(url=self.bot.user.avatar_url_as(format='png'))
        embed.add_field(name="__**System CPU:**__", value=f"**Cores:** {psutil.cpu_count(logical=False)}\n"
                                                          f"**Usage:** {psutil.cpu_percent()}%\n" \
                                                          f"**Frequency:** {round(psutil.cpu_freq().current, 2)} Mhz")
        embed.add_field(name="__**System Memory:**__", value=f"**Total:** {round(psutil.virtual_memory().total/1073741824, 2)} GB\n"
                                                             f"**Used:** {round(psutil.virtual_memory().used/1073741824, 2)} GB\n"
                                                             f"**Available:** {round(psutil.virtual_memory().available/1073741824, 2)} GB")
        embed.add_field(name="__**Bot Information:**__", value=f"**Messages seen:** {self.bot.messages_seen}\n"
                                                               f"**Commands run:** {self.bot.commands_run}\n"
                                                               f"**Messages sent:** {self.bot.messages_sent}",)
        embed.add_field(name="__**Process information:**__", value=f"**Memory usage:** {process.memory_info().rss//(1024**2)}mb\n"
                                                                   f"**CPU usage:** {process.cpu_percent()}%")
        return await ctx.send(embed=embed)

    @commands.command(name='ping')
    async def ping(self, ctx):
        """
        Gets the bots pings.
        """

        typingms, latencyms, discordms, average = await get_information.get_ping(ctx, self.bot)
        return await ctx.send(f'**Typing:** {typingms}ms\n**Latency:** {latencyms}ms\n'
                              f'**Discord:** {discordms}ms\n**Average:** {average}ms')

    @commands.command(name='uptime')
    async def uptime(self, ctx):
        """
        Get the bots uptime.
        """

        uptime = time.time() - start_time
        return await ctx.send(f'{calculations.get_time_friendly(uptime)}')

    @commands.command(name='code_info', aliases=['ci'])
    async def code_info(self, ctx):
        """
        Get information about the bots code.
        """

        file_amount, comments, lines, functions = get_information.linecount()
        return await ctx.send(f"**Comments:** {comments}\n"
                             f"**Functions:** {functions}\n"
                             f"**Lines:** {lines}\n"
                             f"**Files:** {file_amount}\n")

    @commands.command(name='source')
    async def source(self, ctx, *, command: str = None):
        """
        Get a github link for the source of a command.
        """

        github_url = 'https://github.com/MyNameBeMrRandom/MrBot'
        if command is None:
            return await ctx.send(github_url)
        obj = self.bot.get_command(command.replace('.', ' '))
        if obj is None:
            return await ctx.send('Could not find that command.')
        src = obj.callback.__code__
        lines, firstlineno = inspect.getsourcelines(src)
        if not obj.callback.__module__.startswith('discord'):
            location = os.path.relpath(src.co_filename).replace('\\', '/')
        else:
            location = obj.callback.__module__.replace('.', '/') + '.py'
            github_url = 'https://github.com/Rapptz/discord.py'
        final_url = f'<{github_url}/blob/master/MrBot/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>'
        await ctx.send(final_url)

    @commands.command(name='upvote')
    async def upvote(self, ctx):
        """
        Get the bots upvote page.
        """

        embed = discord.Embed(
            colour=0xFF0000,
            timestamp=ctx.message.created_at
        )
        embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
        embed.add_field(name=f'Upvote Link:', value=f'[Click here!](https://discordbots.org/bot/424637852035317770/vote)')
        embed.set_image(url=await self.bot.dblpy.generate_widget_large(cert=calculations.random_colour()))
        await ctx.send(embed=embed)

    @commands.command(name='upvotes')
    async def upvotes(self, ctx):

        upvotes = await self.bot.dblpy.get_bot_upvotes()
        if not upvotes:
            return await ctx.send('No upvotes')
        embed = discord.Embed(
            colour=0xFF0000,
            timestamp=ctx.message.created_at,
            description=""
        )
        embed.set_author(icon_url=self.bot.user.avatar_url_as(format='png'), name='MrBots upvoters:')
        for upvoter in upvotes:
            embed.description += f"{upvoter['username']}{upvoter['discriminator']}\n"
        return await ctx.send(embed=embed)

    @commands.command(name='avatar')
    async def avatar(self, ctx, user: discord.Member = None):
        """
        Get a users avatar.
        """

        if not user:
            user = ctx.author
        embed = discord.Embed(
            colour=0xFF0000,
            timestamp=ctx.message.created_at
        )
        embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
        if user.is_avatar_animated():
            embed.add_field(name=f"{user.name}'s Avatar", value=f'[GIF]({user.avatar_url_as(size=1024, format="gif")}) | '
                                                                f'[PNG]({user.avatar_url_as(size=1024, format="png")}) | '
                                                                f'[JPEG]({user.avatar_url_as(size=1024, format="jpeg")}) | '
                                                                f'[WEBP]({user.avatar_url_as(size=1024, format="webp")}) | ', inline=False)
            embed.set_image(url=f'{user.avatar_url_as(size=1024, format="gif")}')
        else:
            embed.add_field(name=f"{user.name}'s Avatar", value=f'[PNG]({user.avatar_url_as(size=1024, format="png")}) | '
                                                                f'[JPEG]({user.avatar_url_as(size=1024, format="jpeg")}) | '
                                                                f'[WEBP]({user.avatar_url_as(size=1024, format="webp")}) | ', inline=False)
            embed.set_image(url=f'{user.avatar_url_as(size=1024, format="png")}')
        return await ctx.send(embed=embed)

    @commands.command(name='screenshare', aliases=['ss'])
    async def screenshare(self, ctx, channel: discord.VoiceChannel = None):
        """
        Get a link that enables you to screenshare in voice channels.
        """

        if not channel:
            if not ctx.author.voice:
                return await ctx.send('There is no voice channel to create a screenshare from, join one or specify one.')
            channel = ctx.author.voice.channel
        link = f'<http://www.discordapp.com/channels/{ctx.guild.id}/{channel.id}>'
        return await ctx.send(f'Clicking on this link while in the voice channel `{channel.name}` will start a guild screenshare in that channel.\n\n{link}')

    @commands.command(name='serverinfo')
    async def serverinfo(self, ctx):
        """
        Get information about the server.
        """

        online, offline, idle, dnd = get_information.guild_user_count(ctx.guild)
        embed = discord.Embed(
            colour=0xFF0000,
            timestamp=ctx.message.created_at,
            title=f"{ctx.guild.name}'s Stats and Information."
        )
        embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
        embed.set_footer(text=f'ID: {ctx.guild.id}')
        embed.add_field(name='__**General information:**__', value=f'**Owner:** {ctx.guild.owner}\n'
                                                                   f'**Server created at:** {ctx.guild.created_at.__format__("%A %d %B %Y at %H:%M")}\n'
                                                                   f'**Members:** {ctx.guild.member_count} |'
                                                                   f'<:online:608059247099379732>{online} |'
                                                                   f'<:idle:608059272923709441>{idle} |'
                                                                   f'<:dnd:608059261678911582>{dnd} |'
                                                                   f'<:offline:608059228191719424>{offline}', inline=False)
        embed.add_field(name='__**Voice channels:**__', value=f'**Region:** {get_information.guild_region(ctx.guild)}\n'
                                                              f'**Count:** {len(ctx.guild.voice_channels)}\n'
                                                              f'**AFK timeout:** {int(ctx.guild.afk_timeout/60)} minutes\n'
                                                              f'**AFK channel:** {ctx.guild.afk_channel}\n', inline=False)
        embed.add_field(name='__**Text channels:**__',value=f'**Count:** {len(ctx.guild.text_channels)}\n', inline=False)
        embed.add_field(name='__**Role information:**__',value=f'**Roles:** {", ".join([r.mention for r in ctx.guild.roles])}\n'
                                                               f'**Count:** {len(ctx.guild.roles)}\n', inline=False)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        return await ctx.send(embed=embed)

    @commands.command(name='userinfo')
    async def userinfo(self, ctx, user: discord.Member = None):
        """
        Information about you, or a specified user.
        """

        if not user:
            user = ctx.author
        embed = discord.Embed(
            colour=get_information.embed_color(user),
            timestamp=ctx.message.created_at,
            title=f"{user.name}'s Stats and Information."
        )
        embed.set_author(icon_url=user.avatar_url, name=user.name)
        embed.set_footer(text=f'ID: {user.id}')
        embed.add_field(name='__**General information:**__', value=f'**Discord Name:** {user}\n'
                                                                   f'**Nickname:** {user.nick}\n'
                                                                   f'**Account created at:** {user.created_at.__format__("%A %d %B %Y at %H:%M")}\n'
                                                                   f'**Status:** {get_information.user_status(user)}\n'
                                                                   f'**Activity:** {get_information.user_activity(user)}', inline=False)
        embed.add_field(name='__**Server-related information:**__', value=f'**Joined server at:** {user.joined_at.__format__("%A %d %B %Y at %H:%M")}\n'
                                                                          f'**Roles:** {", ".join([r.mention for r in user.roles])}')
        embed.set_thumbnail(url=user.avatar_url)
        return await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Utilities(bot))
