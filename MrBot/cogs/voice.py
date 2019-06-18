from discord.ext import commands
import humanize
import itertools
import datetime
import wavelink
import asyncio
import discord
import random
import re



RURL = re.compile(r'https?:(?:www\.)?.+')

class Track(wavelink.Track):

	def __init__(self, id_, info, *, ctx=None):
		super(Track, self).__init__(id_, info)

		self.channel = ctx.channel
		self.requester = ctx.author


# noinspection PyAttributeOutsideInit
class Player(wavelink.Player):

	def __init__(self, bot, guild_id: int, node: wavelink.Node):
		super(Player, self).__init__(bot, guild_id, node)
		self.bot = bot
		self.volume = 25

		self.queue = asyncio.Queue()
		self.next_event = asyncio.Event()


		self.eq = 'Flat'

		self.bot.loop.create_task(self.player_loop())

	@property
	def entries(self):
		# noinspection PyProtectedMember
		return list(self.queue._queue)

	async def player_loop(self):
		await self.bot.wait_until_ready()
		await self.set_volume(self.volume)
		await self.set_preq('Flat')
		while True:
			self.next_event.clear()

			song = await self.queue.get()
			if not song:
				continue

			self.current = song
			self.paused = False

			await self.play(song)
			await self.invoke_controller()
			await self.next_event.wait()

	async def invoke_controller(self, track: wavelink.Track = None):
		if not track:
			track = self.current
		embed = discord.Embed(title='Music controller',
		                      colour= 0x57FFF5
		                      )
		embed.set_thumbnail(url=track.thumb)
		embed.add_field(name=f'Now playing:', value=f'**[{track.title}]({track.uri})**', inline=False)
		if track.is_stream:
			embed.add_field(name='Duration:', value='Stream')
		else:
			embed.add_field(name='Duration:', value=str(datetime.timedelta(milliseconds=int(track.length))))
		embed.add_field(name='Requester:', value=track.requester.mention)
		embed.add_field(name='Volume:', value=f'{self.volume}%')
		embed.add_field(name='Queue Length:', value=str(len(self.entries)))
		embed.add_field(name=f'Equalizer:', value=f'Current: {self.eq}\nPresets: Flat/Boost/Metal/Piano')
		self.controller_message = await track.channel.send(embed=embed)


