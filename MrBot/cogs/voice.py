from discord.ext import commands
import itertools
import andesite
import asyncio
import discord
import config
import random


class Track(andesite.Track):

	def __init__(self, id_, info, *, ctx=None):
		super(Track, self).__init__(id_, info)

		self.channel = ctx.channel
		self.requester = ctx.author


class Player(andesite.Player):

	def __init__(self, bot, guild_id: int, node):
		super(Player, self).__init__(bot, guild_id, node)
		self.filter = andesite.Timescale(speed=1, pitch=1000, rate=1)
		self.bot.loop.create_task(self.player_loop())
		self.next_event = asyncio.Event()
		self.queue = asyncio.Queue()
		self.volume = 50
		self.paused = False
		self.bot.loop_queue = False

	def get_time(self, second):
		minute, second = divmod(second, 60)
		hour, minute = divmod(minute, 60)
		hours = round(hour)
		minutes = round(minute)
		seconds = round(second)
		message = ""
		if not hours == 0:
			if hours < 10:
				message += f'0{hours}:'
			else:
				message += f'{hours}:'
		else:
			message += '00:'
		if not minutes == 0:
			if minutes < 10:
				message += f'0{minutes}:'
			else:
				message += f'{minutes}:'
		else:
			message += '00:'
		if not seconds == 0:
			if seconds < 10:
				message += f'0{seconds}'
			else:
				message += f'{seconds}'
		else:
			message += '00'
		return message

	async def player_loop(self):
		await self.bot.wait_until_ready()
		await self.set_volume(self.volume)
		await self.set_filters(self.filter)
		while True:
			self.next_event.clear()
			song = await self.queue.get()
			if not song:
				continue
			self.current = song
			await self.play(song)
			await self.invoke_controller()
			await self.bot.wait_for("andesite_track_end", check=lambda p: p.player.guild_id == self.guild_id)
			if self.bot.loop_queue is True:
				await self.queue.put(self.current)

	async def invoke_controller(self, track: andesite.Track = None):
		if not track:
			track = self.current
		embed = discord.Embed(title='Music controller:', colour=0x57FFF5)
		embed.set_thumbnail(url=f'https://img.youtube.com/vi/{track.yt_id}/hqdefault.jpg')
		embed.add_field(name=f'Now playing:', value=f'**[{track.title}]({track.uri})**', inline=False)
		if track.is_stream:
			embed.add_field(name='Time:', value='`Live stream`')
		else:
			embed.add_field(name='Time:', value=f'`{self.get_time(self.last_position / 1000)}` / `{self.get_time(track.length / 1000)}`')
		embed.add_field(name='Volume:', value=f'`{self.volume}%`')
		embed.add_field(name='Queue Length:', value=f'`{str(len(self.queue._queue))}`')
		embed.add_field(name='Queue looped:', value=f'`{self.bot.loop_queue}`')
		embed.add_field(name='Requester:', value=track.requester.mention)
		# embed.add_field(name=f'Filter:', value=f'Current: {self.filter}')
		await track.channel.send(embed=embed)


