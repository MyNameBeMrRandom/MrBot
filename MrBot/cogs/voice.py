from discord.ext import commands
from youtube_dl import YoutubeDL
from .utils import calculations
import collections
import itertools
import andesite
import asyncio
import discord
import config
import random
import os

from discord.ext.commands.cooldowns import BucketType
from discord.opus import Decoder
import speech_recognition as sr
import typing
import wave
import copy
import io

ytdlopts = {
    'format': 'bestaudio',
    'outtmpl': 'audio/%(id)s.%(ext)s',
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'postprocessors':
        [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }
        ],
}
ytdl = YoutubeDL(ytdlopts)


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
        self.loop_queue = False
        self.queue = Queue()
        self.paused = False
        self.volume = 50

        self.filter_count = 0
        self.nightcore = False

    async def player_loop(self):
        await self.bot.wait_until_ready()
        await self.set_volume(self.volume)
        await self.set_pause(False)
        await self.set_karaoke()
        await self.set_timescale()
        await self.set_tremolo()
        await self.set_vibrato()
        self.paused = False
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

    async def invoke_controller(self):
        track = self.current
        embed = discord.Embed(title='Music controller:', colour=0x57FFF5)
        embed.set_thumbnail(url=f'https://img.youtube.com/vi/{track.yt_id}/hqdefault.jpg')
        embed.add_field(name=f'Now playing:', value=f'**[{track.title}]({track.uri})**', inline=False)
        if track.is_stream:
            embed.add_field(name='Time:', value='`Live stream`')
        else:
            embed.add_field(name='Time:', value=f'`{calculations.get_time(round(self.position) / 1000)}` / `{calculations.get_time(track.length / 1000)}`')
        embed.add_field(name='Volume:', value=f'`{self.volume}%`')
        embed.add_field(name='Queue Length:', value=f'`{str(self.queue.qsize())}`')
        embed.add_field(name='Queue looped:', value=f'`{self.loop_queue}`')
        embed.add_field(name='Requester:', value=track.requester.mention)
        # embed.add_field(name=f'Filter:', value=f'Current: {self.filter}')
        await track.channel.send(embed=embed)

