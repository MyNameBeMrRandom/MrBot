from discord.ext import commands
from .utils import calculations
from .utils import exceptions
import traceback
import discord


class Events(commands.Cog):
    """
    Bot related events.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Log which guild was joined.
        await self.bot.log_channel.send(f"Joined a guild called `{guild.name}`")
        print(f"[BOT] Joined a guild called `{guild.name}`")
        # Create a config for the guild.
        if not await self.bot.pool.fetchrow("SELECT * FROM guild_config WHERE key = $1", guild.id):
            await self.bot.pool.execute("INSERT INTO guild_config VALUES ($1)", guild.id)
            print(f"[DB] Created config for guild - {guild.name}.")
        # Try to update discord bot list guild count.
        try:
            await self.bot.dblpy.post_guild_count()
            print(f"[DBL] Posted guild count of {len(self.bot.guilds)}")
        except discord.Forbidden:
            print("[DBL] Forbidden - Failed to post guild count")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        # Log which guild was left.
        await self.bot.log_channel.send(f"Left a guild called `{guild.name}`")
        print(f"[BOT] Left a guild called `{guild.name}`")
        # Try to update discord bot list count.
        try:
            await self.bot.dblpy.post_guild_count()
            print(f"[DBL] Posted guild count of {len(self.bot.guilds)}")
        except discord.Forbidden:
            print("[DBL] Forbidden - Failed to post guild count")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Log message stats.
        if message.author.id == 424637852035317770:
            self.bot.messages_sent += 1
        if not message.author.bot:
            self.bot.messages_seen += 1

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        # Log command stats.
        self.bot.commands_run += 1

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
                return await ctx.send(f"The command `{ctx.command}` is on cooldown for you, retry in `{calculations.get_time_friendly(error.retry_after)}`.")
            if error.cooldown.type == commands.BucketType.default:
                return await ctx.send(f"The command `{ctx.command}` is on cooldown for the whole bot, retry in `{calculations.get_time_friendly(error.retry_after)}`.")
            if error.cooldown.type == commands.BucketType.guild:
                return await ctx.send(f"The command `{ctx.command}` is on cooldown for this guild, retry in `{calculations.get_time_friendly(error.retry_after)}`.")
        if isinstance(error, exceptions.UserNotInVoiceChannel):
            return await ctx.send(f'You must be in a voice channel to use this command.')
        # Print the error and traceback if it doesnt match any of these.
        print(f"Ignoring exception in command {ctx.command}:")
        traceback.print_exception(type(error), error, error.__traceback__)


def setup(bot):
    bot.add_cog(Events(bot))

