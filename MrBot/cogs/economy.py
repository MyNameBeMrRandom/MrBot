from discord.ext import commands
import discord
import config
import time
import dbl


# noinspection PyMethodMayBeStatic,PyBroadException
class Economy(commands.Cog):
	"""
	Economy management commands.
	"""

	def __init__(self, bot):
		self.bot = bot
		self.dblpy = dbl.Client(self.bot, config.DBL_TOKEN, webhook_path='/dblwebhook', webhook_auth=f'{config.DBL_TOKEN}', webhook_port=5000)

	@commands.Cog.listener()
	async def on_dbl_vote(self, data):
		user = self.bot.get_user(int(data['user']))
		if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", user.id):
			return
		user_data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", user.id)
		cash_amount = user_data["cash"]
		vote_count = user_data["vote_count"]
		await self.bot.pool.execute(f"UPDATE user_config SET vote_count = $1 WHERE key = $2", vote_count + 1, user.id)
		await self.bot.pool.execute(f"UPDATE user_config SET vote_time = $1 WHERE key = $2", time.time(), user.id)
		if data['isWeekend'] is True:
			try:
				await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", cash_amount + 500, user.id)
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f'Thank you for voting, You gained **£500** because you voted on a weekend and earned double rewards!'
				)
				return await user.send(embed=embed)
			except Exception:
				return
		else:
			try:
				await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", cash_amount + 250, user.id)
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f'Thank you for voting, You gained **£250**.!'
				)
				return await user.send(embed=embed)
			except Exception:
				return

	@commands.Cog.listener()
	async def on_dbl_test(self, data):
		user = self.bot.get_user(int(data['user']))
		if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", user.id):
			return
		user_data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", user.id)
		cash_amount = user_data["cash"]
		vote_count = user_data["vote_count"]
		await self.bot.pool.execute(f"UPDATE user_config SET vote_count = $1 WHERE key = $2", vote_count + 1, user.id)
		await self.bot.pool.execute(f"UPDATE user_config SET vote_time = $1 WHERE key = $2", time.time(), user.id)
		if data['isWeekend'] is True:
			try:
				await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", cash_amount + 500, user.id)
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f'Thank you for voting, You gained **£500** because you voted on a weekend and earned double rewards!'
				)
				return await user.send(embed=embed)
			except Exception:
				return
		else:
			try:
				await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", cash_amount + 250, user.id)
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f'Thank you for voting, You gained **£250**.!'
				)
				return await user.send(embed=embed)
			except Exception:
				return

	@commands.command(name='balance', aliases=['bal'])
	async def balance(self, ctx):
		"""
		Display the amount of money you have.
		"""

		if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", ctx.author.id):
			return await ctx.send('You dont have an account.')
		data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
		bank = data["bank"]
		cash = data["cash"]
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

	@commands.command(name='deposit', aliases=['dep'])
	async def deposit(self, ctx, amount):
		"""
		Desposit an amount of money to your bank.
		"""

		if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", ctx.author.id):
			return await ctx.send('You dont have an account.')
		data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
		bank_amount = data["bank"]
		cash_amount = data["cash"]
		if amount == 'all':
			if cash_amount == 0:
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					description=f'You have no money to deposit.'
				)
				embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
				return await ctx.send(embed=embed)
			else:
				await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", bank_amount + cash_amount, ctx.author.id)
				await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", cash_amount - cash_amount, ctx.author.id)
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					description=f'Deposited **£{cash_amount}** to your bank.'
				)
				embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
				return await ctx.send(embed=embed)
		else:
			try:
				amount = int(amount)
				if amount > cash_amount or amount <= 0:
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'You cant deposit that amount of money, you either dont have enough money or tried to deposit an amount less then or equal to 0'
					)
					embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
					return await ctx.send(embed=embed)
				else:
					await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", bank_amount + amount, ctx.author.id)
					await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", cash_amount - amount, ctx.author.id)
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'Deposited **£{amount}** to your bank.'
					)
					embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
					return await ctx.send(embed=embed)
			except ValueError:
				return await ctx.send('That was not a valid amount of money, do not use commas or spaces. e.g `mb deposit 999999`')

	@commands.command(name='withdraw', aliases=['wd'])
	async def withdraw(self, ctx, amount):
		"""
		Withdraw an amount of money from your bank.
		"""

		if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", ctx.author.id):
			return await ctx.send('You dont have an account.')
		data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
		bank_amount = data["bank"]
		cash_amount = data["cash"]
		if amount == 'all':
			if bank_amount == 0:
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					description=f'You have no money to withdraw.'
				)
				embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
				return await ctx.send(embed=embed)
			else:
				await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", cash_amount + bank_amount, ctx.author.id)
				await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", bank_amount - bank_amount, ctx.author.id)
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					description=f'Withdrew **£{bank_amount}** from your bank.'
				)
				embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
				return await ctx.send(embed=embed)
		elif not amount == 'all':
			try:
				amount = int(amount)
				if amount > bank_amount or amount <= 0:
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'You cant withdraw that amount of money, you either dont have enough money or tried to withdraw an amount less then or equal to 0'
					)
					embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
					return await ctx.send(embed=embed)
				else:
					await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", cash_amount + amount, ctx.author.id)
					await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", bank_amount - amount, ctx.author.id)
					embed = discord.Embed(
						colour=0x57FFF5,
						timestamp=ctx.message.created_at,
						description=f'Withdrew **£{amount}** from your bank.'
					)
					embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
					return await ctx.send(embed=embed)
			except ValueError:
				return await ctx.send('That was not a valid amount of money, do not use commas or spaces. e.g `mb deposit 999999`')


def setup(bot):
	bot.add_cog(Economy(bot))
