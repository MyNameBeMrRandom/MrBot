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
import os

from discord.ext import commands
import discord
import aiohttp
import asyncpg
import config
import dbl

# noinspection PyUnresolvedReferences
from cogs.utils.paginator import CodeblockPaginator, Paginator, EmbedPaginator, EmbedsPaginator
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
    "cogs.accounts",
    "cogs.images",
    "cogs.api",
    "cogs.help",
    "cogs.kross",
    "cogs.owner",
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

        self.stats = {}
        self.owner_ids = {238356301439041536}
        self.user_blacklist = []
        self.guild_blacklist = []

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

    async def db_connect(self):
        # Try to connect to the database.
        try:
            self.db = await asyncpg.create_pool(**config.DB_CONN_INFO)
            print(f"\n[DB] Connected to database.")

            # Create tables if the dont exist.
            print("\n[DB] Creating tables.")
            with open("schema.sql") as r:
                await self.db.execute(r.read())
            print("[DB] Done creating tables.")

            # Tell the bot that the databse is ready.
            self.db_ready = True

        # Accept any exceptions we might find.
        except ConnectionRefusedError:
            print(f"\n[DB] Connection to database was denied.")
        except Exception as e:
            print(f"\n[DB] An error occured: {e}")

    async def bot_start(self):
        await self.db_connect()
        await self.login(config.DISCORD_TOKEN)
        await self.connect()

    async def bot_close(self):
        await super().logout()
        await self.session.close()

    async def is_owner(self, user):
        # Allows me to set custom owners ids dynamically.
        return user.id in self.owner_ids

    async def on_message(self, message):
        # Ignore all other bots.
        if message.author.bot:
            return

        # Get the context of the message.
        ctx = await self.get_context(message)

        # If it was a command and the author is blacklisted, return.
        if ctx.command:
            if message.author.id in self.user_blacklist:
                return await message.channel.send(f"Sorry, you are blacklisted.")
            # Otherwise process the command.
            await self.process_commands(message)

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=MyContext)


class MyContext(commands.Context):

    @property
    def player(self):
        return self.bot.andesite.get_player(self.guild.id, cls=Player)

    async def paginate(self, **kwargs):
        # Get the aruguements.
        title = kwargs.get("title")
        entries = kwargs.get("entries")
        entries_per_page = kwargs.get("entries_per_page")

        # Start pagination
        paginator = Paginator(ctx=self, title=title,  entries=entries, entries_per_page=entries_per_page, total_entries=len(entries))
        return await paginator.paginate()

    async def paginate_embed(self, **kwargs):
        # Get the aruguements.
        title = kwargs.get("title")
        entries = kwargs.get("entries")
        entries_per_page = kwargs.get("entries_per_page")

        # Start pagination
        paginator = EmbedPaginator(ctx=self, title=title,  entries=entries, entries_per_page=entries_per_page, total_entries=len(entries))
        return await paginator.paginate()

    async def paginate_codeblock(self, **kwargs):
        # Get the aruguements.
        title = kwargs.get("title")
        entries = kwargs.get("entries")
        entries_per_page = kwargs.get("entries_per_page")

        # Start pagination
        paginator = CodeblockPaginator(ctx=self, title=title,  entries=entries, entries_per_page=entries_per_page, total_entries=len(entries))
        return await paginator.paginate()

    async def paginate_embeds(self, **kwargs):
        # Get the aruguements.
        entries = kwargs.get("entries")

        paginator = EmbedsPaginator(ctx=self, entries=entries)

        # Start pagination
        return await paginator.paginate()


if __name__ == "__main__":
    MrBot().run()
