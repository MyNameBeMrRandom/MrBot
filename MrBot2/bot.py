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

You should have received a copy of the GNU Affero General Public License along with this program. If not,
see <https://www.gnu.org/licenses/>.

"""

# noinspection PyUnresolvedReferences
from cogs.music import Player
from discord.ext import commands
import asyncpg
import discord
import asyncio
import aiohttp
import config
import os


# Load opus if it it not loaded automatically.
if not discord.opus.is_loaded():
    discord.opus.load_opus(config.OPUS)

# Set jishaku env variables.
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"

# Define a list of extensions to load.
extensions = [
    "cogs.music",
    "cogs.help",
    "jishaku"
]


class MrBot(commands.AutoShardedBot):

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(config.DISCORD_PREFIX),
            reconnect=True,
        )
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.loop = asyncio.get_event_loop()
        self.config = config
        self.status_channel = None
        self.log_channel = None
        self.db_ready = False
        self.db = None

        # Load extension
        for extension in extensions:
            try:
                self.load_extension(extension)
                print(f"[EXT] Success - {extension}")
            except commands.ExtensionNotFound:
                print(f"[EXT] Failed - {extension}")

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=MyContext)

    async def on_disconnect(self):
        # Send a message to status channel notifying when the bot has been disconnected.
        await self.status_channel.send(f"`{self.user}` has been disconnected.")
        print(f"\n[BOT] Disconnected.")

    async def on_resume(self):
        # Send a message to status channel notifying when the bots connection has been resumed.
        await self.status_channel.send(f"`{self.user}'s` connection has been resumed.")
        print(f"\n[BOT] Connection resumed.")

    async def on_ready(self):
        # Set our logging and status channels.
        self.status_channel = self.get_channel(615936923302887424)
        self.log_channel = self.get_channel(516002789617434664)
        # Send a message to status channel notifying when the bot has been connected.
        await self.status_channel.send(f"`{self.user}` has been connected.")
        print(f"\n[BOT] Logged in as {self.user} - {self.user.id}")
        try:
            # Try and connect to the database.
            self.db = await asyncpg.create_pool(**config.DB_CONN_INFO)
            print(f"\n[DB] Connected to database.")
            # Create tables if they dont exist.
            print('[DB] Creating tables.')
            with open("schema.sql") as f:
                await self.db.execute(f.read())
            print('[DB] Done creating tables.')
            # Create configs for guilds joined during downtime.
            print('[DB] Adding guilds.')
            # Loop through all the current guilds.
            for guild in self.guilds:
                # If the guild already has a config, skip it.
                if await self.db.fetchrow("SELECT * FROM guild_config WHERE key = $1", guild.id):
                    continue
                # Else create a config for the guild.
                await self.db.execute("INSERT INTO guild_config VALUES ($1)", guild.id)
                print(f'[DB] Created config for guild - {guild.name}.')
            print('[DB] Done adding guilds.')
            self.db_ready = True
        except ConnectionRefusedError:
            print(f"[DB] Connection to database was denied.")
        except Exception as e:
            print(f"[DB] An error occured: {e}")

    async def bot_start(self):
        # Log into discord.
        await self.login(config.DISCORD_TOKEN)
        # Connect to discord.
        await self.connect()

    async def bot_close(self):
        # Log the bot out.
        await super().logout()
        # Close the aiohttp session.
        await self.session.close()

    def run(self):
        try:
            self.loop.run_until_complete(self.bot_start())
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.bot_close())


class MyContext(commands.Context):

    @property
    def player(self):
        return self.bot.andesite.get_player(self.guild.id, cls=Player)


MrBot().run()