# noinspection PyProtectedMember,PyProtectedMember,PyAttributeOutsideInit,PyMethodMayBeStatic,PyUnusedLocal
class Voice(commands.Cog):
	"""
	Voice commands
	"""

	def __init__(self, bot):
		self.bot = bot

		if not hasattr(bot, 'wavelink'):
			self.bot.wavelink = wavelink.Client(bot)

		bot.loop.create_task(self.initiate_nodes())

	async def initiate_nodes(self):
		nodes = {'MAIN': {'host': '209.97.136.42',
		                  'port': 13579,
		                  'rest_url': 'http://209.97.136.42:13579',
		                  'password': "Yomama2121",
		                  'identifier': 'MAIN',
		                  'region': 'eu_west'}}

		for n in nodes.values():
			node = await self.bot.wavelink.initiate_node(host=n['host'],
			                                             port=n['port'],
			                                             rest_uri=n['rest_url'],
			                                             password=n['password'],
			                                             identifier=n['identifier'],
			                                             region=n['region'],
			                                             secure=False)

			node.set_hook(self.event_hook)

	def event_hook(self, event):

		if isinstance(event, wavelink.TrackEnd):
			event.player.next_event.set()
		elif isinstance(event, wavelink.TrackException):
			print(event.error)

	async def do_vote(self, ctx, player, command: str):
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		# noinspection PyUnusedLocal
		attr = getattr(player, command + 's', None)

	@commands.command(name='join', aliases=['connect'])
	async def join(self, ctx, *, channel: discord.VoiceChannel = None):
		"""
		Joins or moves to the users or a specified channel.
		"""
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		author = ctx.author.name
		useravatar = ctx.author.avatar_url
		if not channel:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					description=f'There is not a valid voice channel for MrBot to join, please join a channel or specify one after the command.'
				)
				embed.set_author(icon_url=useravatar, name=author)
				return await ctx.send(embed=embed)
		if player.is_connected:
			if not ctx.guild.me.voice.channel.id == channel.id:
				try:
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'MrBot moved to the `{channel}` channel'
					)
					embed.set_author(icon_url=useravatar, name=author)
					await ctx.send(embed=embed)
					return await player.connect(channel.id)
				except Exception as e:
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'MrBot was unable to move to the `{channel}` channel.\n\n**Reason: {e}**'
					)
					embed.set_author(icon_url=useravatar, name=author)
					return await ctx.send(embed=embed)
			else:
				return
		else:
			try:
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					description=f'MrBot joined the `{channel}` channel'
				)
				embed.set_author(icon_url=useravatar, name=author)
				await ctx.send(embed=embed)
				return await player.connect(channel.id)
			except Exception as e:
				print(type(e))
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					description=f'MrBot was unable to join the `{channel}` channel.\n\n**Reason: {e}**'
				)
				embed.set_author(icon_url=useravatar, name=author)
				return await ctx.send(embed=embed)

	@commands.command(name='play')
	async def play(self, ctx, *, query: str):
		"""
		Plays a song using a link or search query.
		"""
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		author = ctx.author.name
		useravatar = ctx.author.avatar_url

		await ctx.trigger_typing()
		await ctx.invoke(self.join)

		if not player.is_connected:
			return

		if not RURL.match(query):
			query = f'ytsearch:{query}'

		tracks = await self.bot.wavelink.get_tracks(query)
		if not tracks:
			embed = discord.Embed(
				colour=0x57FFF5,
				timestamp=ctx.message.created_at,
				description=f'There were no songs found with that search term, please try again.'
			)
			embed.set_author(icon_url=useravatar, name=author)
			return await ctx.send(embed=embed)

		if isinstance(tracks, wavelink.TrackPlaylist):
			for t in tracks.tracks:
				await player.queue.put(Track(t.id, t.info, ctx=ctx))
			embed = discord.Embed(
				colour=0x57FFF5,
				timestamp=ctx.message.created_at,
				description=f'Added the playlist **{tracks.data["playlistInfo"]["name"]}** to the queue with a total of **{len(tracks.tracks)}** entries.'
			)
			embed.set_author(icon_url=useravatar, name=author)
			await ctx.send(embed=embed)
		else:
			track = tracks[0]
			await player.queue.put(Track(track.id, track.info, ctx=ctx))
			embed = discord.Embed(
				colour=0x57FFF5,
				timestamp=ctx.message.created_at,
				description=f'Added the video **{track.title}** to the queue.'
			)
			embed.set_author(icon_url=useravatar, name=author)
			await ctx.send(embed=embed)

	@commands.command(name='leave', aliases=['disconnect', 'stop'])
	async def leave(self, ctx):
		"""
		Leaves the current voice channel.
		"""
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		author = ctx.author.name
		useravatar = ctx.author.avatar_url
		if player.is_connected:
			if ctx.author.voice.channel == ctx.guild.me.voice.channel:
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					description=f'MrBot left the `{ctx.guild.me.voice.channel}` channel.'
				)
				embed.set_author(icon_url=useravatar, name=author)
				await ctx.send(embed=embed)
				return await self.do_leave(ctx)
			else:
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					description=f'You need to be in the same voice channel as MrBot to use this command.'
				)
				embed.set_author(icon_url=useravatar, name=author)
				await ctx.send(embed=embed)
		else:
			embed = discord.Embed(
				colour=0x57FFF5,
				timestamp=ctx.message.created_at,
				description=f'MrBot is not currently in any voice channels.'
			)
			embed.set_author(icon_url=useravatar, name=author)
			await ctx.send(embed=embed)

	async def do_leave(self, ctx):
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		await player.disconnect()
		await player.destroy()

	@commands.command(name='pause')
	async def pause(self, ctx):
		"""
		Pause the current song.
		"""
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		author = ctx.author.name
		useravatar = ctx.author.avatar_url
		if player.is_connected:
			if ctx.author.voice:
				if ctx.author.voice.channel == ctx.guild.me.voice.channel:
					if not player.paused:
						embed = discord.Embed(
							colour=0x57FFF5,
							timestamp=ctx.message.created_at,
							description=f'{ctx.author.mention} paused the current song.'
						)
						embed.set_author(icon_url=useravatar, name=author)
						await ctx.send(embed=embed)
						return await self.do_pause(ctx)
					else:
						embed = discord.Embed(
								colour=0x57FFF5,
								timestamp=ctx.message.created_at,
								description=f'MrBot is already paused.'
							)
						embed.set_author(icon_url=useravatar, name=author)
						return await ctx.send(embed=embed)
				else:
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'You need to be in the same voice channel as MrBot to use this command.'
					)
					embed.set_author(icon_url=useravatar, name=author)
					return await ctx.send(embed=embed)
			else:
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					description=f'You need to be in the same voice channel as MrBot to use this command.'
				)
				embed.set_author(icon_url=useravatar, name=author)
				await ctx.send(embed=embed)
		else:
			embed = discord.Embed(
				colour=0x57FFF5,
				timestamp=ctx.message.created_at,
				description=f'MrBot is not currently in any voice channels.'
			)
			embed.set_author(icon_url=useravatar, name=author)
			return await ctx.send(embed=embed)

	async def do_pause(self, ctx):
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		self.paused = True
		await player.set_pause(True)

	@commands.command(name='resume')
	async def resume(self, ctx):
		"""
		Resumes the current song.
		"""
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		author = ctx.author.name
		useravatar = ctx.author.avatar_url
		if player.is_connected:
			if ctx.author.voice:
				if ctx.author.voice.channel == ctx.guild.me.voice.channel:
					if player.paused:
						embed = discord.Embed(
							colour=0x57FFF5,
							timestamp=ctx.message.created_at,
							description=f'{ctx.author.mention} resumed the current song.'
						)
						embed.set_author(icon_url=useravatar, name=author)
						await ctx.send(embed=embed)
						return await self.do_resume(ctx)
					else:
						embed = discord.Embed(
								colour=0x57FFF5,
								timestamp=ctx.message.created_at,
								description=f'MrBot is not paused.'
							)
						embed.set_author(icon_url=useravatar, name=author)
						return await ctx.send(embed=embed)
				else:
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'You need to be in the same voice channel as MrBot to use this command.'
					)
					embed.set_author(icon_url=useravatar, name=author)
					return await ctx.send(embed=embed)
			else:
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					description=f'You need to be in the same voice channel as MrBot to use this command.'
				)
				embed.set_author(icon_url=useravatar, name=author)
				await ctx.send(embed=embed)
		else:
			embed = discord.Embed(
				colour=0x57FFF5,
				timestamp=ctx.message.created_at,
				description=f'MrBot is not currently in any voice channels.'
			)
			embed.set_author(icon_url=useravatar, name=author)
			return await ctx.send(embed=embed)

	async def do_resume(self, ctx):
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		await player.set_pause(False)

	@commands.command(name='skip')
	async def skip(self, ctx):
		"""
		Skip to the next song in the queue.
		"""
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		author = ctx.author.name
		useravatar = ctx.author.avatar_url
		if player.is_connected:
			if ctx.author.voice:
				if ctx.author.voice.channel == ctx.guild.me.voice.channel:
					if not len(player.entries) == 0:
						if player.current.requester.id == ctx.author.id:
							embed = discord.Embed(
								colour=0x57FFF5,
								timestamp=ctx.message.created_at,
								description=f'The requester, {ctx.author.mention}, has skipped the song.'
							)
							embed.set_author(icon_url=useravatar, name=author)
							await ctx.send(embed=embed)
							return await self.do_skip(ctx)
						else:
							embed = discord.Embed(
									colour=0x57FFF5,
									timestamp=ctx.message.created_at,
									description=f'Vote skip feature coming soon!'
								)
							embed.set_author(icon_url=useravatar, name=author)
							return await ctx.send(embed=embed)
							# return await self.do_vote(ctx, player, 'skip')
					else:
						embed = discord.Embed(
							colour=0x57FFF5,
							timestamp=ctx.message.created_at,
							description=f'There is nothing in the queue to skip.'
						)
						embed.set_author(icon_url=useravatar, name=author)
						return await ctx.send(embed=embed)
				else:
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'You need to be in the same voice channel as MrBot to use this command.'
					)
					embed.set_author(icon_url=useravatar, name=author)
					return await ctx.send(embed=embed)
			else:
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					description=f'You need to be in the same voice channel as MrBot to use this command.'
				)
				embed.set_author(icon_url=useravatar, name=author)
				await ctx.send(embed=embed)
		else:
			embed = discord.Embed(
				colour=0x57FFF5,
				timestamp=ctx.message.created_at,
				description=f'MrBot is not currently in any voice channels.'
			)
			embed.set_author(icon_url=useravatar, name=author)
			return await ctx.send(embed=embed)

	async def do_skip(self, ctx):
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		await player.stop()

	@commands.command(name='volume', aliases=['vol'])
	async def volume(self, ctx, *, vol: int):
		"""
		Change the volume of the player.
		"""
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		author = ctx.author.name
		useravatar = ctx.author.avatar_url
		if player.is_connected:
			if ctx.author.voice:
				if ctx.author.voice.channel == ctx.guild.me.voice.channel:
					if 0 < vol < 101:
						embed = discord.Embed(
							colour=0x57FFF5,
							timestamp=ctx.message.created_at,
							description=f'{ctx.author.mention} changed the volume to **{vol}%**'
						)
						embed.set_author(icon_url=useravatar, name=author)
						await ctx.send(embed=embed)
						await player.set_volume(vol)
					else:
						embed = discord.Embed(
								colour=0x57FFF5,
								timestamp=ctx.message.created_at,
								description=f'Please enter a number between 1 and 100.'
							)
						embed.set_author(icon_url=useravatar, name=author)
						return await ctx.send(embed=embed)
				else:
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'You need to be in the same voice channel as MrBot to use this command.'
					)
					embed.set_author(icon_url=useravatar, name=author)
					return await ctx.send(embed=embed)
			else:
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					description=f'You need to be in the same voice channel as MrBot to use this command.'
				)
				embed.set_author(icon_url=useravatar, name=author)
				await ctx.send(embed=embed)
		else:
			embed = discord.Embed(
				colour=0x57FFF5,
				timestamp=ctx.message.created_at,
				description=f'MrBot is not currently in any voice channels.'
			)
			embed.set_author(icon_url=useravatar, name=author)
			return await ctx.send(embed=embed)

	@commands.command(name='eq', aliases=['set_eq'])
	async def eq(self, ctx, *, eq: str):
		"""
		Change the equalizer of the player.
		"""
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		author = ctx.author.name
		useravatar = ctx.author.avatar_url
		if player.is_connected:
			if ctx.author.voice:
				if ctx.author.voice.channel == ctx.guild.me.voice.channel:
					if eq.upper() in player.equalizers:
						embed = discord.Embed(
							colour=0x57FFF5,
							timestamp=ctx.message.created_at,
							description=f'{ctx.author.mention} changed the equalizer to **{eq.capitalize()}**'
						)
						embed.set_author(icon_url=useravatar, name=author)
						await ctx.send(embed=embed)
						await player.set_preq(eq)
						player.eq = eq.capitalize()
					else:
						embed = discord.Embed(
								colour=0x57FFF5,
								timestamp=ctx.message.created_at,
								description=f'That was not recognised as a valid equalizer, Try Flat, Boost, Metal or Piano.'
							)
						embed.set_author(icon_url=useravatar, name=author)
						return await ctx.send(embed=embed)
				else:
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'You need to be in the same voice channel as MrBot to use this command.'
					)
					embed.set_author(icon_url=useravatar, name=author)
					return await ctx.send(embed=embed)
			else:
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					description=f'You need to be in the same voice channel as MrBot to use this command.'
				)
				embed.set_author(icon_url=useravatar, name=author)
				await ctx.send(embed=embed)
		else:
			embed = discord.Embed(
				colour=0x57FFF5,
				timestamp=ctx.message.created_at,
				description=f'MrBot is not currently in any voice channels.'
			)
			embed.set_author(icon_url=useravatar, name=author)
			return await ctx.send(embed=embed)

	@commands.command(name='now_playing', aliases=['np'])
	async def now_playing(self, ctx):
		"""
		Display information about the current song.
		"""
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		author = ctx.author.name
		useravatar = ctx.author.avatar_url
		if player.is_connected:
			await player.invoke_controller()
		else:
			embed = discord.Embed(
				colour=0x57FFF5,
				timestamp=ctx.message.created_at,
				description=f'MrBot is not currently playing anything.'
			)
			embed.set_author(icon_url=useravatar, name=author)
			return await ctx.send(embed=embed)

	@commands.command(name='queue', aliases=['q'])
	async def queue(self, ctx):
		"""
		Display a list of upcoming songs.
		"""
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		author = ctx.author.name
		useravatar = ctx.author.avatar_url
		if player.is_connected:
			upcoming = list(itertools.islice(player.entries, 0, 10))
			if not upcoming:
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					description=f'There is nothing in the queue.'
				)
				embed.set_author(icon_url=useravatar, name=author)
				return await ctx.send(embed=embed)
			else:
				fmt = '\n\n'.join(f'**{str(song)}**' for song in upcoming)
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					title=f'Displaying the next {len(upcoming)} entries in the queue. ',
					description=fmt
				)
				embed.set_author(icon_url=useravatar, name=author)
				return await ctx.send(embed=embed)

	@commands.command(name='shuffle')
	async def shuffle(self, ctx):
		"""
		Shuffle the queue.
		"""
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		author = ctx.author.name
		useravatar = ctx.author.avatar_url
		if player.is_connected:
			if ctx.author.voice:
				if ctx.author.voice.channel == ctx.guild.me.voice.channel:
					if not len(player.entries) < 3:
						embed = discord.Embed(
							colour=0x57FFF5,
							timestamp=ctx.message.created_at,
							description=f'{ctx.author.mention} has shuffled the queue.'
						)
						embed.set_author(icon_url=useravatar, name=author)
						await ctx.send(embed=embed)
						return await self.do_shuffle(ctx)
					else:
						embed = discord.Embed(
								colour=0x57FFF5,
								timestamp=ctx.message.created_at,
								description=f'Please add more songs to the queue.'
							)
						embed.set_author(icon_url=useravatar, name=author)
						return await ctx.send(embed=embed)
				else:
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'You need to be in the same voice channel as MrBot to use this command.'
					)
					embed.set_author(icon_url=useravatar, name=author)
					return await ctx.send(embed=embed)
			else:
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					description=f'You need to be in the same voice channel as MrBot to use this command.'
				)
				embed.set_author(icon_url=useravatar, name=author)
				await ctx.send(embed=embed)
		else:
			embed = discord.Embed(
				colour=0x57FFF5,
				timestamp=ctx.message.created_at,
				description=f'MrBot is not currently in any voice channels.'
			)
			embed.set_author(icon_url=useravatar, name=author)
			return await ctx.send(embed=embed)

	async def do_shuffle(self, ctx):
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		random.shuffle(player.queue._queue)
		player.update = True

	@commands.command(name='repeat', aliases=['loop'])
	async def repeat(self, ctx):
		"""
		Repeat the queue once.
		"""
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		author = ctx.author.name
		useravatar = ctx.author.avatar_url
		if player.is_connected:
			if ctx.author.voice:
				if ctx.author.voice.channel == ctx.guild.me.voice.channel:
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'{ctx.author.mention} has looped/repeated the queue.'
					)
					embed.set_author(icon_url=useravatar, name=author)
					await ctx.send(embed=embed)
					return await self.do_repeat(ctx)
				else:
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'You need to be in the same voice channel as MrBot to use this command.'
					)
					embed.set_author(icon_url=useravatar, name=author)
					return await ctx.send(embed=embed)
			else:
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					description=f'You need to be in the same voice channel as MrBot to use this command.'
				)
				embed.set_author(icon_url=useravatar, name=author)
				await ctx.send(embed=embed)
		else:
			embed = discord.Embed(
				colour=0x57FFF5,
				timestamp=ctx.message.created_at,
				description=f'MrBot is not currently in any voice channels.'
			)
			embed.set_author(icon_url=useravatar, name=author)
			return await ctx.send(embed=embed)

	async def do_repeat(self, ctx):
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		if not player.entries:
			await player.queue.put(player.current)
		else:
			player.queue._queue.appendleft(player.current)
		player.update = True

	@commands.command(name='node_info')
	async def node_info(self, ctx):
		"""Retrieve various Node/Server/Player information."""
		player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
		node = player.node

		used = humanize.naturalsize(node.stats.memory_used)
		total = humanize.naturalsize(node.stats.memory_allocated)
		free = humanize.naturalsize(node.stats.memory_free)
		cpu = node.stats.cpu_cores

		fmt = f'**WaveLink:** `{wavelink.__version__}`\n\n' \
			f'Connected to `{len(self.bot.wavelink.nodes)}` nodes.\n' \
			f'Best available Node `{self.bot.wavelink.get_best_node().__repr__()}`\n' \
			f'`{len(self.bot.wavelink.players)}` players are distributed on nodes.\n' \
			f'`{node.stats.players}` players are distributed on server.\n' \
			f'`{node.stats.playing_players}` players are playing on server.\n\n' \
			f'Server Memory: `{used}/{total}` | `({free} free)`\n' \
			f'Server CPU: `{cpu}`\n\n' \
			f'Server Uptime: `{datetime.timedelta(milliseconds=node.stats.uptime)}`'
		await ctx.send(fmt)


def setup(bot):
	bot.add_cog(Voice(bot))