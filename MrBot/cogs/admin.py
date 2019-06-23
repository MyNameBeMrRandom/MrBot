from discord.ext import commands
from .utils import file_handling
import discord
import yaml
import os


# noinspection PyMethodMayBeStatic
class Admin(commands.Cog):
	"""
	Guild administration commands.
	"""

	def __init__(self, bot):
		self.bot = bot

	def get_logging_channel(self, ctx):
		with open(f'data/guilds/{ctx.guild.id}.yaml', 'r', encoding='utf8') as r:
			data = yaml.load(r, Loader=yaml.FullLoader)
			logging_channel = data['config']['logging_channel']
			if logging_channel is None:
				return f'None'
			else:
				return f'<#{logging_channel}>'

	def get_logging_status(self, ctx):
		with open(f'data/guilds/{ctx.guild.id}.yaml', 'r', encoding='utf8') as r:
			data = yaml.load(r, Loader=yaml.FullLoader)
			logging_status = data['config']['logging_enabled']
			if logging_status is False:
				return f'Disabled'
			else:
				return f'Enabled'

	def set_logging_channel(self, ctx, channel):
		with open(f'data/guilds/{ctx.guild.id}.yaml', 'r', encoding='utf8') as r:
			data = yaml.load(r, Loader=yaml.FullLoader)
			logging_channel = data['config']['logging_channel']
			if logging_channel == channel.id:
				return 'That is already the guilds logging channel.'
			else:
				data['config']['logging_channel'] = channel.id
				with open(f'data/guilds/{ctx.guild.id}.yaml', 'w', encoding='utf8') as w:
					yaml.dump(data, w)
					return f'Changed this guilds logging channel to <#{channel.id}>.'

	def enable_logging(self, ctx):
		with open(f'data/guilds/{ctx.guild.id}.yaml', 'r', encoding='utf8') as r:
			data = yaml.load(r, Loader=yaml.FullLoader)
			logging_enabled = data['config']['logging_enabled']
			if logging_enabled is True:
				return 'Logging is already enabled in this guild.'
			else:
				data['config']['logging_enabled'] = True
				with open(f'data/guilds/{ctx.guild.id}.yaml', 'w', encoding='utf8') as w:
					yaml.dump(data, w)
					return f'Enabled logging in this guild.'

	def disable_logging(self, ctx):
		with open(f'data/guilds/{ctx.guild.id}.yaml', 'r', encoding='utf8') as r:
			data = yaml.load(r, Loader=yaml.FullLoader)
			logging_enabled = data['config']['logging_enabled']
			if logging_enabled is False:
				return 'Logging is already disabled in this guild.'
			else:
				data['config']['logging_enabled'] = False
				with open(f'data/guilds/{ctx.guild.id}.yaml', 'w', encoding='utf8') as w:
					yaml.dump(data, w)
					return f'Disabled logging in this guild.'

	@commands.group(name='config')
	async def config(self, ctx):
		"""
		Display information about the current guilds config.
		"""
		message = f"__**Information about the config of {ctx.guild.name}**__\n\n"
		try:
			logging_channel = await ctx.bot.loop.run_in_executor(None, self.get_logging_channel, ctx)
			logging_status = await ctx.bot.loop.run_in_executor(None, self.get_logging_status, ctx)
			member_activity = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'member_activity')
			member_join = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'member_join')
			member_leave = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'member_leave')
			member_nickname = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'member_nickname')
			member_role = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'member_role')
			member_status = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'member_status')
			message_delete = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'message_delete')
			message_edit = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'message_edit')
			message_pin = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'message_pin')
			user_avatar = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'user_avatar')
			user_discriminator = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'user_discriminator')
			user_username = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'user_username')
			guild_name = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'guild_name')
			guild_region = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'guild_region')
			guild_afk_timeout = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'guild_afk_timeout')
			guild_afk_channel = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'guild_afk_channel')
			guild_system_channel = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'guild_system_channel')
			guild_icon = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'guild_icon')
			guild_default_notifications = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'guild_default_notifications')
			guild_description = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'guild_description')
			guild_mfa_level = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'guild_mfa_level')
			guild_verification_level = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'guild_verification_level')
			guild_explicit_content_filter = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'guild_explicit_content_filter')
			guild_splash = await ctx.bot.loop.run_in_executor(None, file_handling.get_guild_data, ctx.guild, 'logging', 'guild_splash')
			if member_activity is True:
				member_activity = 'Enabled'
			else:
				member_activity = 'Disabled'
			if member_join is True:
				member_join = 'Enabled'
			else:
				member_join = 'Disabled'
			if member_leave is True:
				member_leave = 'Enabled'
			else:
				member_leave = 'Disabled'
			if member_nickname is True:
				member_nickname = 'Enabled'
			else:
				member_nickname = 'Disabled'
			if member_role is True:
				member_role = 'Enabled'
			else:
				member_role = 'Disabled'
			if member_status is True:
				member_status = 'Enabled'
			else:
				member_status = 'Disabled'
			if message_delete is True:
				message_delete = 'Enabled'
			else:
				message_delete = 'Disabled'
			if message_edit is True:
				message_edit = 'Enabled'
			else:
				message_edit = 'Disabled'
			if message_pin is True:
				message_pin = 'Enabled'
			else:
				message_pin = 'Disabled'
			if user_avatar is True:
				user_avatar = 'Enabled'
			else:
				user_avatar = 'Disabled'
			if user_discriminator is True:
				user_discriminator = 'Enabled'
			else:
				user_discriminator = 'Disabled'
			if user_username is True:
				user_username = 'Enabled'
			else:
				user_username = 'Disabled'
			if guild_name is True:
				guild_name = 'Enabled'
			else:
				guild_name = 'Disabled'
			if guild_region is True:
				guild_region = 'Enabled'
			else:
				guild_region = 'Disabled'
			if guild_afk_timeout is True:
				guild_afk_timeout = 'Enabled'
			else:
				guild_afk_timeout = 'Disabled'
			if guild_afk_channel is True:
				guild_afk_channel = 'Enabled'
			else:
				guild_afk_channel = 'Disabled'
			if guild_system_channel is True:
				guild_system_channel = 'Enabled'
			else:
				guild_system_channel = 'Disabled'
			if guild_icon is True:
				guild_icon = 'Enabled'
			else:
				guild_icon = 'Disabled'
			if guild_default_notifications is True:
				guild_default_notifications = 'Enabled'
			else:
				guild_default_notifications = 'Disabled'
			if guild_description is True:
				guild_description = 'Enabled'
			else:
				guild_description = 'Disabled'
			if guild_mfa_level is True:
				guild_mfa_level = 'Enabled'
			else:
				guild_mfa_level = 'Disabled'
			if guild_verification_level is True:
				guild_verification_level = 'Enabled'
			else:
				guild_verification_level = 'Disabled'
			if guild_explicit_content_filter is True:
				guild_explicit_content_filter = 'Enabled'
			else:
				guild_explicit_content_filter = 'Disabled'
			if guild_splash is True:
				guild_splash = 'Enabled'
			else:
				guild_splash = 'Disabled'
			message += f'**Logging status:** {logging_status}\n'\
					f'**Logging channel:** {logging_channel}\n\n'\
					f'**Member Activity:** {member_activity}\n' \
					f'**Member joins:** {member_join}\n' \
					f'**Member leaves:** {member_leave}\n' \
					f'**Member nicknames:** {member_nickname}\n' \
					f'**Member roles:** {member_role}\n' \
					f'**Member status:** {member_status}\n' \
					f'**Message deletes:** {message_delete}\n' \
					f'**Message edits:** {message_edit}\n' \
					f'**Message pins:** {message_pin}\n' \
					f'**User avatar:** {user_avatar}\n' \
					f'**User discriminator:** {user_discriminator}\n' \
					f'**User username:** {user_discriminator}\n' \
					f'**Guild name:** {guild_name}\n' \
					f'**Guild AFK timeout time:** {guild_afk_timeout}\n' \
					f'**Guild AFK voice channel:** {guild_afk_channel}\n' \
					f'**Guild system channel:** {guild_system_channel}\n' \
					f'**Guild icon:** {guild_icon}\n' \
					f'**Guild default notifications:** {guild_default_notifications}\n' \
					f'**Guild description:** {guild_description}\n' \
					f'**Guild MFA level:** {guild_mfa_level}\n' \
					f'**Guild verfication level:** {guild_verification_level}\n' \
					f'**Guild explicit content filter:** {guild_explicit_content_filter}\n' \
					f'**Guild splash:** {guild_splash}\n\n' \
					f'**Note:** This extension is currently a work in progress so you can not change the logging settings at this point in time.'
			return await ctx.send(message)
		except FileNotFoundError:
			await ctx.send('This guild does not have a config file.\n')
			return await file_handling.config_creation(ctx)

	@config.command(name='create')
	async def create_config(self, ctx):
		"""
		Create a config file for the current guild.
		"""
		try:
			return await file_handling.config_creation(ctx)
		except FileExistsError:
			return await ctx.send(f'This guild already has a config.')

	@config.command(name='delete')
	async def delete_config(self, ctx):
		"""
		Deletes the current guilds config.
		"""
		try:
			os.remove(f'data/guilds/{ctx.guild.id}.yaml')
			return await ctx.send('Deleted this guilds config.')
		except FileNotFoundError:
			return await ctx.send(f'This guild does not have a config')

	@commands.group(name='logging')
	async def logging(self, ctx):
		"""
		Get information about the guilds logging status.
		"""
		try:
			logging_channel = await ctx.bot.loop.run_in_executor(None, self.get_logging_channel, ctx)
			logging_status = await ctx.bot.loop.run_in_executor(None, self.get_logging_status, ctx)
			return await ctx.send(f'**Logging status:** {logging_status}\n**Logging channel:** {logging_channel}')
		except FileNotFoundError:
			await ctx.send(f'This guild does not have a config file.')
			return await file_handling.config_creation(ctx)

	@logging.command(name='set_channel', aliases=['set_c', 'sc'])
	async def logging_set_channel(self, ctx, channel: discord.TextChannel = None):
		"""
		Set the guilds logging channel.
		"""
		if not channel:
			channel = ctx.channel
		try:
			logging_channel = await ctx.bot.loop.run_in_executor(None, self.set_logging_channel, ctx, channel)
			return await ctx.send(logging_channel)
		except FileNotFoundError:
			await ctx.send(f'This guild does not have a config file.')
			return await file_handling.config_creation(ctx)

	@logging.command(name='enable')
	async def logging_enable(self, ctx):
		"""
		Enable logging in the current guild.
		"""
		try:
			logging_enable = await ctx.bot.loop.run_in_executor(None, self.enable_logging, ctx)
			return await ctx.send(logging_enable)
		except FileNotFoundError:
			await ctx.send(f'This guild does not have a config file.')
			return await file_handling.config_creation(ctx)

	@logging.command(name='disable')
	async def logging_disable(self, ctx):
		"""
		Disable logging in the current guild.
		"""
		try:
			logging_disable = await ctx.bot.loop.run_in_executor(None, self.disable_logging, ctx)
			return await ctx.send(logging_disable)
		except FileNotFoundError:
			await ctx.send(f'This guild does not have a config file.')
			return await file_handling.config_creation(ctx)


def setup(bot):
	bot.add_cog(Admin(bot))
