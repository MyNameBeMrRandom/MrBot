from discord.ext import commands
from .utils import calculations
import collections
import itertools
import andesite
import asyncio
import discord
import config
import random

class Queue:

	def __init__(self, maxsize=0, *, loop=None):
		if loop is None:
			self._loop = asyncio.events.get_event_loop()
		else:
			self._loop = loop
		self._maxsize = maxsize

		# Futures.
		self._getters = collections.deque()
		# Futures.
		self._putters = collections.deque()
		self._unfinished_tasks = 0
		self._finished = asyncio.locks.Event(loop=self._loop)
		self._finished.set()
		self.queue = []

	def _wakeup_next(self, waiters):
		# Wake up the next waiter (if any) that isn't cancelled.
		while waiters:
			waiter = waiters.popleft()
			if not waiter.done():
				waiter.set_result(None)
				break

	def __repr__(self):
		return f'<{type(self).__name__} at {id(self):#x} {self._format()}>'

	def __str__(self):
		return f'<{type(self).__name__} {self._format()}>'

	def _format(self):
		result = f'maxsize={self._maxsize!r}'
		if getattr(self, '_queue', None):
			result += f' _queue={list(self.queue)!r}'
		if self._getters:
			result += f' _getters[{len(self._getters)}]'
		if self._putters:
			result += f' _putters[{len(self._putters)}]'
		if self._unfinished_tasks:
			result += f' tasks={self._unfinished_tasks}'
		return result

	@property
	def maxsize(self):
		"""Number of items allowed in the queue."""
		return self._maxsize

	def empty(self):
		"""Return True if the queue is empty, False otherwise."""
		return not self.queue

	def full(self):
		"""Return True if there are maxsize items in the queue.

		Note: if the Queue was initialized with maxsize=0 (the default),
		then full() is never True.
		"""
		if self._maxsize <= 0:
			return False
		else:
			return self.qsize() >= self._maxsize

	def task_done(self):
		"""Indicate that a formerly enqueued task is complete.

		Used by queue consumers. For each get() used to fetch a task,
		a subsequent call to task_done() tells the queue that the processing
		on the task is complete.

		If a join() is currently blocking, it will resume when all items have
		been processed (meaning that a task_done() call was received for every
		item that had been put() into the queue).

		Raises ValueError if called more times than there were items placed in
		the queue.
		"""
		if self._unfinished_tasks <= 0:
			raise ValueError('task_done() called too many times')
		self._unfinished_tasks -= 1
		if self._unfinished_tasks == 0:
			self._finished.set()

	def qsize(self):
		"""Number of items in the queue."""
		return len(self.queue)

	async def put(self, item):
		"""Put an item into the queue.

		Put an item into the queue. If the queue is full, wait until a free
		slot is available before adding item.
		"""
		while self.full():
			putter = self._loop.create_future()
			self._putters.append(putter)
			try:
				await putter
			except:
				putter.cancel()  # Just in case putter is not done yet.
				try:
					# Clean self._putters from canceled putters.
					self._putters.remove(putter)
				except ValueError:
					# The putter could be removed from self._putters by a
					# previous get_nowait call.
					pass
				if not self.full() and not putter.cancelled():
					# We were woken up by get_nowait(), but can't take
					# the call.  Wake up the next in line.
					self._wakeup_next(self._putters)
				raise
		self._unfinished_tasks += 1
		self._finished.clear()
		self._wakeup_next(self._getters)
		return self.queue.append(item)

	async def put_pos(self, item, pos):
		"""Put an item into the queue.

		Put an item into the queue. If the queue is full, wait until a free
		slot is available before adding item.
		"""
		while self.full():
			putter = self._loop.create_future()
			self._putters.append(putter)
			try:
				await putter
			except:
				putter.cancel()  # Just in case putter is not done yet.
				try:
					# Clean self._putters from canceled putters.
					self._putters.remove(putter)
				except ValueError:
					# The putter could be removed from self._putters by a
					# previous get_nowait call.
					pass
				if not self.full() and not putter.cancelled():
					# We were woken up by get_nowait(), but can't take
					# the call.  Wake up the next in line.
					self._wakeup_next(self._putters)
				raise
		self._unfinished_tasks += 1
		self._finished.clear()
		self._wakeup_next(self._getters)
		return self.queue.insert(pos, item)

	async def get(self):
		"""Remove and return an item from the queue.

		If queue is empty, wait until an item is available.
		"""
		while self.empty():
			getter = self._loop.create_future()
			self._getters.append(getter)
			try:
				await getter
			except:
				getter.cancel()  # Just in case getter is not done yet.
				try:
					# Clean self._getters from canceled getters.
					self._getters.remove(getter)
				except ValueError:
					# The getter could be removed from self._getters by a
					# previous put_nowait call.
					pass
				if not self.empty() and not getter.cancelled():
					# We were woken up by put_nowait(), but can't take
					# the call.  Wake up the next in line.
					self._wakeup_next(self._getters)
				raise
		item = self.queue.pop(0)
		self._wakeup_next(self._putters)
		return item

	async def get_pos(self, pos):
		"""Remove and return an item from the queue.

		If queue is empty, wait until an item is available.
		"""
		while self.empty():
			getter = self._loop.create_future()
			self._getters.append(getter)
			try:
				await getter
			except:
				getter.cancel()  # Just in case getter is not done yet.
				try:
					# Clean self._getters from canceled getters.
					self._getters.remove(getter)
				except ValueError:
					# The getter could be removed from self._getters by a
					# previous put_nowait call.
					pass
				if not self.empty() and not getter.cancelled():
					# We were woken up by put_nowait(), but can't take
					# the call.  Wake up the next in line.
					self._wakeup_next(self._getters)
				raise
		item = self.queue.pop(pos)
		self._wakeup_next(self._putters)
		return item


