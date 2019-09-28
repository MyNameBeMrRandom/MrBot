from discord.ext import commands
from .utils import exceptions
from .utils import formatting
import traceback
import andesite
import discord
import dbl


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def initiate_nodes(self):

        nodes = {"Node_1": {"ip": self.bot.config.IP_1,
                            "port": self.bot.config.PORT_1,
                            "rest_uri": self.bot.config.ADRESS_1,
                            "password": self.bot.config.PASSWORD_1,
                            "identifier": self.bot.config.IDENTIFIER_1,
                            }
                 }

        for n in nodes.values():
            try:
                await self.bot.andesite.start_node(
                    n["ip"],
                    n["port"],
                    rest_uri=n["rest_uri"],
                    password=n["password"],
                    identifier=n["identifier"]
                )
            except andesite.InvalidCredentials:
                print(f"\n[ANDESITE] Invalid credentials for node {n['identifier']}.")
                return
            except ConnectionRefusedError:
                print(f"Failed to connect to node {n['identifier']}")
                return
            print(f"\n[ANDESITE] Node {n['identifier']} connected.")

    @commands.Cog.listener()
    async def on_ready(self):

        print(f"\n[BOT] Logged in as {self.bot.user} - {self.bot.user.id}")

        # If we are connected to the database.
        if self.bot.db_ready is True:

            # Create config for bots guilds.
            print("\n[DB] Adding guilds.")

            # Loop through all the bots guilds.
            for guild in self.bot.guilds:

                # If the guild already has a config, skip it.
                if await self.bot.db.fetchrow("SELECT * FROM guild_config WHERE key = $1", guild.id):
                    continue

                # Else create a config for the guild.
                await self.bot.db.execute("INSERT INTO guild_config VALUES ($1)", guild.id)
                print(f"\n[DB] Created config for guild - {guild.name}.")

            print("[DB] Done adding guilds.")

        # Initialise andesite nodes.
        self.bot.andesite = andesite.Client(self.bot)
        await self.initiate_nodes()

        # Set our user/guild blacklists.
        blacklisted_users = await self.bot.db.fetch("SELECT * FROM user_blacklist")
        blacklisted_guilds = await self.bot.db.fetch("SELECT * FROM guild_blacklist")

        for i in range(len(blacklisted_users)):
            self.bot.user_blacklist.append(int(blacklisted_users[i]["id"]))
        for i in range(len(blacklisted_guilds)):
            self.bot.guild_blacklist.append(int(blacklisted_guilds[i]["id"]))

        # Leave any guilds that are blacklisted.
        for guild in self.bot.guilds:
            if guild.id in self.bot.guild_blacklist:
                await guild.leave()
                print(f"[BOT] Left blacklisted guild - {guild.id}")

    @commands.Cog.listener()
    async def on_resume(self):
        print(f"\n[BOT] Connection resumed.")

    @commands.Cog.listener()
    async def on_disconnect(self):
        print(f"\n[BOT] Disconnected.")

    @commands.Cog.listener()
    async def on_message(self, message):

        # If the message was not in a guild, return.
        if not message.guild:
            return

        # If we sent the message.
        if message.author.id == self.bot.user.id:

            # If the guild is not already in the dict, add it.
            if message.guild.id not in self.bot.stats:
                self.bot.stats[message.guild.id] = {}

            # If the value is not aleady in the guilds nested dict, add it
            if "MessagesSent" not in self.bot.stats[message.guild.id]:
                self.bot.stats[message.guild.id]["MessagesSent"] = 1

            # Else increment the value by 1.
            else:
                self.bot.stats[message.guild.id]["MessagesSent"] += 1

        # Track all message not sent by bots.
        if not message.author.bot:

            # If the guild is not already in the dict, add it.
            if message.guild.id not in self.bot.stats:
                self.bot.stats[message.guild.id] = {}

            # If the value is not aleady in the guilds nested dict, add it
            if "MessagesSeen" not in self.bot.stats[message.guild.id]:
                self.bot.stats[message.guild.id]["MessagesSeen"] = 1

            # Else increment the value by 1.
            else:
                self.bot.stats[message.guild.id]["MessagesSeen"] += 1

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        # If the edited message is not embedded or pinned, process it, this allow a user a message and run the command. Useful for misspellings.
        if not after.embeds and not after.pinned:
            await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        # Get the full command.
        parent = ctx.command.full_parent_name
        if parent:
            command = f"{parent} {ctx.command.name}"
        else:
            command = f"{ctx.command.name}"

        # If the guild is not already in the dict, add it.
        if ctx.guild.id not in self.bot.stats:
            self.bot.stats[ctx.guild.id] = {}

        # If the command is not aleady in the guilds nested dict, add it
        if command not in self.bot.stats[ctx.guild.id]:
            self.bot.stats[ctx.guild.id][command] = 1

        # Else increment the command by 1.
        else:
            self.bot.stats[ctx.guild.id][command] += 1

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # If the command has a local error handler, return
        if hasattr(ctx.command, "on_error"):
            return

        # Get the original exception or or if nothing is found keep the exception.
        error = getattr(error, "original", error)

        # Check for errors.
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"You missed the `{error.param}` parameter. You can use `{ctx.prefix}help {ctx.command}` for more information on what parameters to pass.")
        if isinstance(error, commands.TooManyArguments):
            return await ctx.send(f"You passed too many arguments to the command `{ctx.command}`. You can use `{ctx.prefix}help {ctx.command}` for more information on what arguments to pass.")
        if isinstance(error, commands.BadArgument):
            return await ctx.send(f"You passed a bad arguement to the command `{ctx.command}`.")
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.PrivateMessageOnly):
            return await ctx.send(f"The command `{ctx.command}` can only be used in DM's.")
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send(f"The command `{ctx.command}` can not be used in DM's.")
            except discord.Forbidden:
                return
        if isinstance(error, commands.NotOwner):
            return await ctx.send(f"The command `{ctx.command}` is owner only.")
        if isinstance(error, commands.MissingPermissions):
            missing_perms = ""
            for perm in error.missing_perms:
                missing_perms += f"\n> {perm}"
            return await ctx.send(f"You don't have the following permissions required to run the command `{ctx.command}`.\n{missing_perms}")
        if isinstance(error, commands.BotMissingPermissions):
            missing_perms = ""
            for perm in error.missing_perms:
                missing_perms += f"\n> {perm}"
            return await ctx.send(f"I am missing the following permissions to run the command `{ctx.command}`.\n{missing_perms}")
        if isinstance(error, commands.DisabledCommand):
            return await ctx.send(f"The command `{ctx.command}` is currently disabled.")
        if isinstance(error, commands.CommandOnCooldown):
            if error.cooldown.type == commands.BucketType.user:
                return await ctx.send(f"The command `{ctx.command}` is on cooldown for you, retry in `{formatting.get_time_friendly(error.retry_after)}`.")
            if error.cooldown.type == commands.BucketType.default:
                return await ctx.send(f"The command `{ctx.command}` is on cooldown for the whole bot, retry in `{formatting.get_time_friendly(error.retry_after)}`.")
            if error.cooldown.type == commands.BucketType.guild:
                return await ctx.send(f"The command `{ctx.command}` is on cooldown for this guild, retry in `{formatting.get_time_friendly(error.retry_after)}`.")
        if isinstance(error, exceptions.WrongGuild):
            return await ctx.send("This command can not be used in this guild.")

        # Print the error and traceback if it doesnt match any of the above.
        print(f"Ignoring exception in command {ctx.command}:")
        traceback.print_exception(type(error), error, error.__traceback__)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Log the guild that was joined.
        print(f"\n[BOT] Joined a guild - {guild.name}")

        if guild.id in self.bot.guild_blacklist:
            print(f"[BOT] Left blacklisted guild - {guild.name}")
            await guild.leave()

        # Create a config for the guild.
        if not await self.bot.db.fetchrow("SELECT * FROM guild_config WHERE key = $1", guild.id):
            await self.bot.db.execute("INSERT INTO guild_config VALUES ($1)", guild.id)
            print(f"\n[DB] Created config for guild - {guild.name}")

        # Try to update discord bot list guild count.
        try:
            await self.bot.dblpy.post_guild_count()
            print(f"\n[DBL] Posted guild count of {len(self.bot.guilds)}")
        except dbl.Forbidden:
            print("[DBL] Forbidden - Failed to post guild count")
        except dbl.Unauthorized:
            print("[DBL] Forbidden - Failed to post guild count")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        # Log the guild that was left.
        print(f"\n[BOT] Left a guild - {guild.name}")

        # Try to update discord bot list count.
        try:
            await self.bot.dblpy.post_guild_count()
            print(f"\n[DBL] Posted guild count of {len(self.bot.guilds)}")
        except dbl.Forbidden:
            print("[DBL] Forbidden - Failed to post guild count")
        except dbl.Unauthorized:
            print("[DBL] Forbidden - Failed to post guild count")


def setup(bot):
    bot.add_cog(Events(bot))
