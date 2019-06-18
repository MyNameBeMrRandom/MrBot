from discord.ext import commands
from .utils import file_handling
import os


class Accounts(commands.Cog):
	"""
	Account commands.
	"""

	def __init__(self, bot):
		self.bot = bot

	@commands.group(invoke_without_command=True, aliases=['profile'])
	async def account(self, ctx):
		"""
		Display information about your account.
		"""
		print('Account information coming soon.')

	@account.command(name='create')
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
