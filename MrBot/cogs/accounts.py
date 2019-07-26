from discord.ext import commands
import asyncpg


class Accounts(commands.Cog):
	"""
	MrBot account management commands.
	"""

	def __init__(self, bot):
		self.bot = bot

	@commands.group(name='account', aliases=['profile'], invoke_without_command=True)
	async def account(self, ctx):
		"""
		Display information about your account.
		"""

		if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", ctx.author.id):
			return await ctx.send('You dont have an account.')
		message = f">>> __**Information about {ctx.author.name}'s account.**__\n\n"
		data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
		message += f'**Configuration:**\n    **Background:** {data["background"]}\n\n'
		message += f'**Economy information:**\n    **Bank:** £{data["bank"]}\n    **Cash:** £{data["cash"]}\n\n'
		message += f'**General information:**\n    **Timezone:** {data["timezone"]}\n    **Last vote time:** {data["vote_time"]}\n    **Votes:** {data["vote_count"]}\n'
		return await ctx.send(message)

	@account.command(name='create')
	async def create_account(self, ctx):
		"""
		Creates an account.
		"""

		try:
			await self.bot.pool.execute(f"INSERT INTO user_config VALUES ($1, 'default', NULL, NULL, 0, 500, 500)", ctx.author.id)
			return await ctx.send(f'Account created with ID `{ctx.author.id}`')
		except asyncpg.UniqueViolationError:
			return await ctx.send('You already have an account.')

	@account.command(name='delete')
	async def delete_account(self, ctx):
		"""
		Deletes your account.
		"""

		if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", ctx.author.id):
			return await ctx.send('You dont have an account.')
		await self.bot.pool.execute(f"DELETE FROM user_config WHERE key = $1", ctx.author.id)
		return await ctx.send('Deleted your account.')



def setup(bot):
	bot.add_cog(Accounts(bot))
