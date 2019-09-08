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
# noinspection PyUnresolvedReferences
from cogs.utils.paginator import ListPaginator, EmbedPaginator
from discord.ext import commands
import asyncpg
import discord
import asyncio
import aiohttp
import spotify
import config
import math
import dbl
import os


if not discord.opus.is_loaded():
    discord.opus.load_opus(config.OPUS)

os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"

extensions = [
    "cogs.utilities",
    "cogs.music",
    "cogs.images",
    "cogs.kross",
    "cogs.help",
    "jishaku",

    "cogs.background",
    "cogs.events",
]


class MrBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(config.DISCORD_PREFIX),
            reconnect=True,
        )
        self.dblpy = dbl.DBLClient(self, config.DBL_TOKEN, webhook_path="/dblwebhook", webhook_auth=config.DBL_TOKEN, webhook_port=5000)
        self.spotify = spotify.Client(client_id=config.SPOTIFY_CLIENT_ID, client_secret=config.SPOTIFY_CLIENT_SECRET)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.loop = asyncio.get_event_loop()
        self.config = config
        self.status_channel = None
        self.log_channel = None
        self.db_ready = False
        self.db = None
        self.usage = {}

        # Load extensions
        for extension in extensions:
            try:
                self.load_extension(extension)
                print(f"[EXT] Success - {extension}")
            except commands.ExtensionNotFound:
                print(f"[EXT] Failed - {extension}")

    async def bot_start(self):
        await self.login(config.DISCORD_TOKEN)
        await self.connect()

    async def bot_close(self):
        await super().logout()
        await self.session.close()

    def run(self):
        try:
            self.loop.run_until_complete(self.bot_start())
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.bot_close())

    async def on_ready(self):
        # Set our logging and status channels.
        self.status_channel = self.get_channel(config.STATUS_CHANNEL_ID)
        self.log_channel = self.get_channel(config.LOG_CHANNEL_ID)

        # Send a message to status channel notifying when the bot has been connected.
        await self.status_channel.send(f"`{self.user}` has been connected.")
        print(f"\n[BOT] Logged in as {self.user} - {self.user.id}")

        # Connect to database.
        try:
            # Try and connect to the database.
            self.db = await asyncpg.create_pool(**config.DB_CONN_INFO)
            print(f"\n[DB] Connected to database.")

            # Create tables if they dont exist.
            print("[DB] Creating tables.")
            with open("schema.sql") as f:
                await self.db.execute(f.read())
            print("[DB] Done creating tables.")

            # Create configs for guilds joined during downtime.
            print("[DB] Adding guilds.")

            # Loop through all the current guilds.
            for guild in self.guilds:

                # If the guild already has a config, skip it.
                if await self.db.fetchrow("SELECT * FROM guild_config WHERE key = $1", guild.id):
                    continue

                # Else create a config for the guild.
                await self.db.execute("INSERT INTO guild_config VALUES ($1)", guild.id)

                print(f"[DB] Created config for guild - {guild.name}.")
            print("[DB] Done adding guilds.")
            # Tell the bot that the databse is ready.
            self.db_ready = True
        except ConnectionRefusedError:
            print(f"[DB] Connection to database was denied.")
        except Exception as e:
            print(f"[DB] An error occured: {e}")

    async def on_resume(self):
        await self.status_channel.send(f"`{self.user}'s` connection has been resumed.")
        print(f"\n[BOT] Connection resumed.")

    async def on_disconnect(self):
        await self.status_channel.send(f"`{self.user}` has been disconnected.")
        print(f"\n[BOT] Disconnected.")

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=MyContext)


class MyContext(commands.Context):

    @property
    def player(self):
        return self.bot.andesite.get_player(self.guild.id, cls=Player)

    async def lpaginate(self, **kwargs):
        # Get the aruguements.
        title = kwargs.get("title")
        entries = kwargs.get("entries")
        entries_per_page = kwargs.get("entries_per_page")

        # Calculate the amount of pages we will need and round it up.
        pages = math.ceil(len(entries) / entries_per_page)

        # Define a new list to store the "combined" entries
        c_entries = []

        # Create a loop for going through each page.
        for i in range(pages):

            # Define a new entry for us to add amount of "entries_per_page" of entries to.
            new_entry = ""

            # Add one to the page loop so that the next step works lmao.
            i += 1

            # Loop through the entries, getting the first amount of "entries_per_page" and then the next amount of "entries_per_page" in next page cycle.
            for entry in entries[entries_per_page * i - entries_per_page:entries_per_page * i]:
                new_entry += f"{entry}\n"

            # Append the new entry to the "combined" entry list
            c_entries.append(new_entry)

        # Start pagination
        paginator = ListPaginator(ctx=self, title=title, org_entries=entries, entries=c_entries, entries_per_page=entries_per_page, pages=pages)
        return await paginator.paginate()

    async def epaginate(self, **kwargs):
        # Get the aruguements.
        title = kwargs.get("title")
        entries = kwargs.get("entries")
        entries_per_page = kwargs.get("entries_per_page")

        # Calculate the amount of pages we will need and round it up.
        pages = math.ceil(len(entries) / entries_per_page)

        # Define a new list to store the "combined" entries
        c_entries = []

        # Create a loop for going through each page.
        for i in range(pages):

            # Define a new entry for us to add amount of "entries_per_page" of entries to.
            new_entry = ""

            # Add one to the page loop so that the next step works lmao.
            i += 1

            # Loop through the entries, getting the first amount of "entries_per_page" and then the next amount of "entries_per_page" in next page cycle.
            for entry in entries[entries_per_page * i - entries_per_page:entries_per_page * i]:
                new_entry += f"{entry}\n"

            # Append the new entry to the "combined" entry list
            c_entries.append(new_entry)

        # Start pagination
        paginator = EmbedPaginator(ctx=self, title=title, org_entries=entries, entries=c_entries, entries_per_page=entries_per_page, pages=pages)
        return await paginator.paginate()


if __name__ == "__main__":
    MrBot().run()