class Track(andesite.Track):

	def __init__(self, id_, info, *, ctx=None):
		super(Track, self).__init__(id_, info)
		self.channel = ctx.channel
		self.requester = ctx.author


class Player(andesite.Player):

	def __init__(self, bot, guild_id: int, node):
		super(Player, self).__init__(bot, guild_id, node)
		self.bot.loop.create_task(self.player_loop())
		self.queue = Queue()
		self.loop_queue = False
		self.paused = False
		self.filter = None
		self.volume = 50

	async def player_loop(self):
		await self.bot.wait_until_ready()
		await self.set_volume(self.volume)
		while True:
			song = await self.queue.get()
			if not song:
				continue
			self.current = song
			await self.play(song)
			await self.invoke_controller()
			await self.bot.wait_for("andesite_track_end", check=lambda p: p.player.guild_id == self.guild_id)
			if self.loop_queue is True:
				await self.queue.put(self.current)
			self.current = None

	async def invoke_controller(self, track: andesite.Track = None):
		if not track:
			track = self.current
		embed = discord.Embed(title='Music controller:', colour=0x57FFF5)
		embed.set_thumbnail(url=f'https://img.youtube.com/vi/{track.yt_id}/hqdefault.jpg')
		embed.add_field(name=f'Now playing:', value=f'**[{track.title}]({track.uri})**', inline=False)
		if track.is_stream:
			embed.add_field(name='Time:', value='`Live stream`')
		else:
			embed.add_field(name='Time:', value=f'`{calculations.get_time(self.last_position / 1000)}` / `{calculations.get_time(track.length / 1000)}`')
		embed.add_field(name='Volume:', value=f'`{self.volume}%`')
		embed.add_field(name='Queue Length:', value=f'`{str(self.queue.qsize())}`')
		embed.add_field(name='Queue looped:', value=f'`{self.loop_queue}`')
		embed.add_field(name='Requester:', value=track.requester.mention)
		# embed.add_field(name=f'Filter:', value=f'Current: {self.filter}')
		await track.channel.send(embed=embed)


