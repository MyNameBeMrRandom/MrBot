from discord.ext import commands
from .utils import botUtils
import discord
import asyncpg


class Owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(name="stats", hidden=True)
    async def stats(self, ctx):
        """
        Show command usage/message stats.
        """

        # If no stats have been collected yet.
        if not self.bot.stats:
            return await ctx.send("No usage of commands yet.")

        # Define a list to store embeds in.
        embeds = []

        # Loop through bot.usage to get the guild and its command uses.
        for guild, usage in self.bot.stats.items():

            # Get the guild by its stored id.
            guild = self.bot.get_guild(guild)

            # Create the embed.
            embed = discord.Embed(
                title=f"{guild.name} ({guild.id})",
                description=f"",
                color=0xFF0000
            )
            for command in usage:
                embed.description += f"{command} : {usage[command]}\n"
            embeds.append(embed)

        # Send the message
        return await ctx.paginate_embeds(entries=embeds)

    @commands.is_owner()
    @commands.command(name="guilds", hidden=True)
    async def guilds(self, ctx):
        """
        Display information about all the different guilds the bot is in.
        """

        # Define a list for all the embed objects.
        embeds = []

        # Loop through all bots guilds and create an embed for each one.
        for guild in self.bot.guilds:
            online, offline, idle, dnd = botUtils.guild_user_status_count(guild)
            embed = discord.Embed(
                colour=0xFF0000,
                title=f"{guild.name}'s Stats and Information."
            )
            embed.set_footer(text=f"ID: {guild.id}")
            embed.add_field(name="__**General information:**__", value=f"**Owner:** {guild.owner}\n"
                                                                       f"**Server created at:** {guild.created_at.__format__('%A %d %B %Y at %H:%M')}\n"
                                                                       f"**Members:** {guild.member_count} |"
                                                                       f"<:online:608059247099379732>{online} |"
                                                                       f"<:idle:608059272923709441>{idle} |"
                                                                       f"<:dnd:608059261678911582>{dnd} |"
                                                                       f"<:offline:608059228191719424>{offline}\n"
                                                                       f"**Verification level:** {botUtils.guild_verification_level(guild)}\n"
                                                                       f"**Content filter level:** {botUtils.guild_content_filter_level(guild)}\n"
                                                                       f"**2FA:** {botUtils.guild_mfa_level(guild)}\n"
                                                                       f"**Role Count:** {len(guild.roles)}\n", inline=False)
            embed.add_field(name="__**Channels:**__", value=f"**Text channels:** {len(guild.text_channels)}\n"
                                                            f"**Voice channels:** {len(guild.voice_channels)}\n"
                                                            f"**Voice region:** {botUtils.guild_region(guild)}\n"
                                                            f"**AFK timeout:** {int(guild.afk_timeout / 60)} minutes\n"
                                                            f"**AFK channel:** {guild.afk_channel}\n", inline=False)
            embed.set_thumbnail(url=guild.icon_url)

            # Append the embed to the list of embeds.
            embeds.append(embed)

        # Paginate the list of embeds.
        return await ctx.paginate_embeds(entries=embeds)

    @commands.is_owner()
    @commands.command(name="guild_farms", hidden=True)
    async def guild_farms(self, ctx, guilds_per_page=15):
        """
        Display how many bots/humans there are in each guild the bot can see.

        `guilds_per_page`: How many guilds to show per page, this is to reduce spam.
        """

        # Define a key to sort guilds by.
        def key(e):
            return sum([m.bot for m in e.members])

        # Define a list of entries to paginate through.
        entries = []

        # Set a title for the paginator.
        title = "Guild id           |Total    |Humans   |Bots     |Name\n"

        # Loop through all the guilds the bot can see.
        for guild in sorted(self.bot.guilds, key=key, reverse=True):

            # Count how many members are bot/humans.
            bots = 0
            humans = 0
            total = 0
            for member in guild.members:
                if member.bot:
                    bots += 1
                else:
                    humans += 1
                total += 1

            # Create a message with the current guilds information.
            message = f"{guild.id} |{total}{' ' * int(9 - len(str(total)))}|{humans}{' ' * int(9 - len(str(humans)))}|{bots}{' ' * int(9 - len(str(bots)))}|{guild.name}"

            # Append the message to the list of entries.
            entries.append(message)

        # Paginate the entries.
        return await ctx.paginate_codeblock(entries=entries, entries_per_page=guilds_per_page, title=title)

    @commands.is_owner()
    @commands.group(name="blacklist", invoke_without_command=True)
    async def blacklist(self, ctx):
        return await ctx.send("Please choose a valid subcommand.")

    @commands.is_owner()
    @blacklist.group(name="user", invoke_without_command=True)
    async def blacklist_user(self, ctx):
        blacklisted = []
        blacklist = await self.bot.db.fetch("SELECT * FROM user_blacklist")
        if not blacklist:
            return await ctx.send("No blacklisted users.")
        for entry in blacklist:
            user = self.bot.get_user(entry['id'])
            if not user:
                blacklisted.append(f"User not found - {entry['id']} - Reason: {entry['reason']}")
            else:
                blacklisted.append(f"{user.name} - {user.id} - Reason: {entry['reason']}")
        return await ctx.paginate_codeblock(entries=blacklisted, entries_per_page=10, title=f"Showing {len(blacklisted)} blacklisted users.\n\n")

    @commands.is_owner()
    @blacklist_user.command(name="add")
    async def blacklist_user_add(self, ctx, user: int = None, *, reason=None):
        if not reason:
            reason = "No reason"
        if len(reason) > 512:
            return await ctx.caution("The reason can't be more than 512 characters.")
        if not user:
            return await ctx.send("You must specify a user id.")
        try:
            user = await self.bot.fetch_user(user)
            self.bot.guild_blacklist.append(user.id)
            await self.bot.db.execute("INSERT INTO user_blacklist (id, reason) VALUES ($1, $2)", user.id, reason)
            return await ctx.send(f"User: `{user.name} - {user.id}` has been blacklisted with reason `{reason}`")
        except asyncpg.UniqueViolationError:
            return await ctx.send("That user is already blacklisted.")

    @commands.is_owner()
    @blacklist_user.command(name="remove")
    async def blacklist_user_remove(self, ctx, user: int = None):
        if not user:
            return await ctx.send("You must specify a user id.")
        try:
            user = await self.bot.fetch_user(user)
            self.bot.guild_blacklist.remove(user.id)
            await self.bot.db.execute("DELETE FROM user_blacklist WHERE id = $1", user.id)
            return await ctx.send(f"User: `{user.name} - {user.id}` has been unblacklisted.")
        except ValueError:
            return await ctx.send(f"User: `{user.name} - {user.id}` is not blacklisted.")

    @commands.is_owner()
    @blacklist.group(name="guild", invoke_without_command=True)
    async def blacklist_guild(self, ctx):
        blacklisted = []
        blacklist = await self.bot.db.fetch("SELECT * FROM guild_blacklist")
        if not blacklist:
            return await ctx.send("No blacklisted guilds.")
        for entry in blacklist:
            blacklisted.append(f"{entry['id']} - Reason: {entry['reason']}")
        return await ctx.paginate_codeblock(entries=blacklisted, entries_per_page=10, title=f"Showing {len(blacklisted)} blacklisted guilds.\n\n")

    @commands.is_owner()
    @blacklist_guild.command(name="add")
    async def blacklist_guild_add(self, ctx, guild: int = None, *, reason=None):
        if not reason:
            reason = "No reason"
        if len(reason) > 512:
            return await ctx.caution("The reason can't be more than 512 characters.")
        if not guild:
            return await ctx.send("You must specify a guild id.")
        try:
            self.bot.guild_blacklist.append(guild)
            await self.bot.db.execute("INSERT INTO guild_blacklist (id, reason) VALUES ($1, $2)", guild, reason)
            try:
                guild = await self.bot.fetch_guild(guild)
                await guild.leave()
            except discord.Forbidden:
                pass
            return await ctx.send(f"Guild: `{guild}` has been blacklisted with reason `{reason}`")
        except asyncpg.UniqueViolationError:
            return await ctx.send("That guild is already blacklisted.")

    @commands.is_owner()
    @blacklist_guild.command(name="remove")
    async def blacklist_guild_remove(self, ctx, guild: int = None):
        if not guild:
            return await ctx.send("You must specify a user id.")
        try:
            self.bot.guild_blacklist.remove(guild)
            await self.bot.db.execute("DELETE FROM guild_blacklist WHERE id = $1", guild)
            return await ctx.send(f"Guild: `{guild}` has been unblacklisted.")
        except ValueError:
            return await ctx.send(f"Guild: `{guild}` is not blacklisted.")


def setup(bot):
    bot.add_cog(Owner(bot))
