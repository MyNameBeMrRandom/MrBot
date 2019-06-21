from discord.ext import commands
from .utils import file_handling
import discord
import config
import yaml
import dbl


# noinspection PyMethodMayBeStatic
class Economy(commands.Cog):
	"""
	Economy commands.
	"""

	def __init__(self, bot):
		self.bot = bot
		self.token = config.DBL_TOKEN
		self.dblpy = dbl.Client(self.bot, self.token, webhook_path='/dblwebhook', webhook_auth=f'{config.DBL_TOKEN}', webhook_port=5000)

	def do_add_money(self, user, money_type, amount):
		with open(f'data/accounts/{user.id}.yaml', 'r', encoding='utf8') as r:
			data = yaml.load(r, Loader=yaml.FullLoader)
			money = int(data['economy'][f'{money_type}'])
			data['economy'][f'{money_type}'] = money + amount
			with open(f'data/accounts/{user.id}.yaml', 'w', encoding='utf8') as w:
				yaml.dump(data, w)

	def do_remove_money(self, user, money_type, amount):
		with open(f'data/accounts/{user.id}.yaml', 'r', encoding='utf8') as r:
			data = yaml.load(r, Loader=yaml.FullLoader)
			money = int(data['economy'][f'{money_type}'])
			data['economy'][f'{money_type}'] = money - amount
			with open(f'data/accounts/{user.id}.yaml', 'w', encoding='utf8') as w:
				yaml.dump(data, w)

	async def do_deposit(self, ctx, amount):
		if amount == 'all':
			try:
				cash_amount = int(await self.bot.loop.run_in_executor(None, file_handling.get_data, ctx.author, 'economy', 'cash'))
				if cash_amount == 0:
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'You have no money to deposit.'
					)
					embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
					return await ctx.send(embed=embed)
				else:
					await self.bot.loop.run_in_executor(None, self.do_add_money, ctx.author, 'bank', cash_amount)
					await self.bot.loop.run_in_executor(None, self.do_remove_money, ctx.author, 'cash', cash_amount)
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'Deposited **£{cash_amount}** to your bank.'
					)
					embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
					return await ctx.send(embed=embed)
			except FileNotFoundError:
				await ctx.send(f'You dont have an account.')
				return await file_handling.account_creation(ctx)
			except ValueError:
				return await ctx.send('That was not a valid amount of money, do not use commas or spaces. e.g `mb deposit 999999`')
		if not amount == 'all':
			try:
				amount = int(amount)
				cash_amount = int(await self.bot.loop.run_in_executor(None, file_handling.get_data, ctx.author, 'economy', 'cash'))
				if amount > cash_amount or amount <= 0:
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'You cant deposit that amount of money, you either dont have enough money or tried to deposit an amount less then or equal to 0'
					)
					embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
					return await ctx.send(embed=embed)
				else:
					await self.bot.loop.run_in_executor(None, self.do_add_money, ctx.author, 'bank', amount)
					await self.bot.loop.run_in_executor(None, self.do_remove_money, ctx.author, 'cash', amount)
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'Deposited **£{amount}** to your bank.'
					)
					embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
					return await ctx.send(embed=embed)
			except FileNotFoundError:
				await ctx.send(f'You dont have an account.')
				return await file_handling.account_creation(ctx)
			except ValueError:
				return await ctx.send('That was not a valid amount of money, do not use commas or spaces. e.g `mb deposit 999999`')

	async def do_withdraw(self, ctx, amount):
		if amount == 'all':
			try:
				cash_amount = int(await self.bot.loop.run_in_executor(None, file_handling.get_data, ctx.author, 'economy', 'cash'))
				bank_amount = int(await self.bot.loop.run_in_executor(None, file_handling.get_data, ctx.author, 'economy', 'bank'))
				if bank_amount == 0:
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'You have no money to withdraw.'
					)
					embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
					return await ctx.send(embed=embed)
				else:
					await self.bot.loop.run_in_executor(None, self.do_add_money, ctx.author, 'cash', bank_amount)
					await self.bot.loop.run_in_executor(None, self.do_remove_money, ctx.author, 'bank', bank_amount)
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'Withdrew **£{cash_amount}** from your bank.'
					)
					embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
					return await ctx.send(embed=embed)
			except FileNotFoundError:
				await ctx.send(f'You dont have an account.')
				return await file_handling.account_creation(ctx)
			except ValueError:
				return await ctx.send('That was not a valid amount of money, do not use commas or spaces. e.g `mb deposit 999999`')
		elif not amount == 'all':
			try:
				amount = int(amount)
				bank_amount = int(await self.bot.loop.run_in_executor(None, file_handling.get_data, ctx.author, 'economy', 'bank'))
				if amount > bank_amount or amount <= 0:
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'You cant withdraw that amount of money, you either dont have enough money or tried to withdraw an amount less then or equal to 0'
					)
					embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
					return await ctx.send(embed=embed)
				else:
					await self.bot.loop.run_in_executor(None, self.do_add_money, ctx.author, 'cash', amount)
					await self.bot.loop.run_in_executor(None, self.do_remove_money, ctx.author, 'bank', amount)
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'Withdrew **£{amount}** from your bank.'
					)
					embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
					return await ctx.send(embed=embed)
			except FileNotFoundError:
				await ctx.send(f'You dont have an account.')
				return await file_handling.account_creation(ctx)
			except ValueError:
				return await ctx.send('That was not a valid amount of money, do not use commas or spaces. e.g `mb deposit 999999`')

	@commands.Cog.listener()
	async def on_dbl_vote(self, data):
		user = self.bot.get_user(int(data['user']))
		if data['isWeekend'] is True:
			try:
				await self.bot.loop.run_in_executor(None, self.do_add_money, user, 'cash', 500)
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f'Thank you for voting, You gained **£500** because you voted on a weekend and earned double rewards!'
				)
				return await user.send(embed=embed)
			except FileNotFoundError:
				return await user.send('You dont have an account, so your vote didnt count, use `mb account create` to make one.')
		else:
			try:
				await self.bot.loop.run_in_executor(None, self.do_add_money, user, 'cash', 250)
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f'Thank you for voting, You gained **£250**.'
				)
				return await user.send(embed=embed)
			except FileNotFoundError:
				return await user.send('You dont have an account, so your vote didnt count, use `mb account create` to make one.')

	@commands.Cog.listener()
	async def on_dbl_test(self, data):
		user = self.bot.get_user(int(data['user']))
		if data['isWeekend'] is True:
			try:
				await self.bot.loop.run_in_executor(None, self.do_add_money, user, 'cash', 500)
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f'Thank you for voting, You gained **£500** because you voted on a weekend and earned double rewards!'
				)
				return await user.send(embed=embed)
			except FileNotFoundError:
				return await user.send('You dont have an account, so your vote didnt count, use `mb account create` to make one.')
		else:
			try:
				await self.bot.loop.run_in_executor(None, self.do_add_money, user, 'cash', 250)
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f'Thank you for voting, You gained **£250**.'
				)
				return await user.send(embed=embed)
			except FileNotFoundError:
				return await user.send('You dont have an account, so your vote didnt count, use `mb account create` to make one.')

	@commands.command(name='balance', aliases=['bal'])
	async def balance(self, ctx):
		"""
		Display the amount of money you have.
		"""
		try:
			bank = await self.bot.loop.run_in_executor(None, file_handling.get_data, ctx.author, 'economy', 'cash')
			cash = await self.bot.loop.run_in_executor(None, file_handling.get_data, ctx.author, 'economy', 'bank')
			embed = discord.Embed(
				colour=0x57FFF5,
				timestamp=ctx.message.created_at,
				title=f"{ctx.author.name}'s balance:"
			)
			embed.add_field(name='Bank:', value=f'**£{bank}**')
			embed.add_field(name='Cash:', value=f'**£{cash}**')
			embed.add_field(name='Total:', value=f'**£{cash + bank}**')
			embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
			return await ctx.send(embed=embed)
		except FileNotFoundError:
			await ctx.send(f'You dont have an account.')
			return await file_handling.account_creation(ctx)

	@commands.command(name='deposit', aliases=['dep'])
	async def deposit(self, ctx, amount):
		"""
		Desposit an amount of money to your bank.
		"""
		return await self.do_deposit(ctx, amount)

	@commands.command(name='withdraw', aliases=['wd'])
	async def withdraw(self, ctx, amount):
		"""
		Withdraw an amount of money from your bank.
		"""
		return await self.do_withdraw(ctx, amount)

	@commands.command(hidden=True)
	@commands.is_owner()
	async def money(self, ctx, price: int):
		try:
			with open(f'data/accounts/{ctx.author.id}.yaml', 'r', encoding='utf8') as r:
				data = yaml.load(r, Loader=yaml.FullLoader)
				data['economy']['cash'] = price
			with open(f'data/accounts/{ctx.author.id}.yaml', 'w', encoding='utf8') as w:
				yaml.dump(data, w)
		except Exception as e:
			await ctx.send('You dont have an account, use `mb account create` to make one.')
			await ctx.send(f'{e}')


def setup(bot):
	bot.add_cog(Economy(bot))
