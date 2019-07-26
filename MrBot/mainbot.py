from discord.ext import commands
import logging.handlers
import asyncpg
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
	'cogs.voice',
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
class MrBot(commands.Bot):
	"""
	Main bot class.
	"""

	def __init__(self):
		super().__init__(
			command_prefix=commands.when_mentioned_or(config.DISCORD_PREFIX),
			reconnect=True,
		)
		self.loop = asyncio.get_event_loop()
		self.config = config
		self.logging = logger
		self.pool = None

		for ext in extensions:
			# noinspection PyBroadException
			try:
				self.load_extension(ext)
				print(f'[EXT] Success - {ext}')
				logger.info(f'[EXT] Success - {ext}')
			except Exception:
				print(f'[EXT] Failed - {ext}')
				logger.warning(f'[EXT] Failed - {ext}')

	async def db_start(self):
		try:
			self.pool = await asyncpg.create_pool(**config.DB_CONN_INFO)
			print('\n[DB] Successfully connected to database.\n')
			print('[DB] Creating tables.')
			with open("data/schema.sql") as f:
				await self.pool.execute(f.read())
			print('[DB] Done creating tables.\n')
			print('[DB] Adding guilds.')
			for guild in self.guilds:
				try:
					await self.pool.execute(
						"INSERT INTO guild_config VALUES" 
						"($1, NULL, FALSE, FALSE, FALSE," 
						"FALSE, FALSE, FALSE, FALSE, FALSE," 
						"FALSE, FALSE, FALSE, FALSE, FALSE," 
						"FALSE, FALSE, FALSE, FALSE, FALSE," 
						"FALSE, FALSE, FALSE, FALSE, FALSE," 
						"FALSE, FALSE)", guild.id)
					print(f'[DB] Created config for guild - {guild.name}.')
				except asyncpg.UniqueViolationError:
					pass
			print('[DB] Done adding guilds.\n')
		except ConnectionRefusedError:
			print('\n[DB] Connection to db was denied.')
		except Exception as e:
			print(f'\n[DB] An error occured: {e}')

	async def bot_logout(self):
		"""
		Logout from discord.
		"""
		await self.pool.close()
		await super().logout()

	async def bot_start(self):
		"""
        Start the discord bot.
		"""
		await self.login(config.DISCORD_TOKEN)
		await self.connect()

	async def on_ready(self):
		"""
		Allow for processing when the bot is ready.
		"""

		logger.info(f'[BOT] Logged in as {self.user} - {self.user.id}')
		print(f'\n[BOT] Logged in as {self.user} - {self.user.id}')
		await self.db_start()

	def run(self):
		"""
		Run the bot.
		"""

		loop = self.loop
		try:
			loop.run_until_complete(self.bot_start())
		except KeyboardInterrupt:
			loop.run_until_complete(self.bot_logout())


MrBot().run()

