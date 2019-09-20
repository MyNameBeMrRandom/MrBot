"""
MrBot is a discord bot coded by MrRandom#1234
Copyright © 2019 Aaron Hennessey
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with this program. If not,
see <https://www.gnu.org/licenses/>.
"""

import asyncio
import math
import os

from discord.ext import commands
import discord
import aiohttp
import asyncpg
import config
import dbl

# noinspection PyUnresolvedReferences
from cogs.utils.paginator import ListPaginator, EmbedPaginator, ListEmbedPaginator
# noinspection PyUnresolvedReferences
from cogs.music import Player


# Im having problems with opus loading so, this is here.
if not discord.opus.is_loaded():
    discord.opus.load_opus(config.OPUS)

os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"

EXTENSIONS = [
    "cogs.utilities",
    "cogs.music",
    "cogs.kross",

    "cogs.accounts",
    "cogs.images",

    "cogs.api",

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
        self.loop = asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.config = config

        self.db = None
        self.db_ready = False

        self.usage = {}

        self.dblpy = dbl.DBLClient(self, config.DBL_TOKEN, webhook_path="/dblwebhook", webhook_auth=config.DBL_TOKEN, webhook_port=5000)

        for extension in EXTENSIONS:
            try:
                self.load_extension(extension)
                print(f"[EXT] Success - {extension}")
            except commands.ExtensionNotFound:
                print(f"[EXT] Failed - {extension}")

    def run(self):
        try:
            self.loop.run_until_complete(self.bot_start())
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.bot_close())

    async def bot_start(self):
        await self.login(config.DISCORD_TOKEN)
        await self.connect()

    async def bot_close(self):
        await super().logout()
        await self.session.close()

    async def on_ready(self):
        print(f"\n[BOT] Logged in as {self.user} - {self.user.id}")

        # If the database has already been connected
        if self.db_ready is True:
            return

        # Try to connect to the database.
        try:
            self.db = await asyncpg.create_pool(**config.DB_CONN_INFO)
            print(f"\n[DB] Connected to database.")

            # Create tables if the dont exist.
            print("[DB] Creating tables.")
            with open("schema.sql") as r:
                await self.db.execute(r.read())
            print("[DB] Done creating tables.")

            # Create config for guilds..
            print("[DB] Adding guilds.")
            # Loop through all the bots guilds.
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
        print(f"\n[BOT] Connection resumed.")

    async def on_disconnect(self):
        print(f"\n[BOT] Disconnected.")

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=MyContext)


class MyContext(commands.Context):

    @property
    def player(self):
        return self.bot.andesite.get_player(self.guild.id, cls=Player)

    async def paginate_list(self, **kwargs):
        # Get the aruguements.
        title = kwargs.get("title")
        entries = kwargs.get("entries")
        entries_per_page = kwargs.get("entries_per_page")

        # Calculate the amount of pages we need and round it up.
        pages = math.ceil(len(entries) / entries_per_page)

        # Define a new list to store the new entries.
        c_entries = []

        # Create a loop for the amount of pages needed.
        for i in range(pages):
            # Define a new entry for us to add amount of "entries_per_page" of entries to.
            new_entry = ""
            # Add one to the page loop so that the next step works lmao.
            i += 1
            # Loop through the entries, getting the first amount of "entries_per_page" and then the next amount of "entries_per_page" in next page cycle.
            for entry in entries[entries_per_page * i - entries_per_page:entries_per_page * i]:
                new_entry += f"{entry}\n"
            # Append the new entry to the new entry list
            c_entries.append(new_entry)

        # Start pagination
        paginator = ListPaginator(ctx=self, title=title, org_entries=entries, entries=c_entries, entries_per_page=entries_per_page, pages=pages)
        return await paginator.paginate()

    async def paginate_list_embed(self, **kwargs):
        # Get the aruguements.
        title = kwargs.get("title")
        entries = kwargs.get("entries")
        entries_per_page = kwargs.get("entries_per_page")

        # Calculate the amount of pages we need and round it up.
        pages = math.ceil(len(entries) / entries_per_page)

        # Define a new list to store the new entries.
        c_entries = []

        # Create a loop for the amount of pages needed.
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
        paginator = ListEmbedPaginator(ctx=self, title=title, org_entries=entries, entries=c_entries, entries_per_page=entries_per_page, pages=pages)
        return await paginator.paginate()

    async def paginate_embeds(self, **kwargs):
        # Get the aruguements.
        entries = kwargs.get("entries")
        pages = len(entries)

        paginator = EmbedPaginator(ctx=self, entries=entries, pages=pages)

        # Start pagination
        return await paginator.paginate()


if __name__ == "__main__":
    MrBot().run()
