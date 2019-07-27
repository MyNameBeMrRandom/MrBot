from discord.ext import commands
import discord


class Admin(commands.Cog):
	"""
	Guild administration commands.
	"""

	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='config')
	async def config(self, ctx):
		"""
		Display information about the current guilds config.
		"""

		if not await self.bot.pool.fetchrow("SELECT key FROM guild_config WHERE key = $1", ctx.guild.id):
			return await ctx.send('This guild does not have a config, this should not happen.')
		message = f">>> __**Information about the config of {ctx.guild.name}**__\n\n"
		info = await self.bot.pool.fetchrow("SELECT * FROM guild_config WHERE key = $1", ctx.guild.id)
		message +=  f'**Logging info:**\n' \
					f'    **Logging status:** {info["logging_enabled"]}\n' \
					f'    **Logging channel:** {info["logging_channel"]}\n\n' \
					f'**Logging types:**\n' \
					f'    **Member Activity:** {info["member_activity"]}\n' \
					f'    **Member joins:** {info["member_join"]}\n' \
					f'    **Member leaves:** {info["member_leave"]}\n' \
					f'    **Member nicknames:** {info["member_nickname"]}\n' \
					f'    **Member roles:** {info["member_role"]}\n' \
					f'    **Member status:** {info["member_status"]}\n' \
					f'    **Message deletes:** {info["message_delete"]}\n' \
					f'    **Message edits:** {info["message_edit"]}\n' \
					f'    **Message pins:** {info["message_pin"]}\n' \
					f'    **User avatar:** {info["user_avatar"]}\n' \
					f'    **User discriminator:** {info["user_discriminator"]}\n' \
					f'    **User username:** {info["user_username"]}\n' \
					f'    **Guild name:** {info["guild_name"]}\n' \
					f'    **Guild region:** {info["guild_region"]}\n' \
					f'    **Guild AFK timeout time:** {info["guild_afk_timeout"]}\n' \
					f'    **Guild AFK voice channel:** {info["guild_afk_channel"]}\n' \
					f'    **Guild system channel:** {info["guild_system_channel"]}\n' \
					f'    **Guild icon:** {info["guild_icon"]}\n' \
					f'    **Guild default notifications:** {info["guild_default_notifications"]}\n' \
					f'    **Guild description:** {info["guild_description"]}\n' \
					f'    **Guild MFA level:** {info["guild_mfa_level"]}\n' \
					f'    **Guild verfication level:** {info["guild_verification_level"]}\n' \
					f'    **Guild explicit content filter:** {info["guild_explicit_content_filter"]}\n' \
					f'    **Guild splash:** {info["guild_splash"]}\n\n'.replace('False', 'Disabled').replace('True', 'Enabled')
		return await ctx.send(message)

	@commands.group(name='logging', invoke_without_command=True)
	async def logging(self, ctx):
		"""
		Get information about the guilds logging status.
		"""

		if not await self.bot.pool.fetchrow("SELECT key FROM guild_config WHERE key = $1", ctx.guild.id):
			return await ctx.send('This guild does not have a config, this should not happen.')
		info = await self.bot.pool.fetchrow("SELECT * FROM guild_config WHERE key = $1", ctx.guild.id)
		text = f'>>> __**Logging status for {ctx.guild.name}**__\n\n' \
		       f'**Logging status:** {info["logging_enabled"]}\n' \
		       f'**Logging channel:** {info["logging_channel"]}'.replace('False', 'Disabled').replace('True', 'Enabled')
		return await ctx.send(text)

	@logging.command(name='set_channel', aliases=['sc'])
	async def logging_set_channel(self, ctx, channel: discord.TextChannel = None):
		"""
		Set the guilds logging channel.
		"""

		if not await self.bot.pool.fetchrow("SELECT key FROM guild_config WHERE key = $1", ctx.guild.id):
			return await ctx.send('This guild does not have a config, this should not happen.')
		if not channel:
			channel = ctx.channel
		current_channel = await self.bot.pool.fetchrow("SELECT logging_channel FROM guild_config WHERE key = $1", ctx.guild.id)
		if current_channel["logging_channel"] == channel.id:
			return await ctx.send(f'This guilds logging channel is already {channel.mention}')
		await self.bot.pool.execute(f"UPDATE guild_config SET logging_channel = $1 WHERE key = $2", channel.id, ctx.guild.id)
		return await ctx.send(f'Set this guild logging channel to {channel.mention}')

	@logging.command(name='toggle')
	async def logging_toggle(self, ctx):
		"""
		Toggle logging in the current guild.
		"""

		if not await self.bot.pool.fetchrow("SELECT key FROM guild_config WHERE key = $1", ctx.guild.id):
			return await ctx.send('This guild does not have a config, this should not happen.')
		current = await self.bot.pool.fetchrow("SELECT logging_enabled FROM guild_config WHERE key = $1", ctx.guild.id)
		if current["logging_enabled"] is True:
			await self.bot.pool.execute(f"UPDATE guild_config SET logging_enabled = $1 WHERE key = $2", False, ctx.guild.id)
			return await ctx.send(f'Disabled logging for this guild.')
		if current["logging_enabled"] is False:
			await self.bot.pool.execute(f"UPDATE guild_config SET logging_enabled = $1 WHERE key = $2", True, ctx.guild.id)
			return await ctx.send(f'Enabled logging for this guild.')


def setup(bot):
	bot.add_cog(Admin(bot))
