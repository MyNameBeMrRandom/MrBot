from discord.ext import commands
from .utils import file_handling
from .utils import calculations
import os


# noinspection PyMethodMayBeStatic
class Accounts(commands.Cog):
	"""
	MrBot account management commands.
	"""

	def __init__(self, bot):
		self.bot = bot

	@commands.group(name='account', aliases=['profile'])
	async def account(self, ctx):
		"""
		Display information about your account.
		"""
		try:
			message = f"__**Information about {ctx.author.name}'s account.**__\n\n"
			# Get the times in seconds.
			online_time, offline_time, idle_time, dnd_time = await self.bot.loop.run_in_executor(None, file_handling.get_status_times, ctx)
			# Calculate the total time.
			total_time = online_time + offline_time + idle_time + dnd_time
			# Calculate and display each status in days, hour, minutes and seconds.
			online = calculations.calculate_status_times(online_time)
			offline = calculations.calculate_status_times(offline_time)
			idle = calculations.calculate_status_times(idle_time)
			dnd = calculations.calculate_status_times(dnd_time)
			total = calculations.calculate_status_times(total_time)
			# Calculate the percentages of each status and the total percent.
			online_percent, offline_percent, idle_percent, dnd_percent, total_percent = calculations.calculate_status_percentages(online_time, offline_time, idle_time, dnd_time)
			# Append to the message.
			message += (f'**Status times:**\n'
			            f'**Online:**  | {online} | {online_percent}%\n'
			            f'**Offline:** | {offline} | {offline_percent}%\n'
			            f'**Idle:**       | {idle} | {idle_percent}%\n'
			            f'**DnD:**      | {dnd} | {dnd_percent}%\n'
			            f'**Total:**     | {total} | {total_percent}%\n\n')
			# Get different data for the command.
			background = await self.bot.loop.run_in_executor(None, file_handling.get_account_data, ctx.author, 'config', 'background')
			bank = await self.bot.loop.run_in_executor(None, file_handling.get_account_data, ctx.author, 'economy', 'bank')
			cash = await self.bot.loop.run_in_executor(None, file_handling.get_account_data, ctx.author, 'economy', 'cash')
			timezone = await self.bot.loop.run_in_executor(None, file_handling.get_account_data, ctx.author, 'info', 'timezone')
			votes = await self.bot.loop.run_in_executor(None, file_handling.get_account_data, ctx.author, 'info', 'votes')
			# Append to the message
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

	@account.command(name='create')
	async def create_account(self, ctx):
		"""
		Creates an account.
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
			return await ctx.send(f'You dont have an account.')


def setup(bot):
	bot.add_cog(Accounts(bot))
