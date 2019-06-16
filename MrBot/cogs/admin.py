from discord.ext import commands
from .utils import file_handling
import discord
import yaml
import os


# noinspection PyMethodMayBeStatic
class Admin(commands.Cog):
	"""
	Guild admininstation commands.
	"""

	def __init__(self, bot):
		self.bot = bot

	def get_logging_channel(self, ctx):
		with open(f'data/guilds/{ctx.guild.id}.yaml', 'r', encoding='utf8') as r:
			data = yaml.load(r, Loader=yaml.FullLoader)
			logging_channel = data['config']['logging_channel']
			if logging_channel is None:
				return f'This guild does not have logging enabled.'
			else:
				return f'This guilds logging channel is <#{logging_channel}>.'

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

	@commands.group(name='config', aliases=['cfg'], invoke_without_command=True)
	async def config(self, ctx):
		"""
		Display information about the current guilds config.
		"""
		await ctx.send('config stuff.')

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
			await ctx.send(f'This guild does not have a config')
			return await file_handling.config_creation(ctx)

	@commands.group(name='logging', invoke_without_command=True)
	async def logging(self, ctx):
		"""
		Get information about the guilds logging status.
		"""
		try:
			logging_channel = await ctx.bot.loop.run_in_executor(None, self.get_logging_channel, ctx)
			return await ctx.send(logging_channel)
		except FileNotFoundError:
			await ctx.send(f'This guild does not have logging enabled.')
			return await file_handling.config_creation(ctx)

	@logging.command(name='set_channel', aliases=['set_c'])
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
		Enable logging in this guild.
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
		Disable logging in this guild.
		"""
		try:
			logging_disable = await ctx.bot.loop.run_in_executor(None, self.disable_logging, ctx)
			return await ctx.send(logging_disable)
		except FileNotFoundError:
			await ctx.send(f'This guild does not have a config file.')
			return await file_handling.config_creation(ctx)


def setup(bot):
	bot.add_cog(Admin(bot))