# noinspection PyAttributeOutsideInit
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
			await self.andesite.start_node(
				n['ip'],
				n['port'],
				rest_uri=n['rest_uri'],
				password=n['password'],
				identifier=n['identifier']
				)

	@commands.command(name='play')
	async def play(self, ctx, *, search: str):
		"""
		Plays a song using a link or search query.

		`search` will default to a Youtube search however it also accepts links from SoundCloud and Twitch.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)

		try:
			await self.do_join(ctx, player, ctx.author.voice.channel)
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

	@commands.command(name='now_playing', aliases=['np'])
	async def now_playing(self, ctx):
		"""
		Display information about the current song/queue status.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)

		if player.is_connected:
			if not player.current:
				return await ctx.send('No video/songs currently playing.')
			await player.invoke_controller()
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	# TODO: Add equalizer support when granitepy starts supporting it.
	@commands.command(name='eq', enabled=False)
	async def eq(self, ctx):
		"""
		Change the equalizer of the player.
		"""
		return await ctx.send('Waiting on library updates to make this work.')

	@commands.command(name='join', aliases=['connect'])
	async def join(self, ctx):
		"""
		Joins or moves to the users voice channel.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)

		try:
			channel = ctx.author.voice.channel
		except AttributeError:
			return await ctx.send('Join a voice channel to use this command.')

		if player.is_connected:
			if ctx.guild.me.voice.channel.id == channel.id:
				return await ctx.send('I am already in this voice channel.')
			await self.do_join(ctx, player, channel)
			return await ctx.send(f'Moved to the voice channel `{channel}`')
		else:
			await self.do_join(ctx, player, channel)
			return await ctx.send(f'Joined the voice channel `{channel}`')

	async def do_join(self, ctx, player, channel):
		"""
		Join a voice channel.
		"""
		permissions = ctx.author.voice.channel.permissions_for(ctx.me)
		if not permissions.connect:
			raise commands.BotMissingPermissions(['Voice: Connect'])
		if not permissions.speak:
			raise commands.BotMissingPermissions(['Voice: Speak'])
		await player.connect(channel.id)

	@commands.command(name='leave', aliases=['disconnect', 'stop'])
	async def leave(self, ctx):
		"""
		Leaves the current voice channel.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			await self.do_leave(player)
			return await ctx.send(f'Left the voice channel `{ctx.guild.me.voice.channel}`.')
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_leave(self, player):
		"""
		Leave a voice channel.
		"""
		await player.disconnect()
		await player.destroy()

	@commands.command(name='pause')
	async def pause(self, ctx):
		"""
		Pauses the current song.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)

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
		"""
		Pause the current track.
		"""

		self.paused = True
		await player.set_pause(True)

	@commands.command(name='resume')
	async def resume(self, ctx):
		"""
		Resumes the current song.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)

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
		"""
		Resumes the player
		"""

		self.paused = False
		await player.set_pause(False)

	@commands.command(name='skip')
	async def skip(self, ctx):
		"""
		Skip to the next song in the queue.

		This will auto skip if you are the requester of the current songs, otherwise a vote will start to skip the song.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if player.queue.qsize() <= 0:
				return await ctx.send('There are no songs in the queue to skip too.')
			if player.current.requester.id == ctx.author.id:
				await ctx.send(f"The current song's requester has skipped the song.")
				return await self.do_skip(player)
			else:
				await ctx.send('Vote skipping coming soon.')
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_skip(self, player):
		"""
		Skip the current track
		"""

		await player.stop()

	@commands.command(name='volume', aliases=['vol'])
	async def volume(self, ctx, volume: int):
		"""
		Changes the volume of the player.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)

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
		"""
		Changes the volume of the player.
		"""

		await player.set_volume(volume)
		player.volume = volume

	@commands.command(name='filter')
	async def filter(self, ctx):
		"""
		Changes the volume of the player.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)

		def check(msg):
			return ctx.author == msg.author and ctx.channel == msg.channel

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')

			message = await ctx.send(f'What filter type would you like to use?\n> 1. Karaoke\n> 2. Timescale\n> 3. Tremolo\n> 4. Vibrato\nEnter number:')
			try:
				filter_type = await ctx.bot.wait_for('message', timeout=30.0, check=check)
				if filter_type.content == 'cancel':
					return await ctx.send('Ended filter selection.')
				filter_type = int(filter_type.content)
				if filter_type <= 0 or filter_type >= 5:
					return await ctx.send(f'That is not a valid filter, please choose a valid filters number.')
			except asyncio.TimeoutError:
				return await ctx.send(f'You took to long to respond.')
			except ValueError:
				return await ctx.send(f'That was not a valid filter type, make sure you use a number.')
			if filter_type == 1:
				await message.edit(content=f'What `level` would you like?')
				try:
					filter_type = await ctx.bot.wait_for('message', timeout=30.0, check=check)
					if filter_type.content == 'cancel':
						return await ctx.send('Ended filter selection.')
					filter_type = int(filter_type.content)
					if filter_type <= 0 or filter_type >= 20:
						return await ctx.send(f'That is not a valid `level`, please choose a valid filters number.')
				except asyncio.TimeoutError:
					return await ctx.send(f'You took to long to respond.')
				except ValueError:
					return await ctx.send(f'That was not a valid filter type, make sure you use a number.')





			#if not 0 < volume < 101:
				#return await ctx.send(f'Please enter a value between `1` and and `100`.')
			#await ctx.send(f'Changed the players volume to `{volume}%`.')
			return await self.do_filter(player, filters)
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_filter(self, player, filters):
		"""
		Changes the volume of the player.
		"""
		await player.set_filters(filters)

	@commands.command(name='seek')
	async def seek(self, ctx, position: int):
		"""
		Changes the postion of the player.

		`position` can be the time you want to skip to in seconds.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)
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
			if not player.current.is_seekable:
				return await ctx.send('This track is not seekable.')
			if not 0 <= milliseconds <= player.current.length:
				return await ctx.send(f'Please enter a value between `1` and and `{round(player.current.length / 1000)}`.')
			await self.do_seek(player, milliseconds)
			return await ctx.send(f'Changed the players position to `{calculations.get_time(milliseconds / 1000)}`.')
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_seek(self, player, milliseconds):
		"""
		Seek to a postion in a track.
		"""

		await player.seek(milliseconds)

	@commands.command(name='queue')
	async def queue(self, ctx):
		"""
		Display a list of the current queue.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)

		if player.is_connected:
			upcoming = list(itertools.islice(player.queue.queue, 0, 15))
			if player.queue.qsize() <= 0:
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
					title=f'Displaying the next **{len(upcoming)}** out of **{player.queue.qsize()}** entries in the queue.',
					description=message
				)
				return await ctx.send(embed=embed)
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	@commands.command(name='shuffle')
	async def shuffle(self, ctx):
		"""
		Shuffle the queue.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if player.queue.qsize() <= 0:
				return await ctx.send('Add videos/songs to the queue to enable queue shuffling.')
			await self.do_shuffle(player)
			return await ctx.send(f'The queue has been shuffled.')
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_shuffle(self, player):
		"""
		Shuffle the queue.
		"""
		random.shuffle(player.queue.queue)

	@commands.command(name='clear')
	async def clear(self, ctx):
		"""
		Clear the queue of all entries.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if player.queue.qsize() <= 0:
				return await ctx.send('Add videos/songs to the queue to enable queue clearing.')
			await self.do_clear(player)
			return await ctx.send(f'Cleared the queue.')
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_clear(self, player):
		"""
		Clear the queue.
		"""
		player.queue.queue.clear()

	@commands.command(name='loop')
	async def loop(self, ctx):
		"""
		Loop the queue.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if player.queue.qsize() <= 0:
				return await ctx.send('Add videos/songs to the queue to enable queue looping.')
			await self.do_loop(player)
			if player.loop_queue is True:
				return await ctx.send(f'The queue will now loop.')
			else:
				return await ctx.send(f'The queue will stop looping.')
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_loop(self, player):
		"""
		Loop the queue.
		"""

		if player.loop_queue is False:
			player.loop_queue = True
		else:
			player.loop_queue = False

	@commands.command(name='remove')
	async def remove(self, ctx, entry: int):
		"""
		Remove an entry from the queue.

		When removing entries use the number shown in the `queue` command. For example `mb remove  13` will remove the track in 13th position.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if player.queue.qsize() <= 0:
				return await ctx.send('Add videos/songs to the queue to enable queue entry removing.')
			if not 0 < entry <= player.queue.qsize():
				return await ctx.send(f'That was not a valid track entry number.')
			item = await self.do_remove(player, entry)
			return await ctx.send(f'Removed `{item}` from the queue.')
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_remove(self, player, entry):
		item = await player.queue.get_pos(entry - 1)
		return item

	@commands.command(name='move')
	async def move(self, ctx, entry_1: int, entry_2: int):
		"""
		Move an entry from one position to another in the queue.

		When moving entries use the number shown in the `queue` command. For example `mb move 1 15` will move the track in 1st position to 15th.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if player.queue.qsize() <= 0:
				return await ctx.send('Add videos/songs to the queue to enable queue entry moving.')
			if not 0 < entry_1 <= player.queue.qsize():
				return await ctx.send(f'That was not a valid track entry to move from.')
			if not 0 < entry_2 <= player.queue.qsize():
				return await ctx.send(f'That was not a valid track entry to move too.')
			item = await self.do_move(ctx, player, entry_1, entry_2)
			return await ctx.send(f'Moved `{item}` from position `{entry_1}` to position `{entry_2}`.')
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_move(self, ctx, player, entry_1, entry_2):
		item = await player.queue.get_pos(entry_1 - 1)
		tracks = await player.node.get_tracks(f"{item}")
		track = tracks[0]
		await player.queue.put_pos(Track(track.id, track.data, ctx=ctx), entry_2 - 1)
		return item

	@commands.command(name='reverse')
	async def reverse(self, ctx):
		"""
		Remove an entry from the queue.
		"""

		player = self.andesite.get_player(ctx.guild.id, cls=Player)

		if player.is_connected:
			try:
				channel = ctx.author.voice.channel
			except AttributeError:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if not channel == ctx.guild.me.voice.channel:
				return await ctx.send(f'Join the same voice channel as MrBot to use this command.')
			if player.queue.qsize() <= 0:
				return await ctx.send('Add videos/songs to the queue to enable queue reversing.')
			await self.do_reverse(player)
			return await ctx.send(f'Reversed the queue.')
		else:
			return await ctx.send(f'MrBot is not currently in any voice channels.')

	async def do_reverse(self, player):
		return player.queue.queue.reverse()


def setup(bot):
	bot.add_cog(Voice(bot))

