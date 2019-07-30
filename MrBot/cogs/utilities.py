from .utils import get_information
from discord.ext import commands
from io import BytesIO
import inspect
import pathlib
import aiohttp
import discord
import codecs
import random
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
		self.session = aiohttp.ClientSession(loop=bot.loop)

	def get_bot_uptime(self):
		current_time = time.time()
		second = current_time - start_time
		minute, second = divmod(second, 60)
		hour, minute = divmod(minute, 60)
		day, hour = divmod(hour, 24)
		days = round(day)
		hours = round(hour)
		minutes = round(minute)
		seconds = round(second)
		return f'{days} Days, {hours} Hours, {minutes} Minutes, {seconds} Seconds'

	@commands.command(name='info', aliases=['about'])
	async def info(self, ctx):
		"""
		Information about the bot.
		"""

		async with self.session.get(f"https://discordbots.org/api/widget/424637852035317770.png?certifiedcolor={random.randint(0, 999999)}") as req:
			image = BytesIO(await req.read())
		image.seek(0)
		embed = discord.Embed(
			colour=0xFF0000,
			timestamp=ctx.message.created_at,
		)
		embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
		embed.set_footer(text=f'ID: {self.bot.user.id}')
		embed.set_image(url="attachment://dbl.png")
		embed.add_field(name="__**MrBot's information.**__", value=f"MrBot is an all purpose discord bot "
		                                                           f"coded by MrRandom#7593. This bot has many of your typical bot features "
		                                                           f"and quite a few unique ones. MrBot is still being actively worked on "
		                                                           f"and new features are being added all the time so be sure to join the "
		                                                           f"bot's support server [here](https://discord.gg/fKbeTr4).", inline=False)
		embed.add_field(name="__**Stats:**__", value=f"**Ping:** {await get_information.get_ping(ctx)}\n**Uptime:** {self.get_bot_uptime()}\n" \
							                         f"**Guilds:** {len(self.bot.guilds)}\n**Total users:** {len(self.bot.users)}\n"
													 f"**Extensions:** {len(self.bot.cogs)}\n**Commands:** {len(self.bot.commands)}\n"
													 f"**Discord.py Version:** {str(discord.__version__)}", inline=False)
		embed.add_field(name="__**Links:**__", value=
							f"**[Bot Invite](https://discordapp.com/oauth2/authorize?client_id=424637852035317770&scope=bot&permissions=37080128)**\n" \
			                f"**[DBL Upvote](https://discordbots.org/bot/424637852035317770/vote)**\n**[Support server](https://discord.gg/fKbeTr4)**", inline=False)
		return await ctx.send(file=discord.File(fp=image, filename="dbl.png"), embed=embed)

	@commands.command(name='stats')
	async def stats(self, ctx):
		"""
		Stats about the system MrBot is running on and other data.
		"""

		embed = discord.Embed(
			colour=0xFF0000,
			timestamp=ctx.message.created_at,
			title="__**MrBot's System Stats.**__",
			description=""
		)
		embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
		embed.add_field(name="__**System CPU:**__", value=f"**Cores:** {psutil.cpu_count(logical=False)}\n**Usage:** {process.cpu_percent()}%\n" \
			                                       f"**Frequency:** {round(psutil.cpu_freq().current, 2)} Mhz", inline=False)
		embed.add_field(name="__**System Memory:**__", value=f"**Total:** {round(psutil.virtual_memory().total/1073741824, 2)} GB\n"
													  f"**Used:** {round(psutil.virtual_memory().used/1073741824, 2)} GB\n"
													  f"**Available:** {round(psutil.virtual_memory().available/1073741824, 2)} GB", inline=False)
		embed.add_field(name="__**Process information:**__", value=f"**Memory usage:** {process.memory_info().rss//(1024**2)}mb\n"
																   f"**CPU usage:** {process.cpu_percent()}%", inline=False)
		embed.add_field(name="__**Bot Information:**__", value=f"**Messages seen:** {self.bot.messages_seen}\n**Commands run:** {self.bot.commands_run}\n"
															   f"**Messages sent:** {self.bot.messages_sent}", inline=False)
		return await ctx.send(embed=embed)

	@commands.command(name='ping')
	async def ping(self, ctx):
		"""
		Display the bots ping.
		"""

		start = time.perf_counter()
		message = await ctx.send("Ping...")
		end = time.perf_counter()
		duration = (end - start) * 1000
		await message.edit(content='Pong! {:.2f}ms'.format(duration))

	@commands.command(name='serverinfo')
	async def serverinfo(self, ctx):
		"""
		Information about the current server.
		"""

		embed = discord.Embed(
			colour=0xFF0000,
			timestamp=ctx.message.created_at,
			title=f"{ctx.guild.name}'s Stats and Information."
		)
		embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
		embed.set_footer(text=f'ID: {ctx.guild.id}')
		embed.add_field(name='__**General information:**__', value=f'**Owner:** {ctx.guild.owner}\n'
															       f'**Server created at:** {ctx.guild.created_at.__format__("%A %d %B %Y at %H:%M")}\n'
															       f'**Members:** {ctx.guild.member_count}', inline=False)
		embed.add_field(name='__**Voice channels:**__', value=f'**Region:** {get_information.guild_region(ctx.guild)}\n**Count:** {len(ctx.guild.voice_channels)}\n'
															  f'**AFK timeout:** {int(ctx.guild.afk_timeout/60)} minutes\n**AFK channel:** {ctx.guild.afk_channel}\n'
															  f'', inline=False)
		embed.add_field(name='__**Text channels:**__',value=f'**Count:** {len(ctx.guild.text_channels)}\n', inline=False)
		embed.add_field(name='__**Role information:**__',value=f'**Roles:** {", ".join([r.mention for r in ctx.guild.roles])}\n**Count:** {len(ctx.guild.roles)}\n', inline=False)
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
		embed.add_field(name='__**General information:**__', value=f'**Discord Name:** {user}\n**Nickname:** {user.nick}\n'
																   f'**Account created at:** {user.created_at.__format__("%A %d %B %Y at %H:%M")}\n'
																   f'**Status:** {get_information.user_status(user)}\n**Activity:** {get_information.user_activity(user)}', inline=False)
		embed.add_field(name='__**Server-related information:**__', value=f'**Joined server at:** {user.joined_at.__format__("%A %d %B %Y at %H:%M")}\n'
																		  f'**Roles:** {", ".join([r.mention for r in user.roles])}')
		embed.set_thumbnail(url=user.avatar_url)
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
		embed.add_field(name=f"{user.name}'s Avatar", value=f'[Avatar URL]({user.avatar_url_as(size=1024)})', inline=False)
		embed.set_image(url=f'{user.avatar_url_as(size=1024)}')
		return await ctx.send(embed=embed)

	@commands.command(name='upvote')
	async def upvote(self, ctx):
		"""
		Send a link to the bots upvote page.
		"""

		async with self.session.get(f"https://discordbots.org/api/widget/424637852035317770.png?certifiedcolor={random.randint(0, 999999)}") as req:
			image = BytesIO(await req.read())
		image.seek(0)
		embed = discord.Embed(
			colour=0xFF0000,
			timestamp=ctx.message.created_at
		)
		embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
		embed.add_field(name=f'Upvote Link:', value=f'[Click here!](https://discordbots.org/bot/424637852035317770/vote)')
		embed.set_image(url="attachment://dbl.png")
		await ctx.send(file=discord.File(fp=image, filename="dbl.png"), embed=embed)

	@commands.command(name='source')
	async def source(self, ctx, *, command: str = None):
		"""
		Github link to the source of a command.
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

	@commands.command(name='linecount', aliases=['lc'])
	async def linecount(self,ctx):
		"""
		Display how many lines of code the bot is made out of.
		"""

		total = 0
		file_amount = 0
		comments = 0
		for path, subdirs, files in os.walk('.'):
			for name in files:
				if name.endswith('.py'):
					file_amount += 1
					with codecs.open('./' + str(pathlib.PurePath(path, name)), 'r', 'utf-8') as f:
						for i, l in enumerate(f):
							if l.strip().startswith('#'):
								comments += 1
							if len(l.strip()) is 0:
								pass
							else:
								total += 1
		await ctx.send(f'MrBot is made of {total:,} lines of code and {comments:,} comments. Spread out across {file_amount:,} files.')

	@commands.command(name='screenshare', aliases=['ss'])
	async def screenshare(self, ctx, channel: discord.VoiceChannel = None):
		"""
		Generate a link that allows for screenshare in voice channels.
		"""

		if not channel:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send('There is no voice channel to create a screenshare from, join one or specify one.')
		link = f'http://www.discordapp.com/channels/{ctx.guild.id}/{channel.id}'
		return await ctx.send(f'Clicking on this link while in the voice channel `{channel.name}` will start a guild screenshare in that channel.\n\n{link}')


def setup(bot):
	bot.add_cog(Utilities(bot))
