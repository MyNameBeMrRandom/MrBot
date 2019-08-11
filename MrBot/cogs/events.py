from .utils import get_information
from discord.ext import commands
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
        await self.bot.log_channel.send(f'Joined a guild called `{guild.name}`')
        print(f'[BOT] Joined a guild called `{guild.name}`')
        if not await self.bot.pool.fetchrow("SELECT * FROM guild_config WHERE key = $1", guild.id):
            await self.bot.pool.execute(
                "INSERT INTO guild_config VALUES"
                "($1, 0, FALSE, FALSE, FALSE,"
                "FALSE, FALSE, FALSE, FALSE, FALSE,"
                "FALSE, FALSE, FALSE, FALSE, FALSE,"
                "FALSE, FALSE, FALSE, FALSE, FALSE,"
                "FALSE, FALSE, FALSE, FALSE, FALSE,"
                "FALSE, FALSE)", guild.id)
            print(f'[DB] Created config for guild - {guild.name}.')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.log_channel.send(f'Left a guild called `{guild.name}`')
        print(f'[BOT] Left a guild called `{guild.name}`')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == 424637852035317770:
            self.bot.messages_sent += 1
        if not message.author.bot:
            self.bot.messages_seen += 1

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        self.bot.commands_run += 1

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, 'original', error)
        if hasattr(ctx.command, 'on_error'):
            return
        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f"The command `{ctx.command}` is currently disabled.")
        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f"The command `{ctx.command}` is on cooldown, retry in {round(error.retry_after, 2)}s.")
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"You missed the `{error.param}` parameter.")
        elif isinstance(error, commands.TooManyArguments):
            return await ctx.send(f"Too many arguments were passed for the command `{ctx.command}`.")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(f"A bad argument was passed to the command `{ctx.command}`.")
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(f"You dont have the permissions to run the `{ctx.command}` command.")
        if isinstance(error, discord.Forbidden):
            return await ctx.send(f"I am missing permissions to run the command `{ctx.command}`.")
        elif isinstance(error, commands.CommandInvokeError):
            return await ctx.send(f"There was an error while running that command")
        elif isinstance(error, commands.NotOwner):
            return await ctx.send(f"This is an owner only command.")
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send(f"The command `{ctx.command}` cannot be used in private messages.")
            except Exception:
                pass
        elif isinstance(error, commands.BotMissingPermissions):
            missing_perms = ""
            for perms in error.missing_perms:
                missing_perms += f"\n>{perms}"
            return await ctx.send(f"I am missing the following permissions to run the command `{ctx.command}`\n{missing_perms}")
        else:
            try:
                print(f'{error.original.__class__.__name__}: {error.original}')
                traceback.print_tb(error.original.__traceback__)
            except AttributeError:
                print(f'{error.__class__.__name__}: {error}')
                traceback.print_tb(error.__traceback__)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        if self.bot.is_db_ready is False:
            return
        data = await self.bot.pool.fetchrow("SELECT * FROM guild_config WHERE key = $1", before.id)
        if data["logging_enabled"] is False:
            return
        if data["logging_channel"] == 0:
            return
        channel = self.bot.get_channel(data["logging_channel"])
        if not before.name == after.name:
            if data["guild_name"] is True:
                guild_name = before.name
                guild_avatar = before.icon_url
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f"This guilds name has changed.\n\n"
                )
                embed.set_author(icon_url=guild_avatar, name=guild_name)
                embed.description += f'**Before:**\n{before.name}\n**After:**\n{after.name}'
                return await channel.send(embed=embed)
        if not before.region == after.region:
            if data["guild_region"] is True:
                guild_name = before.name
                guild_avatar = before.icon_url
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f"This guilds region has changed.\n\n"
                )
                embed.set_author(icon_url=guild_avatar, name=guild_name)
                embed.description += f'**Before:**\n{get_information.guild_region(before)}\n**After:**\n{get_information.guild_region(after)}'
                return await channel.send(embed=embed)
        if not before.afk_timeout == after.afk_timeout:
            if data["guild_afk_timeout"] is True:
                guild_name = before.name
                guild_avatar = before.icon_url
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f"This guilds AFK timout has changed.\n\n"
                )
                embed.set_author(icon_url=guild_avatar, name=guild_name)
                embed.description += f'**Before:**\n{int(before.afk_timeout/60)} minutes\n**After:**\n{int(after.afk_timeout/60)} minutes'
                return await channel.send(embed=embed)
        if not before.afk_channel == after.afk_channel:
            if data["guild_afk_channel"] is True:
                guild_name = before.name
                guild_avatar = before.icon_url
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f"This guilds AFK voice channel has changed.\n\n"
                )
                embed.set_author(icon_url=guild_avatar, name=guild_name)
                embed.description += f'**Before:**\n{before.afk_channel.name}\n**After:**\n{after.afk_channel.name}'
                return await channel.send(embed=embed)
        if not before.system_channel == after.system_channel:
            if data["guild_system_channel"] is True:
                guild_name = before.name
                guild_avatar = before.icon_url
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f"This guilds system messages channel has changed.\n\n"
                )
                embed.set_author(icon_url=guild_avatar, name=guild_name)
                embed.description += f'**Before:**\n{before.system_channel.mention}\n**After:**\n{after.system_channel.mention}'
                return await channel.send(embed=embed)
        if not before.icon_url == after.icon_url:
            if data["guild_icon"] is True:
                guild_name = before.name
                guild_avatar = before.icon_url
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f"This guilds icon has changed.\n\n"
                )
                embed.set_author(icon_url=guild_avatar, name=guild_name)
                embed.description += f'**Before:**\n[Image]({before.icon_url})\n**After:**\n[Image]({after.icon_url})'
                return await channel.send(embed=embed)
        if not before.default_notifications == after.default_notifications:
            if data["guild_default_notifications"] is True:
                guild_name = before.name
                guild_avatar = before.icon_url
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f"This guilds default notification setting has changed.\n\n"
                )
                embed.set_author(icon_url=guild_avatar, name=guild_name)
                embed.description += f'**Before:**\n{get_information.guild_notification_level(before)}\n**After:**\n{get_information.guild_notification_level(after)}'
                return await channel.send(embed=embed)
        if not before.description == after.description:
            if data["guild_description"] is True:
                guild_name = before.name
                guild_avatar = before.icon_url
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f"This guilds description has changed.\n\n"
                )
                embed.set_author(icon_url=guild_avatar, name=guild_name)
                embed.description += f'**Before:**\n{before.description}\n**After:**\n{after.description}'
                return await channel.send(embed=embed)
        if not before.mfa_level == after.mfa_level:
            if data["guild_mfa_level"] is True:
                guild_name = before.name
                guild_avatar = before.icon_url
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f"This guilds MFA level has changed.\n\n"
                )
                embed.set_author(icon_url=guild_avatar, name=guild_name)
                embed.description += f'**Before:**\n{get_information.guild_mfa_level(before)}\n**After:**\n{get_information.guild_mfa_level(after)}'
                return await channel.send(embed=embed)
        if not before.verification_level == after.verification_level:
            if data["guild_verification_level"] is True:
                guild_name = before.name
                guild_avatar = before.icon_url
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f"This guilds verification level has changed.\n\n"
                )
                embed.set_author(icon_url=guild_avatar, name=guild_name)
                embed.description += f'**Before:**\n{get_information.guild_verification_level(before)}\n**After:**\n{get_information.guild_verification_level(after)}'
                return await channel.send(embed=embed)
        if not before.explicit_content_filter == after.explicit_content_filter:
            if data["guild_explict_content_filter"] is True:
                guild_name = before.name
                guild_avatar = before.icon_url
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f"This guilds explicit content filter has changed.\n\n"
                )
                embed.set_author(icon_url=guild_avatar, name=guild_name)
                embed.description += f'**Before:**\n{get_information.guild_content_filter_level(before)}\n**After:**\n{get_information.guild_content_filter_level(after)}'
                return await channel.send(embed=embed)
        if not before.splash == after.splash:
            if data["guild_splash"] is True:
                guild_name = before.name
                guild_avatar = before.icon_url
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f"This guilds splash has changed.\n\n"
                )
                embed.set_author(icon_url=guild_avatar, name=guild_name)
                embed.description += f'**Before:**\n{before.splash}\n**After:**\n{after.splash}'
                return await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        guild = message.guild
        if self.bot.is_db_ready is False:
            return
        if message.author.bot:
            return
        data = await self.bot.pool.fetchrow("SELECT * FROM guild_config WHERE key = $1", guild.id)
        if data["logging_enabled"] is False:
            return
        if data["logging_channel"] == 0:
            return
        channel = self.bot.get_channel(data["logging_channel"])
        if data['message_delete'] is True:
            author = message.author.name
            useravatar = message.author.avatar_url
            embed = discord.Embed(
                colour=0x57FFF5,
                description=f"**{message.author.name}**'s message in <#{message.channel.id}> was deleted.\n\n"
            )
            embed.set_author(icon_url=useravatar, name=author)
            if message.attachments:
                embed.description += f'**Message content:** [Attachment]({message.attachments[0].proxy_url})\n{message.content}'
                embed.set_image(url=message.attachments[0].proxy_url)
            else:
                embed.description += f'**Message content:**\n{message.content}'
            return await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        guild = before.guild
        if self.bot.is_db_ready is False:
            return
        if before.author.bot:
            return
        data = await self.bot.pool.fetchrow("SELECT * FROM guild_config WHERE key = $1", guild.id)
        if data["logging_enabled"] is False:
            return
        if data["logging_channel"] == 0:
            return
        channel = self.bot.get_channel(data["logging_channel"])
        if not before.pinned == after.pinned:
            if data['message_pin'] is True:
                author = after.author.name
                useravatar = after.author.avatar_url
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f"**{after.author.name}**'s message was pinned/unpinned.\n\n"
                )
                embed.set_author(icon_url=useravatar, name=author)
                if after.attachments:
                    embed.description += f'**Message content:** [Attachment]({after.attachments[0].url})\n{after.content}'
                else:
                    embed.description += f'**Message content:**\n{after.content}'
                return await channel.send(embed=embed)
        if not before.content == after.content:
            if data['message_edit'] is True:
                author = after.author.name
                useravatar = after.author.avatar_url
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f"**{after.author.name}**'s edited a message in <#{after.channel.id}>.\n\n"
                )
                embed.set_author(icon_url=useravatar, name=author)
                if before.attachments:
                    embed.description += f'**Before:** [Attachment]({before.attachments[0].url})\n{before.content}\n**After:** [Attachment]({before.attachments[0].url})\n{after.content}'
                else:
                    embed.description += f'**Before:**\n{before.content}\n**After:**\n{after.content}'
                return await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        if self.bot.is_db_ready is False:
            return
        data = await self.bot.pool.fetchrow("SELECT * FROM guild_config WHERE key = $1", guild.id)
        if data["logging_enabled"] is False:
            return
        if data["logging_channel"] == 0:
            return
        channel = self.bot.get_channel(data["logging_channel"])
        if data['member_join'] is True:
            author = member.name
            useravatar = member.avatar_url
            embed = discord.Embed(
                colour=0x57FFF5,
                description=f"**{member.name}** has joined the guild."
            )
            embed.set_author(icon_url=useravatar, name=author)
            embed.set_footer(text=f'ID: {member.id}')
            embed.set_thumbnail(url=member.avatar_url_as(format="png"))
            return await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        if self.bot.is_db_ready is False:
            return
        data = await self.bot.pool.fetchrow("SELECT * FROM guild_config WHERE key = $1", guild.id)
        if data["logging_enabled"] is False:
            return
        if data["logging_channel"] == 0:
            return
        channel = self.bot.get_channel(data["logging_channel"])
        if data['member_join'] is True:
            author = member.name
            useravatar = member.avatar_url
            embed = discord.Embed(
                colour=0x57FFF5,
                description=f"**{member.name}** has left the guild."
            )
            embed.set_author(icon_url=useravatar, name=author)
            embed.set_footer(text=f'ID: {member.id}')
            embed.set_thumbnail(url=member.avatar_url_as(format="png"))
            return await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild = before.guild
        if self.bot.is_db_ready is False:
            return
        if before.bot:
            return
        data = await self.bot.pool.fetchrow("SELECT * FROM guild_config WHERE key = $1", guild.id)
        if data["logging_enabled"] is False:
            return
        if data["logging_channel"] == 0:
            return
        channel = self.bot.get_channel(data["logging_channel"])
        if not before.status == after.status:
            if data["member_status"] is True:
                author = after.name
                useravatar = after.avatar_url
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f"**{before.name}**'s status has changed.\n\n"
                )
                embed.set_author(icon_url=useravatar, name=author)
                embed.description += f'**Before:**\n{get_information.user_status(before)}\n**After:**\n{get_information.user_status(after)}'
                return await channel.send(embed=embed)
        if not before.nick == after.nick:
            if data["member_nickname"] is True:
                author = after.name
                useravatar = after.avatar_url
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f"**{before.name}**'s nickname has changed.\n\n"
                )
                embed.set_author(icon_url=useravatar, name=author)
                embed.description += f'**Before:**\n{before.nick}\n**After:**\n{after.nick}'
                return await channel.send(embed=embed)
        if not before.roles == after.roles:
            if data["member_role"] is True:
                author = after.name
                useravatar = after.avatar_url
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f"**{before.name}**'s roles have changed.\n\n"
                )
                embed.set_author(icon_url=useravatar, name=author)
                embed.description += f'**Before:**\n{", ".join([r for r in before.roles])}\n**After:**\n{", ".join([r for r in after.roles])}'
                return await channel.send(embed=embed)
        if not before.activity == after.activity:
            try:
                if before.activity.name == after.activity.name:
                    return
            except AttributeError:
                pass
            if data["member_activity"] is True:
                author = after.name
                useravatar = after.avatar_url
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f"**{before.name}**'s activity has changed.\n\n"
                )
                embed.set_author(icon_url=useravatar, name=author)
                embed.description += f'**Before:**\n{get_information.user_activity(before)}\n**After:**\n{get_information.user_activity(after)}'
                return await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if self.bot.is_db_ready is False:
            return
        if before.bot:
            return
        for guild in self.bot.guilds:
            data = await self.bot.pool.fetchrow("SELECT * FROM guild_config WHERE key = $1", guild.id)
            if data["logging_enabled"] is False:
                return
            if data["logging_channel"] == 0:
                return
            channel = self.bot.get_channel(data["logging_channel"])
            if before or after not in guild.members:
                return
            if not before.name == after.name:
                if data["user_username"] is True:
                    author = after.name
                    useravatar = after.avatar_url
                    embed = discord.Embed(
                        colour=0x57FFF5,
                        description=f"**{after.name}**'s name has changed.\n\n"
                    )
                    embed.set_author(icon_url=useravatar, name=author)
                    embed.description += f'**Before:**\n{before.name}\n**After:**\n{after.name}'
                    return await channel.send(embed=embed)
            if not before.discriminator == after.discriminator:
                if data["user_discriminator"] is True:
                    author = after.name
                    useravatar = after.avatar_url
                    embed = discord.Embed(
                        colour=0x57FFF5,
                        description=f"**{after.name}**'s discriminator has changed.\n\n"
                    )
                    embed.set_author(icon_url=useravatar, name=author)
                    embed.description += f'**Before:**\n{before.discriminator}\n**After:**\n{after.discriminator}'
                    return await channel.send(embed=embed)
            if not before.avatar == after.avatar:
                if data["user_avatar"] is True:
                    author = after.name
                    useravatar = after.avatar_url
                    embed = discord.Embed(
                        colour=0x57FFF5,
                        description=f"**{after.name}**'s avatar has changed.\n\n"
                    )
                    embed.set_author(icon_url=useravatar, name=author)
                    embed.description += f'**Before:**\n{before.avatar_url}\n**After:**\n{after.avatar_url}'
                    return await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Events(bot))

