from discord.ext import commands
from .utils import get_information
from .utils import file_handling
import traceback
import asyncio
import discord
import yaml
import time
import os


# noinspection PyMethodMayBeStatic
class Events(commands.Cog):
	"""
	Bot related events.
	"""

	def __init__(self, bot):
		self.bot = bot
		self.user_status = self.bot.loop.create_task(self.check_user_status())

	# Task to check the users status every so often and update it if its changed
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
			await asyncio.sleep(300)

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

	# Updates as users status.
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

	# When the bot joins a guild.
	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		self.bot.logging.info(f'[GUILD] - Joined the guild {guild.name}.')
		channel = self.bot.get_channel(516002789617434664)
		return await channel.send(f'{self.bot.name} joined a guild called `{guild.name}`')

	# When the bot leaves the guild.
	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		self.bot.logging.info(f'[GUILD] - Left the guild {guild.name}.')
		channel = self.bot.get_channel(516002789617434664)
		return await channel.send(f'{self.bot.name} left a guild called `{guild.name}`')

	# When a guild is updated
	@commands.Cog.listener()
	async def on_guild_update(self, before, after):
		# If the guild name has changed
		if not before.name == after.name:
			# Check if this type of logging is enabled.
			guild_name_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, before, 'guild_name')
			if guild_name_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, before))
				guild_name = before.name
				guild_avatar = before.icon_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"This guilds name has changed.\n\n"
				)
				embed.set_author(icon_url=guild_avatar, name=guild_name)
				embed.description += f'**Before:**\n{before.name}\n**After:**\n{after.name}'
				return await channel.send(embed=embed)
		# If the guilds region has changed.
		if not before.region == after.region:
			# Check if this type of logging is enabled.
			guild_region_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, before, 'guild_region')
			if guild_region_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, before))
				guild_name = before.name
				guild_avatar = before.icon_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"This guilds region has changed.\n\n"
				)
				embed.set_author(icon_url=guild_avatar, name=guild_name)
				embed.description += f'**Before:**\n{get_information.guild_region(before)}\n**After:**\n{get_information.guild_region(after)}'
				return await channel.send(embed=embed)
		# If the guilds afk timout has changed.
		if not before.afk_timeout == after.afk_timeout:
			# Check if this type of logging is enabled.
			guild_afk_timeout_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, before, 'guild_afk_timeout')
			if guild_afk_timeout_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, before))
				guild_name = before.name
				guild_avatar = before.icon_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"This guilds AFK timout has changed.\n\n"
				)
				embed.set_author(icon_url=guild_avatar, name=guild_name)
				embed.description += f'**Before:**\n{int(before.afk_timeout/60)} minutes\n**After:**\n{int(after.afk_timeout/60)} minutes'
				return await channel.send(embed=embed)
		# If the guilds afk channel has changed.
		if not before.afk_channel == after.afk_channel:
			# Check if this type of logging is enabled.
			guild_afk_channel_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, before, 'guild_afk_channel')
			if guild_afk_channel_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, before))
				guild_name = before.name
				guild_avatar = before.icon_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"This guilds AFK voice channel has changed.\n\n"
				)
				embed.set_author(icon_url=guild_avatar, name=guild_name)
				embed.description += f'**Before:**\n{before.afk_channel.name}\n**After:**\n{after.afk_channel.name}'
				return await channel.send(embed=embed)
		# If the guilds system channel has changed.
		if not before.system_channel == after.system_channel:
			# Check if this type of logging is enabled.
			guild_system_channel_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, before, 'guild_system_channel')
			if guild_system_channel_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, before))
				guild_name = before.name
				guild_avatar = before.icon_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"This guilds system messages channel has changed.\n\n"
				)
				embed.set_author(icon_url=guild_avatar, name=guild_name)
				embed.description += f'**Before:**\n{before.system_channel.mention}\n**After:**\n{after.system_channel.mention}'
				return await channel.send(embed=embed)
		# If the guilds icon has changed.
		if not before.icon_url == after.icon_url:
			# Check if this type of logging is enabled.
			guild_icon_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, before, 'guild_icon')
			if guild_icon_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, before))
				guild_name = before.name
				guild_avatar = before.icon_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"This guilds icon has changed.\n\n"
				)
				embed.set_author(icon_url=guild_avatar, name=guild_name)
				embed.description += f'**Before:**\n[Image]({before.icon_url})\n**After:**\n[Image]({after.icon_url})'
				return await channel.send(embed=embed)
		# If the guilds notification setting has changed.
		if not before.default_notifications == after.default_notifications:
			# Check if this type of logging is enabled.
			guild_default_notifications_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, before, 'guild_default_notifications')
			if guild_default_notifications_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, before))
				guild_name = before.name
				guild_avatar = before.icon_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"This guilds default notification setting has changed.\n\n"
				)
				embed.set_author(icon_url=guild_avatar, name=guild_name)
				embed.description += f'**Before:**\n{get_information.guild_notification_level(before)}\n**After:**\n{get_information.guild_notification_level(after)}'
				return await channel.send(embed=embed)
		# If the guilds description has changed.
		if not before.description == after.description:
			# Check if this type of logging is enabled.
			guild_description_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, before, 'guild_description')
			if guild_description_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, before))
				guild_name = before.name
				guild_avatar = before.icon_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"This guilds description has changed.\n\n"
				)
				embed.set_author(icon_url=guild_avatar, name=guild_name)
				embed.description += f'**Before:**\n{before.description}\n**After:**\n{after.description}'
				return await channel.send(embed=embed)
		# If the guilds mfa_level has changed.
		if not before.mfa_level == after.mfa_level:
			# Check if this type of logging is enabled.
			guild_mfa_level_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, before, 'guild_mfa_level')
			if guild_mfa_level_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, before))
				guild_name = before.name
				guild_avatar = before.icon_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"This guilds MFA level has changed.\n\n"
				)
				embed.set_author(icon_url=guild_avatar, name=guild_name)
				embed.description += f'**Before:**\n{get_information.guild_mfa_level(before)}\n**After:**\n{get_information.guild_mfa_level(after)}'
				return await channel.send(embed=embed)
		# If the guilds verification level has changed.
		if not before.verification_level == after.verification_level:
			# Check if this type of logging is enabled.
			guild_mfa_level_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, before, 'guild_verification_level')
			if guild_mfa_level_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, before))
				guild_name = before.name
				guild_avatar = before.icon_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"This guilds verification level has changed.\n\n"
				)
				embed.set_author(icon_url=guild_avatar, name=guild_name)
				embed.description += f'**Before:**\n{get_information.guild_verification_level(before)}\n**After:**\n{get_information.guild_verification_level(after)}'
				return await channel.send(embed=embed)
		# If the guilds explicit content filter has changed.
		if not before.explicit_content_filter == after.explicit_content_filter:
			# Check if this type of logging is enabled.
			guild_explicit_content_filter_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, before, 'guild_explicit_content_filter')
			if guild_explicit_content_filter_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, before))
				guild_name = before.name
				guild_avatar = before.icon_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"This guilds explicit content filter has changed.\n\n"
				)
				embed.set_author(icon_url=guild_avatar, name=guild_name)
				embed.description += f'**Before:**\n{get_information.guild_content_filter_level(before)}\n**After:**\n{get_information.guild_content_filter_level(after)}'
				return await channel.send(embed=embed)
		# If the guilds splash has changed.
		if not before.splash == after.splash:
			# Check if this type of logging is enabled.
			guild_splash_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, before, 'guild_splash')
			if guild_splash_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, before))
				guild_name = before.name
				guild_avatar = before.icon_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"This guilds splash has changed.\n\n"
				)
				embed.set_author(icon_url=guild_avatar, name=guild_name)
				embed.description += f'**Before:**\n{before.splash}\n**After:**\n{after.splash}'
				return await channel.send(embed=embed)
		else:
			return

	# When a member joins a server.
	@commands.Cog.listener()
	async def on_member_join(self, member):
		guild = member.guild
		# Check if this type of logging is enabled.
		check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, guild, 'member_join')
		if check is True:
			# Get the logging channel for the guild.
			channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, guild))
			author = member.name
			useravatar = member.avatar_url
			embed = discord.Embed(
				colour=0x57FFF5,
				description=f"**{member.name}** has joined the guild."
			)
			embed.set_author(icon_url=useravatar, name=author)
			embed.set_footer(text=f'ID: {member.id}')
			embed.set_thumbnail(url=member.avatar_url_as(format="png"))
			return await channel.send(embed=embed)
		else:
			return

	# When a member leaves a server.
	@commands.Cog.listener()
	async def on_member_remove(self, member):
		guild = member.guild
		# Check if this type of logging is enabled.
		check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, guild, 'member_leave')
		if check is True:
			# Get the logging channel for the guild.
			channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, guild))
			author = member.name
			useravatar = member.avatar_url
			embed = discord.Embed(
				colour=0x57FFF5,
				description=f"**{member.name}** has left the guild."
			)
			embed.set_author(icon_url=useravatar, name=author)
			embed.set_footer(text=f'ID: {member.id}')
			embed.set_thumbnail(url=member.avatar_url_as(format="png"))
			return await channel.send(embed=embed)
		else:
			return

	# When a member updates their profile
	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		guild = before.guild
		# If the user is a bot, return nothing.
		if before.bot:
			return
		# If the members status has changed.
		if not before.status == after.status:
			# Check if this type of logging is enabled.
			member_status_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, guild, 'member_status')
			if member_status_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, guild))
				author = after.name
				useravatar = after.avatar_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"**{before.name}**'s status has changed.\n\n"
				)
				embed.set_author(icon_url=useravatar, name=author)
				embed.description += f'**Before:**\n{get_information.user_status(before)}\n**After:**\n{get_information.user_status(after)}'
				return await channel.send(embed=embed)
			try:
				self.update_user_status(before, after)
			except FileNotFoundError:
				return
			except TypeError:
				return
		# If the members nickname has changed.
		if not before.nick == after.nick:
			# Check if this type of logging is enabled.
			member_nickname_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, guild, 'member_nickname')
			if member_nickname_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, guild))
				author = after.name
				useravatar = after.avatar_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"**{before.name}**'s nickname has changed.\n\n"
				)
				embed.set_author(icon_url=useravatar, name=author)
				embed.description += f'**Before:**\n{before.nick}\n**After:**\n{after.nick}'
				return await channel.send(embed=embed)
		# If the members roles have changed.
		if not before.roles == after.roles:
			# Check if this type of logging is enabled.
			member_role_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, guild, 'member_role')
			if member_role_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, guild))
				author = after.name
				useravatar = after.avatar_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"**{before.name}**'s roles have changed.\n\n"
				)
				embed.set_author(icon_url=useravatar, name=author)
				embed.description += f'**Before:**\n{", ".join([r for r in before.roles])}\n**After:**\n{", ".join([r for r in after.roles])}'
				return await channel.send(embed=embed)
		# If the members activity has changed.
		if not before.activity == after.activity:
			try:
				if before.activity.name == after.activity.name:
					return
			except AttributeError:
				pass
			# Check if this type of logging is enabled.
			member_activity_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, guild, 'member_activity')
			if member_activity_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, guild))
				author = after.name
				useravatar = after.avatar_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"**{before.name}**'s activity has changed.\n\n"
				)
				embed.set_author(icon_url=useravatar, name=author)
				embed.description += f'**Before:**\n{get_information.user_activity(before)}\n**After:**\n{get_information.user_activity(after)}'
				return await channel.send(embed=embed)
		else:
			return

	# When a user updates thier profile
	@commands.Cog.listener()
	async def on_user_update(self, before, after):
		# If the user is a bot, return nothing.
		if before.bot:
			return
		# Loop through all guilds the bot is in.
		for guild in self.bot.guilds:
			#If the user is not in the guilds, return nothing.
			if before or after not in guild.members:
				return
			# If the users username has changed.
			if not before.name == after.name:
				# Check if this type of logging is enabled.
				user_name_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, guild, 'user_username')
				if user_name_check is True:
					# Get the logging channel for the guild.
					channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, guild))
					author = after.name
					useravatar = after.avatar_url
					embed = discord.Embed(
						colour=0x57FFF5,
						description=f"**{after.name}**'s name has changed.\n\n"
					)
					embed.set_author(icon_url=useravatar, name=author)
					embed.description += f'**Before:**\n{before.name}\n**After:**\n{after.name}'
					return await channel.send(embed=embed)
			# If the users discriminator has changed.
			elif not before.discriminator == after.discriminator:
				# Check if this type of logging is enabled.
				user_discriminator_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, guild, 'user_discriminator')
				if user_discriminator_check is True:
					# Get the logging channel for the guild.
					channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, guild))
					author = after.name
					useravatar = after.avatar_url
					embed = discord.Embed(
						colour=0x57FFF5,
						description=f"**{after.name}**'s discriminator has changed.\n\n"
					)
					embed.set_author(icon_url=useravatar, name=author)
					embed.description += f'**Before:**\n{before.discriminator}\n**After:**\n{after.discriminator}'
					return await channel.send(embed=embed)
			# If the users avatar has changed.
			elif not before.avatar == after.avatar:
				# Check if this type of logging is enabled.
				user_avatar_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, guild, 'user_avatar')
				if user_avatar_check is True:
					# Get the logging channel for the guild.
					channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, guild))
					author = after.name
					useravatar = after.avatar_url
					embed = discord.Embed(
						colour=0x57FFF5,
						description=f"**{after.name}**'s avatar has changed.\n\n"
					)
					embed.set_author(icon_url=useravatar, name=author)
					embed.description += f'**Before:**\n{before.avatar_url}\n**After:**\n{after.avatar_url}'
					return await channel.send(embed=embed)
			else:
				continue

	# When a message is edited.
	@commands.Cog.listener()
	async def on_message_edit(self, before, after):
		guild = before.guild
		# If the user is a bot, return
		if before.author.bot:
			return
		# If message has been pinned/unpinned.
		if not before.pinned == after.pinned:
			# Check if this type of logging is enabled.
			message_pin_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, guild, 'message_pin')
			if message_pin_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, guild))
				author = after.author.name
				useravatar = after.author.avatar_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"**{after.author.name}**'s message was pinned/unpinned.\n\n"
				)
				embed.set_author(icon_url=useravatar, name=author)
				# If the message has an attachement.
				if after.attachments:
					embed.description += f'**Message content:** [Attachment]({after.attachments[0].url})\n{after.content}'
				else:
					embed.description += f'**Message content:**\n{after.content}'
				return await channel.send(embed=embed)
		# If the message was edited.
		if not before.content == after.content:
			# Check if this type of logging is enabled.
			message_edit_check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, guild, 'message_edit')
			if message_edit_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, guild))
				author = after.author.name
				useravatar = after.author.avatar_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"**{after.author.name}**'s edited a message in <#{after.channel.id}>.\n\n"
				)
				embed.set_author(icon_url=useravatar, name=author)
				# If the message has an attachment.
				if before.attachments:
					embed.description += f'**Before:** [Attachment]({before.attachments[0].url})\n{before.content}\n**After:** [Attachment]({before.attachments[0].url})\n{after.content}'
				else:
					embed.description += f'**Before:**\n{before.content}\n**After:**\n{after.content}'
				return await channel.send(embed=embed)
		if not after.embeds and not after.pinned:
			await self.bot.process_commands(after)
		else:
			return

	# When a message is deleted.
	@commands.Cog.listener()
	async def on_message_delete(self, message):
		guild = message.guild
		# If the user is a bot, return
		if message.author.bot:
			return
		# Check if this type of logging is enabled.
		check = await self.bot.loop.run_in_executor(None, file_handling.logging_check, guild, 'message_delete')
		if check is True:
			# Get the logging channel for the guild.
			channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, file_handling.get_logging_channel, guild))
			author = message.author.name
			useravatar = message.author.avatar_url
			embed = discord.Embed(
				colour=0x57FFF5,
				description=f"**{message.author.name}**'s message in <#{message.channel.id}> was deleted.\n\n"
			)
			embed.set_author(icon_url=useravatar, name=author)
			# If the message had an attachment.
			if message.attachments:
				embed.description += f'**Message content:** [Attachment]({message.attachments[0].proxy_url})\n{message.content}'
				embed.set_image(url=message.attachments[0].proxy_url)
			else:
				embed.description += f'**Message content:**\n{message.content}'
			return await channel.send(embed=embed)
		else:
			return

	# When a message is sent.
	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.id == self.bot.user.id:
			return await self.bot.loop.run_in_executor(None, file_handling.update_stat_data, 'messages_sent')
		if not message.author.bot:
			return await self.bot.loop.run_in_executor(None, file_handling.update_stat_data, 'messages_seen')
		if message.author.bot:
			return

	# When a command errors. (Error handler)
	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		error = getattr(error, 'original', error)
		if hasattr(ctx.command, 'on_error'):
			return
		elif isinstance(error, commands.NoPrivateMessage):
			try:
				return await ctx.send(f"The command `{ctx.command}` cannot be used in private messages.")
			except Exception:
				pass
		elif isinstance(error, commands.DisabledCommand):
			return await ctx.send(f"The command `{ctx.command}` is currently disabled.")
		elif isinstance(error, commands.CommandNotFound):
			return
		elif isinstance(error, commands.CommandOnCooldown):
			return await ctx.send(f"The command `{ctx.command}` is on cooldown, retry in {round(error.retry_after, 2)}s.")
		elif isinstance(error, commands.MissingRequiredArgument):
			return await ctx.send(f"You missed the `{error.param}` parameter.")
		elif isinstance(error, commands.TooManyArguments):
			return await ctx.send(f"Too many arguments were passed for the command `{ctx.command}`.")
		elif isinstance(error, commands.BadArgument):
			return await ctx.send(f"A bad argument was passed to the command `{ctx.command}`.")
		elif isinstance(error, commands.MissingPermissions):
			return await ctx.send(f"You dont have the permissions to run the `{ctx.command}` command.")
		elif isinstance(error, commands.BotMissingPermissions):
			return await ctx.send(f"I am missing the following permissions to run the command `{ctx.command}`.\n{error.missing_perms}")
		elif isinstance(error, discord.HTTPException):
			if isinstance(error, discord.Forbidden):
				return await ctx.send(f"I am missing permissions to run the command `{ctx.command}`.")
		elif isinstance(error, commands.CommandInvokeError):
			return await ctx.send(f"There was an error while running that command")
		else:
			try:
				print(f'{error.original.__class__.__name__}: {error.original}')
				traceback.print_tb(error.original.__traceback__)
			except AttributeError:
				print(f'{error.__class__.__name__}: {error}')
				traceback.print_tb(error.__traceback__)

	# When a command successfully completes
	@commands.Cog.listener()
	async def on_command_completion(self, ctx):
		self.bot.logging.info(f'[COMMAND] - {ctx.author} used the command "{ctx.command}" in the guild "{ctx.guild}".')
		return await self.bot.loop.run_in_executor(None, file_handling.update_stat_data, 'commands_run')


def setup(bot):
	bot.add_cog(Events(bot))