class Voice(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.andesite = andesite.Client(bot)
		bot.loop.create_task(self.initiate_nodes())

	async def initiate_nodes(self):
		nodes = {'MAIN_NODE': { 'ip': config.IP_1,
		                        'port': config.PORT_1,
		                        'rest_uri': config.ADRESS_1,
		                        'password': config.PASSWORD_1,
		                        'identifier': "Node_1",
		                        }
		         }

		for n in nodes.values():
			node = await self.andesite.start_node(
				n['ip'],
				n['port'],
				rest_uri=n['rest_uri'],
				password=n['password'],
				identifier=n['identifier']
				)

	def get_time(self, second):
		minute, second = divmod(second, 60)
		hour, minute = divmod(minute, 60)
		hours = round(hour)
		minutes = round(minute)
		seconds = round(second)
		message = ""
		if not hours == 0:
			if hours < 10:
				message += f'0{hours}:'
			else:
				message += f'{hours}:'
		else:
			message += '00:'
		if not minutes == 0:
			if minutes < 10:
				message += f'0{minutes}:'
			else:
				message += f'{minutes}:'
		else:
			message += '00:'
		if not seconds == 0:
			if seconds < 10:
				message += f'0{seconds}'
			else:
				message += f'{seconds}'
		else:
			message += '00'
		return message

	@commands.command(name='now_playing', aliases=['np'])
	async def now_playing(self, ctx):
		"""
		Display information about the current song/queue status.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)
		useravatar = ctx.author.avatar_url
		author = ctx.author.name

		if player.is_connected:
			if not player.current:
				return await ctx.send('No video/songs currently playing.')
			await player.invoke_controller()
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	@commands.command(name='play')
	async def play(self, ctx, *, search: str):
		"""
		Plays a song using a link or search query.

		`search` will default to a Youtube search however it also accepts links from SoundCloud and Twitch.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)
		useravatar = ctx.author.avatar_url
		author = ctx.author.name

		try:
			await self.do_join(player, ctx.author.voice.channel)
		except AttributeError:
			return await ctx.send(f'You must be in a voice channel to use this command.')

		if not player.is_connected:
			return await ctx.send(f'Something went wrong! You should not see this.')

		await ctx.trigger_typing()
		tracks = await player.node.get_tracks(f"{search}")
		if not tracks:
			return await ctx.send(f'No results were found for the search term `{search}`.')

		if isinstance(tracks, andesite.Playlist):
			for t in tracks.tracks:
				await player.queue.put(Track(t.id, t.data, ctx=ctx))
			await ctx.send(f'Added the playlist **{tracks.name}** to the queue with a total of **{len(tracks.tracks)}** entries.')
		else:
			track = tracks[0]
			await player.queue.put(Track(track.id, track.data, ctx=ctx))
			await ctx.send(f'Added the video **{track.title}** to the queue.')

	@commands.command(name='join', aliases=['connect'])
	async def join(self, ctx):
		"""
		Joins or moves to the users voice channel.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)
		useravatar = ctx.author.avatar_url
		author = ctx.author.name

		try:
			channel = ctx.author.voice.channel
		except AttributeError:
			return await ctx.send('Join the same voice channel as MrBot to use this command.')

		if player.is_connected:
			if ctx.guild.me.voice.channel.id == channel.id:
				return await ctx.send('I am already in that voice channel.')
			await self.do_join(player, channel)
			return await ctx.send(f'MrBot moved to the voice channel `{channel}`')
		else:
			await self.do_join(player, channel)
			return await ctx.send(f'MrBot joined the voice channel `{channel}`')

	async def do_join(self, player, channel):
		await player.connect(channel.id)

	@commands.command(name='leave', aliases=['disconnect', 'stop'])
	async def leave(self, ctx):
		"""
		Leaves the current voice channel.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)
		useravatar = ctx.author.avatar_url
		author = ctx.author.name

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			await ctx.send(f'Left the voice channel `{ctx.guild.me.voice.channel}`.')
			return await self.do_leave(player)
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_leave(self, player):
		await player.disconnect()
		await player.destroy()

	@commands.command(name='pause')
	async def pause(self, ctx):
		"""
		Pauses the current song.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)
		useravatar = ctx.author.avatar_url
		author = ctx.author.name

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not player.current:
				return await ctx.send('No songs/videos currently playing.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not player.paused:
				await ctx.send(f'Paused the current video/song.')
				return await self.do_pause(player)
			else:
				return await ctx.send('The video/song is already paused.')
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_pause(self, player):
		await player.set_pause(True)

	@commands.command(name='resume')
	async def resume(self, ctx):
		"""
		Resumes the current song.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)
		useravatar = ctx.author.avatar_url
		author = ctx.author.name

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not player.current:
				return await ctx.send('No songs/videos currently playing.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if player.paused:
				await ctx.send(f'Resumed playback of the current video/song.')
				return await self.do_resume(player)
			else:
				return await ctx.send('The video/song is not paused.')
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_resume(self, player):
		self.paused = False
		await player.set_pause(False)

	@commands.command(name='skip')
	async def skip(self, ctx):
		"""
		Skip to the next song in the queue.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)
		useravatar = ctx.author.avatar_url
		author = ctx.author.name

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not player.current:
				return await ctx.send('No songs/videos currently playing.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if player.current.requester.id == ctx.author.id:
				await ctx.send(f'The requester of the current song has skipped the song.')
				return await self.do_skip(player)
			else:
				await ctx.send('Vote skipping coming soon.')
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_skip(self, player):
		await player.stop()

	@commands.command(name='volume', aliases=['vol'])
	async def volume(self, ctx, volume: int):
		"""
		Changes the volume of the player.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)
		useravatar = ctx.author.avatar_url
		author = ctx.author.name

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not 0 < volume < 101:
				return await ctx.send(f'Please enter a value between `1` and and `100`.')
			await ctx.send(f'Changed the players volume to `{volume}%`.')
			return await self.do_volume(player, volume)
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_volume(self, player, volume):
		await player.set_volume(volume)
		player.volume = volume

	@commands.command(name='seek')
	async def seek(self, ctx, position: int):
		"""
		Changes the postion of the player.

		`position` can be the time you want to skip to in seconds.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)
		useravatar = ctx.author.avatar_url
		author = ctx.author.name

		milliseconds = position * 1000

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not player.current:
				return await ctx.send('No songs/videos currently playing.')
			if not 0 <= milliseconds <= player.current.length:
				return await ctx.send(f'Please enter a value between `1` and and `{round(player.current.length / 1000)}`.')
			await self.do_seek(player, milliseconds)
			return await ctx.send(f'Changed the players position to `{self.get_time(milliseconds / 1000)}`.')
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_seek(self, player, milliseconds):
		await player.seek(milliseconds)


	# @commands.command(name='eq', aliases=['set_eq'])
	# async def eq(self, ctx):
	#   """
	#   Change the equalizer of the player.
	#   """
	#   return await ctx.send('Waiting on lib updates to make this work.')

	@commands.group(name='queue', aliases=['q'], invoke_without_command=True)
	async def queue(self, ctx):
		"""
		Display a list of the current queue.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)
		useravatar = ctx.author.avatar_url
		author = ctx.author.name

		if player.is_connected:
			upcoming = list(itertools.islice(player.queue._queue, 0, 15))
			if not upcoming:
				return await ctx.send('The queue is empty.')
			else:
				message = ""
				counter = 1
				for track in upcoming:
					message += f'**{counter}.** {str(track)}\n'
					counter += 1
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					title=f'Displaying the next **{len(upcoming)}** out of **{len(player.queue._queue)}** entries in the queue.',
					description=message
				)
				embed.set_author(icon_url=useravatar, name=author)
				return await ctx.send(embed=embed)

	@queue.command(name='shuffle')
	async def shuffle(self, ctx):
		"""
		Shuffle the queue.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)
		useravatar = ctx.author.avatar_url
		author = ctx.author.name

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if len(player.queue._queue) <= 1:
				return await ctx.send('Add videos/songs to the queue to enable queue shuffling.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			await self.do_shuffle(player)
			return await ctx.send(f'The queue has been shuffled.')
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_shuffle(self, player):
		random.shuffle(player.queue._queue)

	@queue.command(name='loop')
	async def loop(self, ctx):
		"""
		Loop the queue.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)
		useravatar = ctx.author.avatar_url
		author = ctx.author.name

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not player.current and not player.queue._queue:
				return await ctx.send('Add videos/songs to the queue to enable queue looping.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			await self.do_loop()
			if self.bot.loop_queue is True:
				return await ctx.send(f'The queue will now loop.')
			else:
				return await ctx.send(f'The queue will stop looping.')
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_loop(self):
		if self.bot.loop_queue is False:
			self.bot.loop_queue = True
		else:
			self.bot.loop_queue = False

	@queue.command(name='clear')
	async def clear(self, ctx):
		"""
		Clear the queue of all entries.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)
		useravatar = ctx.author.avatar_url
		author = ctx.author.name

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not player.current and not player.queue._queue:
				return await ctx.send('Add videos/songs to the queue to enable queue clearing.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			await self.do_clear(player)
			return await ctx.send(f'Cleared the queue.')
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_clear(self, player):
		player.queue._queue.clear()

	"""
	@queue.command(name='remove')
	async def remove(self, ctx, entry: int):
	
	
		Remove an entry from the queue.


		player = self.andesite.get_player(ctx.guild.id, cls=Player)
		useravatar = ctx.author.avatar_url
		author = ctx.author.name

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not player.current and not player.queue._queue:
				return await ctx.send('Add videos/songs to the queue to enable queue entry removing.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			await self.do_remove(player, entry)
			return await ctx.send(f'Cleared the queue.')
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_remove(self, player, entry):
		player.queue.pop(entry)
	"""


def setup(bot):
	bot.add_cog(Voice(bot))

