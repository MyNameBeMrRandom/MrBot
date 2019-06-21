from discord.ext import commands
from .utils import file_handling
import discord
import yaml
import time
import os



class Accounts(commands.Cog):
	"""
	Account commands.
	"""

	def __init__(self, bot):
		self.bot = bot

	def get_status_times(self, ctx):
		with open(f'data/accounts/{ctx.author.id}.yaml', 'r', encoding='utf8') as r:
			data = yaml.load(r, Loader=yaml.FullLoader)
			status_since = data['status_times'][f'{ctx.author.status}_since']
			status_time_before = time.time() - status_since
			current_status = round(status_time_before)
			online_time = data['status_times'][f'online_time']
			offline_time = data['status_times'][f'offline_time']
			idle_time = data['status_times'][f'idle_time']
			dnd_time = data['status_times'][f'dnd_time']
			if ctx.author.status == discord.Status.online:
				return online_time + current_status, offline_time, idle_time, dnd_time
			elif ctx.author.status == discord.Status.offline:
				return online_time, offline_time + current_status, idle_time, dnd_time
			elif ctx.author.status == discord.Status.idle:
				return online_time, offline_time, idle_time + current_status, dnd_time
			elif ctx.author.status == discord.Status.dnd:
				return online_time, offline_time, idle_time, dnd_time + current_status
			else:
				return online_time, offline_time, idle_time, dnd_time

	def calculate_status_times(self, times):
		minute, second = divmod(times, 60)
		hour, minute = divmod(minute, 60)
		day, hour = divmod(hour, 24)
		days = round(day)
		hours = round(hour)
		minutes = round(minute)
		seconds = round(second)
		return f'{days}d, {hours}h, {minutes}m, {seconds}s'

	def calculate_status_percent(self, online, offline, idle, dnd):
		total = online + offline + idle + dnd
		online_p = online / total
		offline_p = offline / total
		idle_p = idle / total
		dnd_p = dnd / total
		online_percent = round(online_p * 100, 3)
		offline_percent = round(offline_p * 100, 3)
		idle_percent = round(idle_p * 100, 3)
		dnd_percent = round(dnd_p * 100, 3)
		return online_percent, offline_percent, idle_percent, dnd_percent

	def get_information(self, ctx):
		with open(f'data/accounts/{ctx.author.id}.yaml', 'r', encoding='utf8') as r:
			data = yaml.load(r, Loader=yaml.FullLoader)
			background = data['config']['background']
			bank = data['economy']['bank']
			cash = data['economy']['cash']
			timezone = data['info']['timezone']
			votes = data['info']['votes']
			return background, bank, cash, timezone, votes

	@commands.group(name='account', aliases=['profile'], hidden=True)
	async def account(self, ctx):
		"""
		Display information about your account.
		"""
		message = f"__**Information about {ctx.author.name}'s account.**__\n\n"
		try:
			online_time, offline_time, idle_time, dnd_time = await self.bot.loop.run_in_executor(None, self.get_status_times, ctx)
			total_time = online_time + offline_time + idle_time + dnd_time
			online = self.calculate_status_times(online_time)
			offline = self.calculate_status_times(offline_time)
			idle = self.calculate_status_times(idle_time)
			dnd = self.calculate_status_times(dnd_time)
			total= self.calculate_status_times(total_time)
			online_percent, offline_percent, idle_percent, dnd_percent = self.calculate_status_percent(online_time, offline_time, idle_time, dnd_time)
			total_percent = round(offline_percent + online_percent + idle_percent + dnd_percent, 2)
			message += (f'**Status times:**\n'
			            f'**Online:**  | {online} | {online_percent}%\n'
			            f'**Offline:** | {offline} | {offline_percent}%\n'
			            f'**Idle:**       | {idle} | {idle_percent}%\n'
			            f'**DnD:**      | {dnd} | {dnd_percent}%\n'
			            f'**Total:**     | {total} | {total_percent}%\n\n')
			background, bank, cash, timezone, votes = await self.bot.loop.run_in_executor(None, self.get_information, ctx)
			message += (f'**Configuration:**\n'
			            f'**Background:** {background}\n\n')
			message += (f'**Economy information:**\n'
			            f'**Bank:** £{bank}\n'
			            f'**Cash:** £{cash}\n\n')
			message += (f'**General information:**\n'
			            f'**Timezone:** {timezone}\n'
			            f'**Votes:** {votes}\n')
			return await ctx.send(message)
		except FileNotFoundError:
			await ctx.send('You dont have an account.\n')
			return await file_handling.account_creation(ctx)

	@account.command(name='create', hidden=True)
	async def create_account(self, ctx):
		"""
		Creates an account with your user ID.
		"""
		try:
			return await file_handling.account_creation(ctx)
		except FileExistsError:
			return await ctx.send(f'You already have an account.')

	@account.command(name='delete')
	async def delete_account(self, ctx):
		"""
		Deletes your account.
		"""
		try:
			os.remove(f'data/accounts/{ctx.author.id}.yaml')
			return await ctx.send('Deleted your account.')
		except FileNotFoundError:
			await ctx.send(f'You dont have an account.')
			return await file_handling.account_creation(ctx)


def setup(bot):
	bot.add_cog(Accounts(bot))
