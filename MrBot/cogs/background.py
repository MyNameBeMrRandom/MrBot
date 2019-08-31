from discord.ext import commands, tasks
import discord
import random


class Background(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.change_prescence.start()

    def cog_unload(self):
        self.change_prescence.stop()

    @tasks.loop(minutes=10.0)
    async def change_prescence(self):
        prescences = [discord.Activity(type=discord.ActivityType.watching, name=f'{len(self.bot.guilds)} Guilds'),
                      discord.Activity(type=discord.ActivityType.watching, name=f'{len(self.bot.users)} Users'),
                      discord.Activity(type=discord.ActivityType.playing, name=f"mb help")
                      ]
        await self.bot.change_presence(activity=random.choice(prescences))

    @change_prescence.before_loop
    async def before_change_prescence(self):
        await self.bot.wait_until_ready()

    @change_prescence.after_loop
    async def after_change_prescence(self):
        await self.bot.change_presence()


def setup(bot):
    bot.add_cog(Background(bot))
