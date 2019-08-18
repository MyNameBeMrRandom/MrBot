from discord.opus import Decoder
from discord.ext import commands
import speech_recognition as sr
from io import BytesIO
import discord
import asyncio
import typing
import wave
import copy

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
        self.listen = False

    @commands.is_owner()
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
    @commands.command(name='listen')
    async def listen(self, ctx, user: typing.Optional[discord.Member] = None):
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

        # If the user doesn't pick someone to record, record them.
        if user is None:
            user = ctx.author

        # If the bot is already listening.
        if self.listen is True:
            return await ctx.send('I am already listening.')

        # Keep on listening.
        await ctx.send(f'I am listening to `{user}`. You can say `Alexa` to invoke commands.')
        self.listen = True
        while self.listen is True:
            await self.listen_to_audio(ctx, user)

    async def listen_to_audio(self, ctx, user):
        try:
            # Get voice client.
            vc = ctx.voice_client
            # Get sink and start listening.
            sink = MySink("audio/listen.wav")
            vc.listen(discord.UserFilter(sink, user))
            # Sleep for 3 seconds.
            await asyncio.sleep(3)
            # Stop listening and exit file.
            vc.stop_listening()
            sink.cleanup()
            # Try and find what was said.
            msg = await self.bot.loop.run_in_executor(None, self.translate, sink)
            # If alexa was said.
            if 'Alexa' in msg or "alexa" in msg:
                await ctx.send('I have detected keyword `Alexa`, you can say a command now.')
                # Get sink and start listening.
                sink = MySink("audio/listen.wav")
                vc.listen(discord.UserFilter(sink, user))
                # Sleep for 10 secs.
                await asyncio.sleep(10)
                # Stop listening and exit file.
                vc.stop_listening()
                sink.cleanup()
                # Try and find what was said.
                msg = await self.bot.loop.run_in_executor(None, self.translate, sink)
                msg = f'mb {msg}'
                await ctx.send(msg)
                fake_msg = copy.copy(ctx.message)
                fake_msg.content = msg.lower()
                fake_msg.author = user
                await self.bot.process_commands(fake_msg)
        except Exception as e:
            print(e)

    def translate(self, sink):
        with sr.WavFile(sink.destination) as source:
            sr.Recognizer().adjust_for_ambient_noise(source, duration=0.25)
            audio = sr.Recognizer().record(source)
        try:
            msg = sr.Recognizer().recognize_google(audio)
        except sr.UnknownValueError:
            msg = "ERROR: Couldn't understand."
        except sr.RequestError as e:
            msg = f"ERROR: Could not request results from service {e}"
        return msg

def setup(bot):
    bot.add_cog(VoiceReceive(bot))

