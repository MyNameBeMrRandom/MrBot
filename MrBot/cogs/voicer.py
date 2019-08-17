from discord.opus import Decoder
from discord.ext import commands
import speech_recognition as sr
from io import BytesIO
import discord
import asyncio
import typing
import wave


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

class VoiceReceive(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

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

        # Define a buffer and sink
        buffer = BytesIO()
        sink = MySink(buffer)

        # Start listening.
        vc.listen(discord.UserFilter(sink, user))
        message = await ctx.send(f'I am now recording `{user}` for `{time}s` in <#{channel.id}>.')

        # Sleep for however long the user wants to record for.
        await asyncio.sleep(time)

        # Stop listening.
        vc.stop_listening()
        await message.edit(content='I have finished recording.')

        #Seek back to begginning and send file.
        sink.cleanup()
        buffer.seek(0)
        await ctx.send('Here is your recording.', file=discord.File(filename=f'{ctx.author.id}.wav', fp=buffer))

    """
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
    """


def setup(bot):
    bot.add_cog(VoiceReceive(bot))

