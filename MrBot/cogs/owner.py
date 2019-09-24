from discord.ext import commands
from .utils import botUtils
import discord


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

        msg = ">>> "

        # Loop through bot.usage to get the guild and its command uses.
        for guild, usage in self.bot.stats.items():

            # Get the guild so we can have its name.
            guild = self.bot.get_guild(guild)
            msg += f"**{guild}:**\n"

            # Loop through the commands in the guild usages.
            for command in usage:
                msg += f"{command} : {usage[command]}\n"

            # Add a line between each guild.
            msg += "\n"

        # Send the message
        await ctx.send(msg)

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
    @commands.command(name="check_for_farms", hidden=True)
    async def check_for_farms(self, ctx, guilds_per_page=10):
        """
        Display how many bots/humans there are in each guild the bot can see.

        `guilds_per_page`: How many guilds to show per page, this is to reduce spam.
        """

        # Define a list of entries to paginate through.
        entries = []

        # Set a title for the paginator.
        title = "Guild id           |Total    |Humans   |Bots     |Name\n"

        # Loop through all the guilds the bot can see.
        for guild in self.bot.guilds:

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


def setup(bot):
    bot.add_cog(Owner(bot))
