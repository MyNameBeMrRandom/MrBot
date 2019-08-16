from discord.opus import Decoder
from discord.ext import commands
import speech_recognition as sr
import discord
import asyncio
import typing
import wave
import os


class MySink(discord.AudioSink):

    def __init__(self, destination):

        self.destination = destination
        self.buffer = wave.open(destination, 'wb')
        self.buffer.setnchannels(Decoder.CHANNELS)
        self.buffer.setsampwidth(Decoder.SAMPLE_SIZE//Decoder.CHANNELS)
        self.buffer.setframerate(Decoder.SAMPLING_RATE)

    def write(self, data):
        print(0)
        self.buffer.writeframes(data.data)

    def cleanup(self):
        self.buffer.close()

class VoiceReceive(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.recording = False

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
        # Get the voice client.
        vc = ctx.voice_client
        # Check if recording time is too long.
        if not 0 < time <= 300:
            return await ctx.send(f'You can not record for more then 5 minutes.')
        # If the user does'nt pick someone to record, record them.
        if user is None:
            to_record = ctx.author
        else:
            to_record = user
        # Check if we are already recording.
        if self.recording is True:
            return await ctx.send('I am already recording something.')
        # Start listening to the voice channel.
        vc.listen(discord.UserFilter(MySink(f'audio/{ctx.author.id}.wav'), to_record))
        self.recording = True
        message = await ctx.send(f'I am now recording `{user}` for `{time}s` in <#{channel.id}>.')
        # Sleep for however long the user wants to record for.
        await asyncio.sleep(time)
        # Edit message for when the time is up.
        await message.edit(content='I have finished recording.')
        # Stop listening.
        vc.stop_listening()
        self.recording = False
        # Send file.
        await ctx.send('Here is your recording.', file=discord.File(filename=f'{ctx.author.id}.wav', fp=f'audio/{ctx.author.id}.wav'))
        os.remove(f'audio/{ctx.author.id}.wav')

    @commands.command(name='listen')
    async def listen(self, ctx):

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f'You must be in a voice channel to use this command.')
        channel = ctx.author.voice.channel
        vc = await channel.connect()
        vc.listen(discord.UserFilter(self.buffer, ctx.author))
        if vc.is_listening:
            await ctx.send('I am listening.')
        while vc.is_listening:
            await asyncio.sleep(2)
            msg = await self.bot.loop.run_in_executor(None, self.read_audio)
            await ctx.send(msg)

    def read_audio(self):
        file = sr.AudioFile('music.wav')
        with file as source:
            audio = sr.Recognizer().record(source)
        msg = 'None'
        try:
            msg = sr.Recognizer().recognize_google(audio)
        except sr.UnknownValueError:
            print("ERROR: Couldn't understand.")
        except sr.RequestError as e:
            print(f"ERROR: Could not request results from service {e}")
        return msg


def setup(bot):
    bot.add_cog(VoiceReceive(bot))

