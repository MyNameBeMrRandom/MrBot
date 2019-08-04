# noinspection PyUnresolvedReferences
from cogs.voice import Player
from discord.ext import commands
import logging.handlers
import asyncpg
import asyncio
import config
import dbl
import os

os.environ['JISHAKU_HIDE'] = 'True'
os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'

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
handler = logging.handlers.TimedRotatingFileHandler(filename=f'logs/mrbot.log', encoding='utf-8', backupCount=10, interval=100, when='D', utc=True)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


class MrBot(commands.AutoShardedBot):
	"""
	Main bot class.
	"""

	def __init__(self):
		super().__init__(
			command_prefix=commands.when_mentioned_or(config.DISCORD_PREFIX),
			reconnect=True,
		)
		self.loop = asyncio.get_event_loop()
		self.is_db_ready = False
		self.messages_seen = 0
		self.messages_sent = 0
		self.commands_run = 0
		self.logging = logger
		self.config = config
		self.pool = None

		for ext in extensions:
			try:
				self.load_extension(ext)
				print(f'[EXT] Success - {ext}')
				logger.info(f'[EXT] Success - {ext}')
			except commands.ExtensionNotFound:
				print(f'[EXT] Failed - {ext}')
				logger.warning(f'[EXT] Failed - {ext}')

	def run(self):
		"""
		Run the bot.
		"""

		loop = self.loop
		try:
			loop.run_until_complete(self.bot_start())
		except KeyboardInterrupt:
			loop.run_until_complete(self.bot_logout())

	async def db_start(self):
		try:
			self.pool = await asyncpg.create_pool(**config.DB_CONN_INFO)
			print('[DB] Successfully connected to database.')
			print('[DB] Creating tables.')
			with open("schema.sql") as f:
				await self.pool.execute(f.read())
			print('[DB] Done creating tables.')
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
			print('[DB] Done adding guilds.')
			self.is_db_ready = True
		except ConnectionRefusedError:
			print('[DB] Connection to db was denied.')
		except Exception as e:
			print(f'[DB] An error occured: {e}')

	async def bot_logout(self):
		"""
		Logout from discord.
		"""
		self.is_db_ready = False
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
		print(f'\n[BOT] Logged in as {self.user} - {self.user.id}\n')
		await self.db_start()

	async def get_context(self, message, *, cls=None):
		return await super().get_context(message, cls=MyContext)

class MyContext(commands.Context):

	@property
	def player(self):
		return self.bot.andesite.get_player(self.guild.id, cls=Player)


MrBot().run()

