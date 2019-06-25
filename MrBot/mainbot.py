from discord.ext import commands
import logging.handlers
import traceback
import discord
import asyncio
import config
import os

os.environ['JISHAKU_HIDE'] = 'True'

try:
	# noinspection PyUnresolvedReferences
	import uvloop
except ImportError:
	pass
else:
	asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

extensions = [
	'cogs.guild_logging',
	'cogs.user_logging',
	'cogs.kross_server',
	'cogs.utilities',
	'cogs.bg_tasks',
	'cogs.accounts',
	'cogs.economy',
	'cogs.images',
	'cogs.admin',
	'cogs.owner',
	'cogs.voice',
	'cogs.help',
	'jishaku',

]

logger = logging.getLogger('MrBot')
logger.setLevel(logging.INFO)
handler = logging.handlers.TimedRotatingFileHandler(
	filename=f'logs/mrbot.log',
	encoding='utf-8',
	backupCount=10,
	interval=100,
	when='D',
	utc=True
)
handler.setFormatter(
	logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger.addHandler(handler)


# noinspection PyMethodMayBeStatic
class MrBot(commands.AutoShardedBot):

	def __init__(self):
		super().__init__(
			command_prefix=commands.when_mentioned_or(config.DISCORD_PREFIX),
			reconnect=True,
		)
		self.loop = asyncio.get_event_loop()
		self.config = config
		self.logging = logger

		for ext in extensions:
			# noinspection PyBroadException
			try:
				self.load_extension(ext)
				print(f'Success - {ext}')
				logger.info(f'[EXT] - Successfully loaded - {ext}')
			except Exception:
				print(f'Failed - {ext}')
				logger.warning(f'[EXT] - Failed to load - {ext}')

	async def on_command_error(self, ctx, error):
		error = getattr(error, 'original', error)
		if hasattr(ctx.command, 'on_error'):
			return
		elif isinstance(error, commands.NoPrivateMessage):
			try:
				return await ctx.send(f"The command `{ctx.command}` cannot be used in private messages.")
			except Exception:
				pass
		elif isinstance(error, commands.DisabledCommand):
			return await ctx.send(f"The command `{ctx.command}` is currently disabled.")
		elif isinstance(error, commands.CommandNotFound):
			return await ctx.send(f"The command `{ctx.message.clean_content}` was not found.")
		elif isinstance(error, commands.CommandOnCooldown):
			return await ctx.send(f"The command `{ctx.command}` is on cooldown, retry in {round(error.retry_after, 2)}s.")
		elif isinstance(error, commands.MissingRequiredArgument):
			return await ctx.send(f"You missed the `{error.param}` parameter.")
		elif isinstance(error, commands.TooManyArguments):
			return await ctx.send(f"Too many arguments were passed for the command `{ctx.command}`.")
		elif isinstance(error, commands.BadArgument):
			return await ctx.send(f"A bad argument was passed to the command `{ctx.command}`.")
		elif isinstance(error, commands.MissingPermissions):
			return await ctx.send(f"You dont have the permissions to run the `{ctx.command}` command.")
		elif isinstance(error, commands.BotMissingPermissions):
			return await ctx.send(f"I am missing the following permissions to run the command `{ctx.command}`.\n{error.missing_perms}")
		elif isinstance(error, discord.HTTPException):
			if isinstance(error, discord.Forbidden):
				return await ctx.send(f"I am missing permissions to run the command `{ctx.command}`.")
		elif isinstance(error, commands.CommandInvokeError):
			return await ctx.send(f"There was an error while running that command")
		else:
			try:
				print(f'{error.original.__class__.__name__}: {error.original}')
				traceback.print_tb(error.original.__traceback__)
			except AttributeError:
				print(f'{error.__class__.__name__}: {error}')
				traceback.print_tb(error.__traceback__)

	async def on_command_completion(self, ctx):
		self.logging.info(f'[COMMAND] - {ctx.author} used the command "{ctx.command}" in the guild {ctx.guild}.')

	async def on_guild_join(self, guild):
		self.logging.info(f'[GUILD] - Joined the guild {guild.name}.')
		channel = self.get_channel(516002789617434664)
		embed = discord.Embed(
			colour=0x57FFF5,
		)
		embed.add_field(name='Guild Join', value=f'MrBot joined a guild.\nName: **{guild.name}**', inline=False)
		return await channel.send(embed=embed)

	async def on_guild_remove(self, guild):
		self.logging.info(f'[GUILD] - Left the guild {guild.name}.')
		channel = self.get_channel(516002789617434664)
		embed = discord.Embed(
			colour=0x57FFF5,
		)
		embed.add_field(name='Guild Leave', value=f'MrBot left a guild.\nName: **{guild.name}**', inline=False)
		return await channel.send(embed=embed)

	async def bot_logout(self):
		await super().logout()

	async def bot_start(self):
		await self.login(config.DISCORD_TOKEN)
		await self.connect()

	async def on_ready(self):
		logger.info(f'[BOT] Logged in as {self.user} - {self.user.id}')
		print(f'\nLogged in as {self.user} - {self.user.id}')

	def run(self):
		loop = self.loop
		try:
			loop.run_until_complete(self.bot_start())
		except KeyboardInterrupt:
			loop.run_until_complete(self.bot_logout())


MrBot().run()

