from discord.ext import commands
import discord
import asyncio
import config
import dbl


class BgTasks(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.dblpy = dbl.Client(self.bot, config.DBL_TOKEN, webhook_path='/dblwebhook', webhook_auth=f'{config.DBL_TOKEN}', webhook_port=5000)
		self.presence_task = self.bot.loop.create_task(self.activity_changing())
		self.updating = self.bot.loop.create_task(self.update_guild_count())

	async def activity_changing(self):
			await self.bot.wait_until_ready()
			while not self.bot.is_closed():
				await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f'{len(self.bot.guilds)} Guilds.', ))
				await asyncio.sleep(60)
				await self.bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.watching, name=f'{len(self.bot.users)} Users.'))
				await asyncio.sleep(60)
				await self.bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.playing, name=f'Do "mb help"!'))
				await asyncio.sleep(60)

	async def update_guild_count(self):
		await self.bot.wait_until_ready()
		while self.bot.is_ready():
			self.bot.logging.info('[SERVER_COUNT] - Attempting to post server count to DBL.')
			try:
				await self.dblpy.post_guild_count()
				self.bot.logging.info(f'[SERVER_COUNT] - Posted server count to DBL({self.dblpy.guild_count()}).')
			except Exception as e:
				self.bot.logging.exception('[SERVER_COUNT] - Failed to post server count.\n{}: {}'.format(type(e).__name__, e))
			await asyncio.sleep(21600)


def setup(bot):
	bot.add_cog(BgTasks(bot))