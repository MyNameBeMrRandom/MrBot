from discord.ext import commands
import logging.handlers
import config
import asyncio
import yaml
import time
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
	'jishaku',
	'cogs.bot_utils',
	'cogs.accounts',
	'cogs.economy',
	'cogs.admin',
	'cogs.logging',
	'cogs.images',
	'cogs.kross_server',
	'cogs.owner',
	'cogs.utilities',
	'cogs.voice',

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

	def update_times(self):
		for guild in self.guilds:
			for member in guild.members:
				try:
					if os.path.isfile(f'data/accounts/{member.id}.yaml'):
						with open(f'data/accounts/{member.id}.yaml', 'r', encoding='utf8') as r:
							data = yaml.load(r, Loader=yaml.FullLoader)
							if data['status_times'][f'{member.status}_since'] is None:
								data['status_times'][f'{member.status}_since'] = time.time()
								with open(f'data/accounts/{member.id}.yaml', 'w', encoding='utf8') as w:
									yaml.dump(data, w)
				except FileNotFoundError:
					return

	async def bot_logout(self):
		await super().logout()

	async def bot_start(self):
		await self.loop.run_in_executor(None, self.update_times)
		await self.login(config.DISCORD_TOKEN)
		await self.connect()

	async def on_ready(self):
		logger.info(f'[BOT] Logged in as {self.user} - {self.user.id}')
		print(f'\nLogged in as {self.user} - {self.user.id}')

	async def on_message(self, message):
		if message.author.bot:
			return
		await self.process_commands(message)

	def run(self):
		loop = self.loop
		try:
			loop.run_until_complete(self.bot_start())
		except KeyboardInterrupt:
			loop.run_until_complete(self.bot_logout())


MrBot().run()

