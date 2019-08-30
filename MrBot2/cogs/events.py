from discord.ext import commands
from .utils import formatting
import traceback
import discord


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Log the guild that was joined.
        await self.bot.log_channel.send(f"Joined a guild called `{guild.name}`")
        print(f"[BOT] Joined a guild called `{guild.name}`")

        # Create a config for the guild.
        if not await self.bot.pool.fetchrow("SELECT * FROM guild_config WHERE key = $1", guild.id):
            await self.bot.pool.execute("INSERT INTO guild_config VALUES ($1)", guild.id)
            print(f"\n[DB] Created config for guild - {guild.name}.")

        # Try to update discord bot list guild count.
        try:
            await self.bot.dblpy.post_guild_count()
            print(f"\n[DBL] Posted guild count of {len(self.bot.guilds)}")
        except discord.Forbidden:
            print("\n[DBL] Forbidden - Failed to post guild count")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        # Log the guild that was left.
        await self.bot.log_channel.send(f"Left a guild called `{guild.name}`")
        print(f"\n[BOT] Left a guild called `{guild.name}`")

        # Try to update discord bot list count.
        try:
            await self.bot.dblpy.post_guild_count()
            print(f"\n[DBL] Posted guild count of {len(self.bot.guilds)}")
        except discord.Forbidden:
            print("\n[DBL] Forbidden - Failed to post guild count")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        # If the edited message is not embedded or pinned, process it, this allow a user a message and run the command. Useful for misspellings.
        if not after.embeds and not after.pinned:
            await self.bot.process_commands(after)

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

        # Print the error and traceback if it doesnt match any of the above.
        print(f"Ignoring exception in command {ctx.command}:")
        traceback.print_exception(type(error), error, error.__traceback__)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        # Get the full command.
        parent = ctx.command.full_parent_name
        if parent:
            command = f"{parent} {ctx.command.name}"
        else:
            command = f"{ctx.command.name}"

        # If the guild is not already in the dict, add it.
        if ctx.guild.id not in self.bot.usage:
            self.bot.usage[ctx.guild.id] = {}

        # If the command is not aleady in the guilds nested dict, add it
        if command not in self.bot.usage[ctx.guild.id]:
            self.bot.usage[ctx.guild.id][command] = 1

        # Else increment the command by 1.
        else:
            self.bot.usage[ctx.guild.id][command] += 1

    @commands.Cog.listener()
    async def on_message(self, message):

        if not message.guild:
            return
        
        # If we sent the message.
        if message.author.id == self.bot.user.id:

            # If the guild is not already in the dict, add it.
            if message.guild.id not in self.bot.usage:
                self.bot.usage[message.guild.id] = {}

            # If the value is not aleady in the guilds nested dict, add it
            if "MessagesSent" not in self.bot.usage[message.guild.id]:
                self.bot.usage[message.guild.id]["MessagesSent"] = 1

            # Else increment the value by 1.
            else:
                self.bot.usage[message.guild.id]["MessagesSent"] += 1

        # Track all message not sent by bots.
        if not message.author.bot:

            # If the guild is not already in the dict, add it.
            if message.guild.id not in self.bot.usage:
                self.bot.usage[message.guild.id] = {}

            # If the value is not aleady in the guilds nested dict, add it
            if "MessagesSeen" not in self.bot.usage[message.guild.id]:
                self.bot.usage[message.guild.id]["MessagesSeen"] = 1

            # Else increment the value by 1.
            else:
                self.bot.usage[message.guild.id]["MessagesSeen"] += 1


def setup(bot):
    bot.add_cog(Events(bot))
