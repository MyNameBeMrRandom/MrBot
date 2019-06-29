from discord.ext import commands
import logging.handlers
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
	'cogs.kross_server',
	'cogs.utilities',
	'cogs.bg_tasks',
	'cogs.accounts',
	'cogs.economy',
	'cogs.events',
	'cogs.images',
	'cogs.admin',
	'cogs.owner',
	#'cogs.voice',
	'cogs.help',
	'cogs.fun',
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

