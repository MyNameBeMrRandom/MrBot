from discord.ext import commands
import discord
import asyncio


class BgTasks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.update_presence = self.bot.loop.create_task(self.activity_changing())

    async def activity_changing(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f'{len(self.bot.guilds)} Guilds', ))
            await asyncio.sleep(300)
            await self.bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.watching, name=f'{len(self.bot.users)} Users'))
            await asyncio.sleep(300)
            await self.bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.playing, name=f"Do 'mb help'!"))
            await asyncio.sleep(300)

def setup(bot):
    bot.add_cog(BgTasks(bot))