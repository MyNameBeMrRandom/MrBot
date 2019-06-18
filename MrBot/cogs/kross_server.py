from discord.ext import commands
import matplotlib.pyplot as plt
import discord
import time


class KrossServer(commands.Cog):
	"""
	Server specific commands.
	"""

	def __init__(self, bot):
		self.bot = bot

	async def refresh_points(self, ctx):
		channel = self.bot.get_channel(547156691985104896)
		with open('data/kross_server/kodama.txt') as r:
			kp = r.readline()
			kp = int(kp)
			km = await channel.fetch_message(548311930054639637)
			await km.edit(content=f'Kodama has {kp} points!')
		with open('data/kross_server/phoenix.txt') as r:
			pp = r.readline()
			pp = int(pp)
			pm = await channel.fetch_message(548311654568427533)
			await pm.edit(content=f'Phoenix has {pp} points!')
		with open('data/kross_server/leviathan.txt') as r:
			lp = r.readline()
			lp = int(lp)
			lm = await channel.fetch_message(548311845434294282)
			await lm.edit(content=f'Leviathan has {lp} points!')
		with open('data/kross_server/sylph.txt') as r:
			sp = r.readline()
			sp = int(sp)
			sm = await channel.fetch_message(548311533424476170)
			await sm.edit(content=f'Sylph has {sp} points!')
		await ctx.send('Refreshed the points leaderboard in <#547156691985104896>')

	def calculate_percent(self, kodama_points, phoenix_points, leviathan_points, sylph_points):
		total = kodama_points + phoenix_points + leviathan_points + sylph_points
		kodama_p = kodama_points / total
		phoenix_p = phoenix_points / total
		leviathan_p = leviathan_points / total
		sylph_p = sylph_points / total
		kodama_percent = round(kodama_p * 100, 1)
		phoenix_percent = round(phoenix_p * 100, 1)
		leviathan_percent = round(leviathan_p * 100, 1)
		sylph_percent = round(sylph_p * 100, 1)
		return kodama_percent, phoenix_percent, leviathan_percent, sylph_percent

	def do_point_pie(self, ctx):

		with open('data/kross_server/kodama.txt') as r:
			kp = r.readline()
			kodama_points = int(kp)
		with open('data/kross_server/phoenix.txt') as r:
			pp = r.readline()
			phoenix_points = int(pp)
		with open('data/kross_server/leviathan.txt') as r:
			lp = r.readline()
			leviathan_points = int(lp)
		with open('data/kross_server/sylph.txt') as r:
			sp = r.readline()
			sylph_points = int(sp)

		kodama_percent, phoenix_percent, leviathan_percent, sylph_percent = self.calculate_percent(kodama_points, phoenix_points, leviathan_points, sylph_points)
		labels = [f'Phoenix: {phoenix_percent}%', f'Leviathan: {leviathan_percent}%', f'Kodama: {kodama_percent}%', f'Sylph: {sylph_percent}%']
		sizes = [phoenix_points, leviathan_points, kodama_points, sylph_points]
		colors = ['#ff6600', '#304bff', '#235d0e', '#FD0061']

		fig, axs = plt.subplots()
		axs.pie(sizes,colors=colors, shadow=True, startangle=90)
		axs.legend(labels, loc="best")
		axs.axis('equal')
		plt.tight_layout()
		plt.savefig(f'images/pie_charts/point_pie.png', transparent=True)
		plt.close()

	@commands.Cog.listener()
	async def on_member_join(self, member):
		guild = member.guild
		if guild.id == 491312179476299786:
			if member.bot is False:
				kodama = discord.utils.get(guild.roles, name='Kodama')
				sylph = discord.utils.get(guild.roles, name='Sylph')
				leviathan = discord.utils.get(guild.roles, name='Leviathan')
				phoenix = discord.utils.get(guild.roles, name='Phoenix')
				kodama_count = len(kodama.members)
				sylph_count = len(sylph.members)
				leviathan_count = len(leviathan.members)
				phoenix_count = len(phoenix.members)
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
			else:
				return

	@commands.command(name='house_members', aliases=['hm'], hidden=True)
	@commands.has_role(548604302768209920)
	async def houses(self, ctx):
		if ctx.guild.id == 491312179476299786:
			kodama = discord.utils.get(ctx.guild.roles, name='Kodama')
			sylph = discord.utils.get(ctx.guild.roles, name='Sylph')
			leviathan = discord.utils.get(ctx.guild.roles, name='Leviathan')
			phoenix = discord.utils.get(ctx.guild.roles, name='Phoenix')
			banshee = discord.utils.get(ctx.guild.roles, name='Banshee')
			kodama_count = len(kodama.members)
			sylph_count = len(sylph.members)
			leviathan_count = len(leviathan.members)
			phoenix_count = len(phoenix.members)
			banshee_count = len(banshee.members)
			await ctx.send(f'Kodama members: {kodama_count}')
			await ctx.send(f'Sylph members: {sylph_count}')
			await ctx.send(f'Leviathan members: {leviathan_count}')
			await ctx.send(f'Phoenix members: {phoenix_count}')
			return await ctx.send(f'Banshee members: {banshee_count}')
		else:
			await ctx.send('This is a guild specific command.')

	@commands.command(name='points', aliases=['p'], hidden=True)
	@commands.has_role(548604302768209920)
	async def points(self, ctx, house: str, operation: str, points: int):
		if ctx.guild.id == 491312179476299786:
			if house == 'kodama':
				with open('data/kross_server/kodama.txt') as r:
					cp = r.readline()
					cp = int(cp)
					if operation == 'add':
						np = cp + points
						with open('data/kross_server/kodama.txt', 'w') as a:
							a.write(str(np))
							a.close()
						await ctx.send(f'Added {points} points to house Kodama. They now have {np} points!')
						await self.refresh_points(ctx)
					elif operation == 'minus':
						np = cp - points
						with open('data/kross_server/sylph.txt', 'w') as m:
							m.write(str(np))
							m.close()
						await ctx.send(f'Removed {points} points from house Kodama. They now have {np} points!')
						await self.refresh_points(ctx)
					else:
						await ctx.send('That operation was not recognised.')
			elif house == 'phoenix':
				with open('data/kross_server/phoenix.txt') as r:
					cp = r.readline()
					cp = int(cp)
					if operation == 'add':
						np = cp + points
						with open('data/kross_server/phoenix.txt', 'w') as a:
							a.write(str(np))
							a.close()
						await ctx.send(f'Added {points} points to house Phoenix. They now have {np} points!')
						await self.refresh_points(ctx)
					elif operation == 'minus':
						np = cp - points
						with open('data/kross_server/phoenix.txt', 'w') as m:
							m.write(str(np))
							m.close()
						await ctx.send(f'Removed {points} points from house Phoenix. They now have {np} points!')
						await self.refresh_points(ctx)
					else:
						await ctx.send('That operation was not recognised.')
			elif house == 'leviathan':
				with open('data/kross_server/leviathan.txt') as r:
					cp = r.readline()
					cp = int(cp)
					if operation == 'add':
						np = cp + points
						with open('data/kross_server/leviathan.txt', 'w') as a:
							a.write(str(np))
							a.close()
						await ctx.send(f'Added {points} points to house Leviathan. They now have {np} points!')
						await self.refresh_points(ctx)
					elif operation == 'minus':
						np = cp - points
						with open('data/kross_server/sylph.txt', 'w') as m:
							m.write(str(np))
							m.close()
						await ctx.send(f'Removed {points} points from house Leviathan. They now have {np} points!')
						await self.refresh_points(ctx)
					else:
						await ctx.send('That operation was not recognised.')
			elif house == 'sylph':
				with open('data/kross_server/sylph.txt') as r:
					cp = r.readline()
					cp = int(cp)
					if operation == 'add':
						np = cp + points
						with open('data/kross_server/sylph.txt', 'w') as a:
							a.write(str(np))
							a.close()
						await ctx.send(f'Added {points} points to house Sylph. They now have {np} points!')
						await self.refresh_points(ctx)
					elif operation == 'minus':
						np = cp - points
						with open('data/kross_server/sylph.txt', 'w') as m:
							m.write(str(np))
							m.close()
						await ctx.send(f'Removed {points} points from house Sylph. They now have {np} points!')
						await self.refresh_points(ctx)
					else:
						await ctx.send('That operation was not recognised.')
			else:
				await ctx.send("That house wasn't recognised.")
		else:
			await ctx.send('This is a guild specific command.')

	@commands.command(name='points_pie', aliases=['point_p', 'pp'], hidden=True)
	async def point_pie(self, ctx):
		if ctx.guild.id == 491312179476299786:
			start = time.perf_counter()
			await ctx.trigger_typing()
			await self.bot.loop.run_in_executor(None, self.do_point_pie, ctx)
			await ctx.send(file=discord.File(f'images/pie_charts/point_pie.png'))
			end = time.perf_counter()
			return await ctx.send(f'That took {end - start:.3f}sec to complete')
		else:
			await ctx.send('This is a guild specific command.')




def setup(bot):
	bot.add_cog(KrossServer(bot))
