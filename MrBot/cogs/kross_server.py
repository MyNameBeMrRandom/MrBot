from discord.ext import commands
import discord


class KrossServer(commands.Cog):
	"""
	Custom server commands.
	"""

	def __init__(self, bot):
		self.bot = bot

	async def cog_before_invoke(self, ctx):
		if ctx.guild.id == 491312179476299786:
			return True
		else:
			await ctx.send('This command is only for a certain guild.')
			return False

	@commands.Cog.listener()
	async def on_member_join(self, member):
		guild = member.guild
		if not guild.id == 491312179476299786:
			return
		if member.bot is True:
			return
		kodama = discord.utils.get(guild.roles, name='Kodama')
		sylph = discord.utils.get(guild.roles, name='Sylph')
		leviathan = discord.utils.get(guild.roles, name='Leviathan')
		phoenix = discord.utils.get(guild.roles, name='Phoenix')
		kodama_count = len(kodama.members)
		sylph_count = len(sylph.members)
		leviathan_count = len(leviathan.members)
		phoenix_count = len(phoenix.members)
		try:
			if kodama_count <= phoenix_count and kodama_count <= leviathan_count and kodama_count <= sylph_count:
				return await member.add_roles(kodama)
			elif phoenix_count <= kodama_count and phoenix_count <= leviathan_count and phoenix_count <= sylph_count:
				return await member.add_roles(phoenix)
			elif leviathan_count <= phoenix_count and leviathan_count <= kodama_count and leviathan_count <= sylph_count:
				return await member.add_roles(leviathan)
			elif sylph_count <= phoenix_count and sylph_count <= leviathan_count and sylph_count <= kodama_count:
				return await member.add_roles(sylph)
			else:
				await member.add_roles(phoenix)
		except discord.Forbidden:
			return

	@commands.command(name='house_members', aliases=['hm'], hidden=True)
	async def houses(self, ctx):
		kodama = discord.utils.get(ctx.guild.roles, name='Kodama')
		sylph = discord.utils.get(ctx.guild.roles, name='Sylph')
		leviathan = discord.utils.get(ctx.guild.roles, name='Leviathan')
		phoenix = discord.utils.get(ctx.guild.roles, name='Phoenix')
		banshee = discord.utils.get(ctx.guild.roles, name='Banshee')
		await ctx.send(f'Kodama members: {len(kodama.members)}')
		await ctx.send(f'Sylph members: {len(sylph.members)}')
		await ctx.send(f'Leviathan members: {len(leviathan.members)}')
		await ctx.send(f'Phoenix members: {len(phoenix.members)}')
		return await ctx.send(f'Banshee members: {len(banshee.members)}')

	@commands.command(name='points', aliases=['p'], hidden=True)
	@commands.has_role(548604302768209920)
	async def points(self, ctx, house: str, operation: str, points: int):
		if not await self.bot.pool.fetchrow("SELECT key FROM kross_config WHERE key = $1", "phoenix"):
			await self.bot.pool.execute(f"INSERT INTO kross_config VALUES ('phoenix', 0)")
			await self.bot.pool.execute(f"INSERT INTO kross_config VALUES ('kodama', 0)")
			await self.bot.pool.execute(f"INSERT INTO kross_config VALUES ('sylph', 0)")
			await self.bot.pool.execute(f"INSERT INTO kross_config VALUES ('leviathan', 0)")
		if house == 'kodama':
			data = await self.bot.pool.fetchrow("SELECT * FROM kross_config WHERE key = $1", 'kodama')
			if operation == 'add':
				await self.bot.pool.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", data['points'] + points , 'kodama')
				await ctx.send(f'Added `{points}` points to house Kodama. They now have `{data["points"] + points}` points!')
				return await self.refresh_points(ctx)
			elif operation == 'minus':
				await self.bot.pool.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", data['points'] - points, 'kodama')
				await ctx.send(f'Removed `{points}` points from house Kodama. They now have `{data["points"] - points}` points!')
				return await self.refresh_points(ctx)
			else:
				return await ctx.send('That operation was not recognised.')
		elif house == 'phoenix':
			data = await self.bot.pool.fetchrow("SELECT * FROM kross_config WHERE key = $1", 'phoenix')
			if operation == 'add':
				await self.bot.pool.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", data['points'] + points , 'phoenix')
				await ctx.send(f'Added `{points}` points to house Phoenix. They now have `{data["points"] + points}` points!')
				return await self.refresh_points(ctx)
			elif operation == 'minus':
				await self.bot.pool.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", data['points'] - points, 'phoenix')
				await ctx.send(f'Removed `{points}` points from house Phoenix. They now have `{data["points"] - points}` points!')
				return await self.refresh_points(ctx)
			else:
				return await ctx.send('That operation was not recognised.')
		elif house == 'leviathan':
			data = await self.bot.pool.fetchrow("SELECT * FROM kross_config WHERE key = $1", 'leviathan')
			if operation == 'add':
				await self.bot.pool.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", data['points'] + points , 'leviathan')
				await ctx.send(f'Added `{points}` points to house Leviathan. They now have `{data["points"] + points}` points!')
				return await self.refresh_points(ctx)
			elif operation == 'minus':
				await self.bot.pool.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", data['points'] - points, 'leviathan')
				await ctx.send(f'Removed `{points}` points from house Leviathan. They now have `{data["points"] - points}` points!')
				return await self.refresh_points(ctx)
			else:
				return await ctx.send('That operation was not recognised.')
		elif house == 'sylph':
			data = await self.bot.pool.fetchrow("SELECT * FROM kross_config WHERE key = $1", 'sylph')
			if operation == 'add':
				await self.bot.pool.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", data['points'] + points , 'sylph')
				await ctx.send(f'Added `{points}` points to house Sylph. They now have `{data["points"] + points}` points!')
				return await self.refresh_points(ctx)
			elif operation == 'minus':
				await self.bot.pool.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", data['points'] - points, 'sylph')
				await ctx.send(f'Removed `{points}` points from house Sylph. They now have `{data["points"] - points}` points!')
				return await self.refresh_points(ctx)
			else:
				return await ctx.send('That operation was not recognised.')
		else:
			return await ctx.send("That house wasn't recognised.")

	async def refresh_points(self, ctx):
		channel = self.bot.get_channel(547156691985104896)
		try:
			kodama = await self.bot.pool.fetchrow("SELECT * FROM kross_config WHERE key = $1", 'kodama')
			phoenix = await self.bot.pool.fetchrow("SELECT * FROM kross_config WHERE key = $1", 'phoenix')
			leviathan = await self.bot.pool.fetchrow("SELECT * FROM kross_config WHERE key = $1", 'leviathan')
			sylph = await self.bot.pool.fetchrow("SELECT * FROM kross_config WHERE key = $1", 'sylph')
			km = await channel.fetch_message(548311930054639637)
			await km.edit(content=f'Kodama has {kodama["points"]} points!')
			pm = await channel.fetch_message(548311654568427533)
			await pm.edit(content=f'Phoenix has {phoenix["points"]} points!')
			lm = await channel.fetch_message(548311845434294282)
			await lm.edit(content=f'Leviathan has {leviathan["points"]} points!')
			sm = await channel.fetch_message(548311533424476170)
			await sm.edit(content=f'Sylph has {sylph["points"]} points!')
			await ctx.send(f'Refreshed the points leaderboard in {channel.mention}')
		except discord.Forbidden:
			return


def setup(bot):
	bot.add_cog(KrossServer(bot))