class MySink(discord.AudioSink):

    def __init__(self, destination):

        self.destination = destination
        self.file = wave.open(destination, 'wb')
        self.file.setnchannels(Decoder.CHANNELS)
        self.file.setsampwidth(Decoder.SAMPLE_SIZE//Decoder.CHANNELS)
        self.file.setframerate(Decoder.SAMPLING_RATE)

    def write(self, data):
        self.file.writeframes(data.data)

    def cleanup(self):
        self.file.close()

class Voice(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.andesite = andesite.Client(bot)
        self.bot.loop.create_task(self.initiate_nodes())
        self.listen = False

    async def initiate_nodes(self):

        nodes = {'Node_1': {'ip': config.IP_1,
                            'port': config.PORT_1,
                            'rest_uri': config.ADRESS_1,
                            'password': config.PASSWORD_1,
                            'identifier': "Node_1",
                            }
                 }

        for n in nodes.values():
            try:
                await self.bot.andesite.start_node(
                    n['ip'],
                    n['port'],
                    rest_uri=n['rest_uri'],
                    password=n['password'],
                    identifier=n['identifier']
                )
            except Exception:
                print('[ANDESITE] Nodes failed to connect.')
            print('[ANDESITE] Nodes connected.')

    @commands.command(name='play')
    async def play(self, ctx, *, search: str):
        """
        Plays a song using a link or search query.

        `search`: will default to a Youtube search however it also accepts links from SoundCloud and Twitch.
        """

        if not ctx.player.is_connected:
            try:
                await self.do_join(ctx, ctx.author.voice.channel.id)
            except AttributeError:
                return await ctx.send(f'You must be in a voice channel to use this command.')

        await ctx.trigger_typing()
        tracks = await ctx.player.node.get_tracks(f"{search}")
        if not tracks:
            return await ctx.send(f'No results were found for the search term `{search}`.')
        if isinstance(tracks, andesite.Playlist):
            for track in tracks.tracks:
                await ctx.player.queue.put(Track(track.id, track.data, ctx=ctx))
            return await ctx.send(f'Added the playlist **{tracks.name}** to the queue with a total of **{len(tracks.tracks)}** entries.')
        track = tracks[0]
        await ctx.player.queue.put(Track(track.id, track.data, ctx=ctx))
        return await ctx.send(f'Added the track **{track.title}** to the queue.')

    @commands.command(name='join', aliases=['connect'])
    async def join(self, ctx):
        """
        Joins or moves to the users voice channel.
        """

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        channel = ctx.author.voice.channel
        if not ctx.player.is_connected:
            await self.do_join(ctx, channel.id)
            return await ctx.send(f'Joined the voice channel `{channel}`')
        if not ctx.guild.me.voice.channel.id == channel.id:
            await self.do_join(ctx, channel.id)
            return await ctx.send(f'Moved to the voice channel `{channel}`')
        return await ctx.send('I am already in this voice channel.')

    async def do_join(self, ctx, channel):
        """
        Join a voice channel.
        """
        permissions = ctx.author.voice.channel.permissions_for(ctx.me)
        if not permissions.connect:
            raise commands.BotMissingPermissions(['Voice: Connect'])
        if not permissions.speak:
            raise commands.BotMissingPermissions(['Voice: Speak'])
        await ctx.player.connect(channel)

    @commands.command(name='leave', aliases=['disconnect', 'stop'])
    async def leave(self, ctx):
        """
        Leaves the current voice channel.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f'MrBot is not connected to any voice channels.')
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        if not ctx.player.channel_id == ctx.author.voice.channel.id:
            return await ctx.send(f'You must be in the same voice channel as MrBot to use this command.')
        await ctx.player.disconnect()
        await ctx.player.destroy()
        return await ctx.send(f'Left the voice channel `{ctx.guild.me.voice.channel}`.')

    @commands.command(name='pause')
    async def pause(self, ctx):
        """
        Pauses the current song.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f'MrBot is not connected to any voice channels.')
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        if not ctx.player.channel_id == ctx.author.voice.channel.id:
            return await ctx.send(f'You must be in the same voice channel as MrBot to use this command.')
        if not ctx.player.current:
            return await ctx.send('No tracks currently playing.')
        if not ctx.player.paused:
            await ctx.send(f'Paused the current track.')
            self.paused = True
            await ctx.player.set_pause(True)

        return await ctx.send('The current track is already paused.')

    @commands.command(name='resume')
    async def resume(self, ctx):
        """
        Resumes the current song.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f'MrBot is not connected to any voice channels.')
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        if not ctx.player.channel_id == ctx.author.voice.channel.id:
            return await ctx.send(f'You must be in the same voice channel as MrBot to use this command.')
        if not ctx.player.current:
            return await ctx.send('No tracks currently playing.')
        if ctx.player.paused:
            await ctx.send(f'Resumed playback of the current track.')
            self.paused = False
            await ctx.player.set_pause(False)
        return await ctx.send('The current track is not paused.')

    @commands.command(name='skip')
    async def skip(self, ctx, amount: int = None):
        """
        Skip to the next song in the queue.

        This will auto skip if you are the requester of the current songs, otherwise a vote will start to skip the song.

        If `amount` is specified then the queue will skip the specified amount of songs.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f'MrBot is not connected to any voice channels.')
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        if not ctx.player.channel_id == ctx.author.voice.channel.id:
            return await ctx.send(f'You must be in the same voice channel as MrBot to use this command.')
        if ctx.player.queue.qsize() <= 0:
            return await ctx.send('There are no tracks in the queue to skip too.')
        if ctx.player.current.requester.id == ctx.author.id:
            if amount:
                if not 1 < amount <= ctx.player.queue.qsize():
                    return await ctx.send('That is not a valid amount of songs to skip.')
                for track in ctx.player.queue.queue[:amount]:
                    if not ctx.author.id == track.requester.id:
                        return await ctx.send(
                            f'You are not the requester of all `{amount}` of the next tracks in the queue.')
                    await ctx.player.queue.get_pos(0)
                await ctx.player.stop()
                return await ctx.send(f"The current song's requester has skipped `{amount}` songs.")
            await ctx.send(f"The current song's requester has skipped the song.")
            return await ctx.player.stop()
        await ctx.send('Vote skipping coming soon.')

    @commands.command(name='volume', aliases=['vol'])
    async def volume(self, ctx, volume: int):
        """
        Changes the volume of the player.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f'MrBot is not connected to any voice channels.')
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        if not ctx.player.channel_id == ctx.author.voice.channel.id:
            return await ctx.send(f'You must be in the same voice channel as MrBot to use this command.')
        if not 0 < volume < 101:
            return await ctx.send(f'Please enter a value between `1` and and `100`.')
        await ctx.send(f'Changed the players volume to `{volume}%`.')
        ctx.player.volume = volume
        await ctx.player.set_volume(volume)

    @commands.command(name='seek')
    async def seek(self, ctx, seconds: int):
        """
        Changes the postion of the player.

        `position` can be the time you want to skip to in seconds.
        """

        milliseconds = seconds * 1000
        if not ctx.player.is_connected:
            return await ctx.send(f'MrBot is not connected to any voice channels.')
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        if not ctx.player.channel_id == ctx.author.voice.channel.id:
            return await ctx.send(f'You must be in the same voice channel as MrBot to use this command.')
        if not ctx.player.current:
            return await ctx.send('No tracks currently playing.')
        if not ctx.player.current.is_seekable:
            return await ctx.send('This track is not seekable.')
        if not 0 <= milliseconds <= ctx.player.current.length:
            return await ctx.send(f'Please enter a value between `1` and `{round(ctx.player.current.length / 1000)}`.')
        await ctx.player.seek(milliseconds)
        return await ctx.send(f'Changed the players position to `{calculations.get_time(milliseconds / 1000)}`.')

    @commands.command(name='shuffle')
    async def shuffle(self, ctx):
        """
        Shuffle the queue.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f'MrBot is not connected to any voice channels.')
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        if not ctx.player.channel_id == ctx.author.voice.channel.id:
            return await ctx.send(f'You must be in the same voice channel as MrBot to use this command.')
        if ctx.player.queue.qsize() <= 0:
            return await ctx.send('Add more tracks to the queue to enable queue track shuffling.')
        random.shuffle(ctx.player.queue.queue)
        return await ctx.send(f'The queue has been shuffled.')

    @commands.command(name='clear')
    async def clear(self, ctx):
        """
        Clear the queue of all entries.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f'MrBot is not connected to any voice channels.')
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        if not ctx.player.channel_id == ctx.author.voice.channel.id:
            return await ctx.send(f'You must be in the same voice channel as MrBot to use this command.')
        if ctx.player.queue.qsize() <= 0:
            return await ctx.send('Add more tracks to the queue to enable queue clearing.')
        ctx.player.queue.queue.clear()
        return await ctx.send(f'Cleared the queue.')

    @commands.command(name='loop')
    async def loop(self, ctx):
        """
        Loop the queue.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f'MrBot is not connected to any voice channels.')
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        if not ctx.player.channel_id == ctx.author.voice.channel.id:
            return await ctx.send(f'You must be in the same voice channel as MrBot to use this command.')
        if ctx.player.loop_queue is False:
            ctx.player.loop_queue = True
        else:
            ctx.player.loop_queue = False
        if ctx.player.loop_queue is True:
            return await ctx.send(f'The queue will now loop.')
        return await ctx.send(f'The queue will stop looping.')

    @commands.command(name='remove')
    async def remove(self, ctx, entry: int):
        """
        Remove an entry from the queue.

        When removing entries use the number shown in the `queue` command. For example `mb remove  13` will remove the track in 13th position.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f'MrBot is not connected to any voice channels.')
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        if not ctx.player.channel_id == ctx.author.voice.channel.id:
            return await ctx.send(f'You must be in the same voice channel as MrBot to use this command.')
        if ctx.player.queue.qsize() <= 0:
            return await ctx.send('Add more tracks to the queue to enable queue track removing.')
        if not 0 < entry <= ctx.player.queue.qsize():
            return await ctx.send(f'That was not a valid track entry number.')
        item = await ctx.player.queue.get_pos(entry - 1)
        return await ctx.send(f'Removed `{item}` from the queue.')

    @commands.command(name='move')
    async def move(self, ctx, entry_1: int, entry_2: int):
        """
        Move an entry from one position to another in the queue.

        When moving entries use the number shown in the `queue` command. For example `mb move 1 15` will move the track in 1st position to 15th.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f'MrBot is not connected to any voice channels.')
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        if not ctx.player.channel_id == ctx.author.voice.channel.id:
            return await ctx.send(f'You must be in the same voice channel as MrBot to use this command.')
        if ctx.player.queue.qsize() <= 0:
            return await ctx.send('Add more tracks to the queue to enable queue track moving.')
        if not 0 < entry_1 <= ctx.player.queue.qsize():
            return await ctx.send(f'That was not a valid track to move from.')
        if not 0 < entry_2 <= ctx.player.queue.qsize():
            return await ctx.send(f'That was not a valid track to move too.')
        item = await ctx.player.queue.get_pos(entry_1 - 1)
        tracks = await ctx.player.node.get_tracks(f"{item}")
        track = tracks[0]
        await ctx.player.queue.put_pos(Track(track.id, track.data, ctx=ctx), entry_2 - 1)
        return await ctx.send(f'Moved `{item}` from position `{entry_1}` to position `{entry_2}`.')

    @commands.command(name='reverse')
    async def reverse(self, ctx):
        """
        Remove an entry from the queue.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f'MrBot is not connected to any voice channels.')
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        if not ctx.player.channel_id == ctx.author.voice.channel.id:
            return await ctx.send(f'You must be in the same voice channel as MrBot to use this command.')
        if ctx.player.queue.qsize() <= 0:
            return await ctx.send('Add more tracks to the queue to enable queue track moving.')
        ctx.player.queue.queue.reverse()
        return await ctx.send(f'Reversed the queue.')

    @commands.command(name='download')
    async def download(self, ctx):
        """
        Downloads an mp3 file of the current track.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f'MrBot is not connected to any voice channels.')
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        if not ctx.player.channel_id == ctx.author.voice.channel.id:
            return await ctx.send(f'You must be in the same voice channel as MrBot to use this command.')
        if not ctx.player.current:
            return await ctx.send('No tracks currently playing.')
        message = await ctx.send('Downloading track... <a:updating:403035325242540032>')
        await ctx.trigger_typing()
        track_title, track_id = await self.bot.loop.run_in_executor(None, self.do_download, ctx)
        await self.do_file_check(ctx, f'audio/{track_id}.mp3')
        await message.edit(content='Uploading track... <a:updating:403035325242540032>')
        await ctx.send(content='Here is your download.', file=discord.File(filename=f'{track_title}.mp3', fp=f'audio/{track_id}.mp3'))
        os.remove(f'audio/{track_id}.mp3')
        return await message.delete()

    async def do_file_check(self, ctx, path):
        if ctx.guild.premium_tier == 2:
            size = os.path.getsize(path)
            if size >= 52428800:
                return await ctx.send('This track is too big to upload to discord.')
        if ctx.guild.premium_tier == 3:
            size = os.path.getsize(path)
            if size >= 104857600:
                return await ctx.send('This track is too big to upload to discord.')

    def do_download(self, ctx):
        data = ytdl.extract_info(f'{ctx.player.current.uri}', download=False)
        ytdl.download([f'{ctx.player.current.uri}'])
        return data['title'], data['id']

    @commands.command(name='now_playing', aliases=['np'])
    async def now_playing(self, ctx):
        """
        Display information about the current song/queue status.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f'MrBot is not connected to any voice channels.')
        if not ctx.player.current:
            return await ctx.send('There are no tracks currently playing.')
        await ctx.player.invoke_controller()

    @commands.command(name='queue')
    async def queue(self, ctx):
        """
        Display a list of the current queue.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f'MrBot is not currently in any voice channels.')
        if ctx.player.queue.qsize() <= 0:
            return await ctx.send('The queue is empty.')
        upcoming = list(itertools.islice(ctx.player.queue.queue, 0, 10))
        message = f"__**Current track:**__\n[{ctx.player.current.title}]({ctx.player.current.uri}) | " \
                  f"`{calculations.get_time(round(ctx.player.current.length) / 1000)}` | " \
                  f"`Requested by:` {ctx.player.current.requester.mention}\n\n" \
                  f"__**Up next:**__: `{len(upcoming)}` out of `{ctx.player.queue.qsize()}` entries in the queue.\n"
        counter = 1
        time = 0
        for track in upcoming:
            message += f'**{counter}.** [{str(track.title)}]({track.uri}) | ' \
                f'`{calculations.get_time(round(track.length) / 1000)}` | ' \
                f'`Requested by:` {track.requester.mention}\n\n'
            counter += 1
            time += track.length
        message += f'There are `{ctx.player.queue.qsize()}` tracks in the queue with a total time of `{calculations.get_time(round(time) / 1000)}`'
        embed = discord.Embed(
            colour=0x57FFF5,
            timestamp=ctx.message.created_at,
            description=message
        )
        return await ctx.send(embed=embed)

    @commands.group(name='filter', invoke_without_command=True)
    async def filter(self, ctx):

        if not ctx.player.is_connected:
            return await ctx.send(f'MrBot is not connected to any voice channels.')
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        if not ctx.player.channel_id == ctx.author.voice.channel.id:
            return await ctx.send(f'You must be in the same voice channel as MrBot to use this command.')
        if ctx.player.filter_count == 0:
             return await ctx.send('No filters curently enabled.')
        message = f'>>> **The current filters are:**\n'
        if ctx.player.nightcore is True:
            message += '   - Nightcore'
        return await ctx.send(message)

    @filter.command(name='nightcore')
    async def nightcore(self, ctx):

        if not ctx.player.is_connected:
            return await ctx.send(f'MrBot is not connected to any voice channels.')
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        if not ctx.player.channel_id == ctx.author.voice.channel.id:
            return await ctx.send(f'You must be in the same voice channel as MrBot to use this command.')
        if ctx.player.nightcore is True:
            ctx.player.nightcore = False
            ctx.player.filter_count -= 1
            await ctx.send(f'Removed the nightcore filter.')
            return await ctx.player.set_timescale()
        ctx.player.nightcore = True
        ctx.player.filter_count += 1
        await ctx.send(f'Added the nightcore filter.')
        return await ctx.player.set_timescale(speed=1.1, pitch=1.1, rate=1)

    @commands.is_owner()
    @commands.cooldown(1, 300, BucketType.user)
    @commands.command(name='record')
    async def record(self, ctx, time: typing.Optional[int] = 10, user: typing.Optional[discord.Member] = None):
        """
        Record audio from a voice channel.

        `time`: How long (in seconds) you want to record for.
        `user`: The user to record. This can be a mention, id, nickname or name.
        """

        # Check if the user in a voice channel.
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        channel = ctx.author.voice.channel

        # Try to join channel, ignore errors.
        try:
            await channel.connect()
        except discord.ClientException:
            pass
        vc = ctx.voice_client

        # Check if recording time is too long.
        if not 0 < time <= 300:
            return await ctx.send(f'You can not record for more then 5 minutes.')

        # If the user doesn't pick someone to record, record them.
        if user is None:
            user = ctx.author

        # Define a buffer and a sink
        buffer = BytesIO()
        sink = MySink(buffer)

        # Start listening.
        vc.listen(discord.UserFilter(sink, user))
        message = await ctx.send(f'I am now recording `{user}` for `{time}s` in `{channel}`.')

        # Sleep for however long the user wants to record for.
        await asyncio.sleep(time + 2)

        # Stop listening.
        vc.stop_listening()
        await message.edit(content='I have finished recording.')

        #Seek back to begginning and send file.
        sink.cleanup()
        buffer.seek(0)
        await ctx.send('Here is your recording.', file=discord.File(filename=f'{ctx.author.id}.wav', fp=buffer))

    @commands.is_owner()
    @commands.command(name='stt')
    async def stt(self, ctx, user: typing.Optional[discord.Member] = None):
        """
        Execute commands based on what you say.

        To use this first join a voice chat, use this command, and say `alexa`. When the message saying you have been recognised is sent, you will be able to say a command which will then be executes by the bot.
        """

        # Check if the user in a voice channel.
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        channel = ctx.author.voice.channel

        # Try to join channel, ignore errors.
        try:
            await channel.connect()
        except discord.ClientException:
            pass

        # If the bot is already listening.
        if self.listen is True:
            return await ctx.send('I am already listening.')

        # If the user doesn't pick someone to record, record them.
        if user is None:
            user = ctx.author

        # Tell the user that we are listening, then start.
        await ctx.send(f'I am listening to `{user}`. You can say `Alexa` to invoke commands.')
        self.listen = True
        await self.listen_to_audio(ctx, user)

    async def listen_to_audio(self, ctx, user):

        # Define the stream and sink and start listening.
        vc = ctx.voice_client
        found = False
        while self.listen is True:
            try:
                # While we have not found our keyword.
                while found is False:
                    # Create a new stream and start listening.
                    stream = io.BytesIO()
                    sink = MySink(stream)
                    vc.listen(discord.UserFilter(sink, user))
                    # Sleep for 3 seconds, this is so we can loop every 3 secs.
                    await asyncio.sleep(3)
                    # Stop listening.
                    vc.stop_listening()
                    # Speech recognition is blocking so try to check what was said in an executor.
                    msg = await self.bot.loop.run_in_executor(None, self.translate, stream)
                    # If the keyword was said.
                    if 'Alexa' in msg or "alexa" in msg:
                        await ctx.send('I have detected the keyword `Alexa`, you can say a command now.')
                        # Stop listening for our keyword.
                        found = True
                # Create a new stream and start listening for our command.
                stream = io.BytesIO()
                sink = MySink(stream)
                vc.listen(discord.UserFilter(sink, user))
                # Sleep for 7 or so seconds, this is so we the user has enough time to say their command.
                await asyncio.sleep(7)
                # Stop listening.
                vc.stop_listening()
                # Speech recognition is blocking so try to check what was said in an executor.
                msg = await self.bot.loop.run_in_executor(None, self.translate, stream)
                # If the message we get back is a specific code, give an error.
                if msg == '81431':
                    await ctx.send("I was unable to understand what you said. This could be because nothing was said, or because there is too much background noise.")
                    continue
                if msg == '75482':
                    await ctx.send("Error: I could not get the results from the service.")
                    continue
                # Otherwise add the bots prefix to the message
                msg = f'{ctx.prefix}{msg.lower()}'
                await ctx.send(f'Trying to invoke the command `{msg}`.')
                # Copy the message so that we can execute it as the user we are listening too.
                fake_msg = copy.copy(ctx.message)
                fake_msg.content = msg
                fake_msg.author = user
                # Process the command.
                await self.bot.process_commands(fake_msg)
                found = False
            except Exception as e:
                print(e)

    def translate(self, stream: io.BytesIO):
        # Listen to the audio from the file, adjusting for the ambient noise.
        stream.seek(0)
        with sr.WavFile(stream) as source:
            sr.Recognizer().adjust_for_ambient_noise(source, duration=0.25)
            audio = sr.Recognizer().record(source)
        try:
            # Try to translate it into text.
            msg = sr.Recognizer().recognize_google(audio)
        except sr.UnknownValueError:
            # Return a specific code if it was not understandable
            msg = '81431'
        except sr.RequestError as e:
            msg = '75482'
            print(f"Could not request results from service. {e}")
        return msg

def setup(bot):
    bot.add_cog(Voice(bot))




