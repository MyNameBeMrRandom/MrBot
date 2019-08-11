"""
MrBot is a discord bot coded by MrRandom#1234
Copyright © 2019 Aaron Hennessey
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

# noinspection PyUnresolvedReferences
from cogs.voice import Player
from discord.ext import commands
import asyncpg
import asyncio
import aiohttp
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
    'jishaku',

]


class MrBot(commands.Bot):
    """
    Main bot class.
    """

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(config.DISCORD_PREFIX),
            reconnect=True,
        )
        self.dblpy = dbl.Client(self, config.DBL_TOKEN, webhook_path='/dblwebhook', webhook_auth=f'{config.DBL_TOKEN}', webhook_port=5000)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.loop = asyncio.get_event_loop()
        self.log_channel = None
        self.is_db_ready = False
        self.messages_seen = 0
        self.messages_sent = 0
        self.commands_run = 0
        self.config = config
        self.pool = None

        for ext in extensions:
            try:
                self.load_extension(ext)
                print(f'[EXT] Success - {ext}')
            except commands.ExtensionNotFound:
                print(f'[EXT] Failed - {ext}')

    def run(self):
        loop = self.loop
        try:
            loop.run_until_complete(self.bot_start())
        except KeyboardInterrupt:
            loop.run_until_complete(self.bot_logout())

    async def db_start(self):
        try:
            # connect to the database.
            self.pool = await asyncpg.create_pool(**config.DB_CONN_INFO)
            print('[DB] Connected to database.')

            # Create tables if they dont exist.
            print('[DB] Creating tables.')
            with open("schema.sql") as f:
                await self.pool.execute(f.read())
            print('[DB] Done creating tables.')

            # Create config for guilds joined during downtime.
            print('[DB] Adding guilds.')
            for guild in self.guilds:
                data = await self.pool.fetchrow("SELECT * FROM guild_config WHERE key = $1", guild.id)
                if not data:
                    await self.pool.execute(
                        "INSERT INTO guild_config VALUES"
                        "($1, 0, FALSE, FALSE, FALSE,"
                        "FALSE, FALSE, FALSE, FALSE, FALSE,"
                        "FALSE, FALSE, FALSE, FALSE, FALSE,"
                        "FALSE, FALSE, FALSE, FALSE, FALSE,"
                        "FALSE, FALSE, FALSE, FALSE, FALSE,"
                        "FALSE, FALSE)", guild.id)
                    print(f'[DB] Created config for guild - {guild.name}.')
            print('[DB] Done adding guilds.')

            # Tell bot that database is ready.
            self.is_db_ready = True

        except ConnectionRefusedError:
            print('[DB] Connection to db was denied.')
        except Exception as e:
            print(f'[DB] An error occured: {e}')

    async def bot_logout(self):
        self.is_db_ready = False
        await super().logout()
        await self.session.close()
        await self.pool.close()

    async def bot_start(self):
        await self.login(config.DISCORD_TOKEN)
        await self.connect()

    async def on_ready(self):
        print(f'\n[BOT] Logged in as {self.user} - {self.user.id}\n')
        self.log_channel = self.get_channel(516002789617434664)
        await self.db_start()

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=MyContext)

class MyContext(commands.Context):

    @property
    def player(self):
        return self.bot.andesite.get_player(self.guild.id, cls=Player)


MrBot().run()
