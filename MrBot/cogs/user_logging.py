from discord.ext import commands
import asyncio
import discord
import yaml
import time
import os


# noinspection PyMethodMayBeStatic
class UserLogging(commands.Cog):
	"""
	Bot logging
	"""

	def __init__(self, bot):
		self.bot = bot
		self.user_status = self.bot.loop.create_task(self.check_user_status())

	def do_check_user_status(self, member):
		with open(f'data/accounts/{member.id}.yaml', 'r', encoding='utf8') as r:
			data = yaml.load(r, Loader=yaml.FullLoader)
			if data['status_times'][f'online_since'] is not None:
				# Get the time since the user was in previous state.
				status_since = data['status_times'][f'online_since']
				# Calculate how long they were in that status for.
				status_time_1 = time.time() - status_since
				# Get the amount of time they have already been in the previous status.
				status_time_2 = data['status_times'][f'online_time']
				# Calculate the total time.
				status_time = status_time_1 + status_time_2
				# Round it and set it as the before status time.
				data['status_times'][f'online_time'] = round(status_time)
			if data['status_times'][f'offline_since'] is not None:
				# Get the time since the user was in previous state.
				status_since = data['status_times'][f'offline_since']
				# Calculate how long they were in that status for.
				status_time_1 = time.time() - status_since
				# Get the amount of time they have already been in the previous status.
				status_time_2 = data['status_times'][f'offline_time']
				# Calculate the total time.
				status_time = status_time_1 + status_time_2
				# Round it and set it as the before status time.
				data['status_times'][f'offline_time'] = round(status_time)
			if data['status_times'][f'dnd_since'] is not None:
				# Get the time since the user was in previous state.
				status_since = data['status_times'][f'dnd_since']
				# Calculate how long they were in that status for.
				status_time_1 = time.time() - status_since
				# Get the amount of time they have already been in the previous status.
				status_time_2 = data['status_times'][f'dnd_time']
				# Calculate the total time.
				status_time = status_time_1 + status_time_2
				# Round it and set it as the before status time.
				data['status_times'][f'dnd_time'] = round(status_time)
			if data['status_times'][f'idle_since'] is not None:
				# Get the time since the user was in previous state.
				status_since = data['status_times'][f'idle_since']
				# Calculate how long they were in that status for.
				status_time_1 = time.time() - status_since
				# Get the amount of time they have already been in the previous status.
				status_time_2 = data['status_times'][f'idle_time']
				# Calculate the total time.
				status_time = status_time_1 + status_time_2
				# Round it and set it as the before status time.
				data['status_times'][f'idle_time'] = round(status_time)
			with open(f'data/accounts/{member.id}.yaml', 'w', encoding='utf8') as w:
				data['status_times'][f'online_since'] = None
				data['status_times'][f'offline_since'] = None
				data['status_times'][f'dnd_since'] = None
				data['status_times'][f'idle_since'] = None
				if data['status_times'][f'{member.status}_since'] is None:
					data['status_times'][f'{member.status}_since'] = time.time()
				yaml.dump(data, w)

	async def check_user_status(self):
		await self.bot.wait_until_ready()
		while not self.bot.is_closed():
			for guild in self.bot.guilds:
				for member in guild.members:
					if os.path.isfile(f'data/accounts/{member.id}.yaml'):
						try:
							await self.bot.loop.run_in_executor(None, self.do_check_user_status, member)
						except FileNotFoundError:
							continue
			await asyncio.sleep(1800)

	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		try:
			if before.status != after.status:
				self.update_user_status(before, after)
		except FileNotFoundError:
			return
		except TypeError:
			return

	def update_user_status(self, before, after):
		with open(f'data/accounts/{before.id}.yaml', 'r', encoding='utf8') as r:
			data = yaml.load(r, Loader=yaml.FullLoader)
			# Get the time since the user was in previous state.
			before_status_since = data['status_times'][f'{before.status}_since']
			# Calculate how long they were in that status for.
			before_status_time_1 = time.time() - before_status_since
			# Get the amount of time they have already been in the previous status.
			before_status_time_2 = data['status_times'][f'{before.status}_time']
			# Calculate the total time.
			status_time = before_status_time_1 + before_status_time_2
			# Round it and set it as the before status time.
			data['status_times'][f'{before.status}_time'] = round(status_time)
			with open(f'data/accounts/{before.id}.yaml', 'w', encoding='utf8') as w:
				# Set the new status since to the current time
				data['status_times'][f'{after.status}_since'] = time.time()
				# Set the old status since to null
				data['status_times'][f'{before.status}_since'] = None
				yaml.dump(data, w)

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.id == self.bot.user.id:
			await self.bot.loop.run_in_executor(None, self.update_bot_stats, 'messages_sent')
		if not message.author == message.author.bot:
			await self.bot.loop.run_in_executor(None, self.update_bot_stats, 'messages_seen')
		if message.author.bot:
			return

	@commands.Cog.listener()
	async def on_command_completion(self, ctx):
		await self.bot.loop.run_in_executor(None, self.update_bot_stats, 'commands_run')

	def update_bot_stats(self, stat_type):
		with open(f'data/stats/stats.yaml', 'r', encoding='utf8') as r:
			data = yaml.load(r, Loader=yaml.FullLoader)
			stat = int(data[stat_type])
			with open(f'data/stats/stats.yaml', 'w', encoding='utf8') as w:
				data[stat_type] = stat + 1
				yaml.dump(data, w)






def setup(bot):
	bot.add_cog(UserLogging(bot))

