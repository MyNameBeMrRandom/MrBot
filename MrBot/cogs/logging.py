from discord.ext import commands
import asyncio
import discord
import config
import yaml
import time
import dbl


# noinspection PyMethodMayBeStatic,PyMethodMayBeStatic,PyMethodMayBeStatic,PyMethodMayBeStatic,PyMethodMayBeStatic,PyMethodMayBeStatic,PyMethodMayBeStatic,PyMethodMayBeStatic,PyMethodMayBeStatic,PyMethodMayBeStatic,PyMethodMayBeStatic
class Logging(commands.Cog):
	"""
	Bot logging
	"""

	def __init__(self, bot):
		self.bot = bot
		self.token = config.DBL_TOKEN
		self.dblpy = dbl.Client(self.bot, self.token, webhook_path='/dblwebhook', webhook_auth=f'{config.DBL_TOKEN}', webhook_port=5000)
		self.updating = self.bot.loop.create_task(self.update_stats())

	async def update_stats(self):
		await self.bot.wait_until_ready()
		while self.bot.is_ready():
			self.bot.logging.info('[SERVER_COUNT] - Attempting to post server count.')
			try:
				await self.dblpy.post_guild_count()
				self.bot.logging.info(f'[SERVER_COUNT] - Posted server count ({self.dblpy.guild_count()}).')
			except Exception as e:
				self.bot.logging.exception('[SERVER_COUNT] - Failed to post server count.\n{}: {}'.format(type(e).__name__, e))
			await asyncio.sleep(21600)

	def user_activity(self, user):
		if user.status == user.status.offline:
			return 'N/A'
		else:
			try:
				if user.activity.type == user.activity.type.playing:
					return f'Playing: **{user.activity.name}**'
				elif user.activity.type == user.activity.type.streaming:
					return f'Streaming [{user.activity.name}]({user.activity.url})'
				elif user.activity.type == user.activity.type.listening:
					return f'Listening to {user.activity.name}: **{user.activity.title}**  by  **{user.activity.artist}**'
				elif user.activity.type == user.activity.type.watching:
					return f'Watching: {user.activity.name}'
			except TypeError:
				return 'N/A'

	def user_status(self, user):
		if user.status == user.status.online:
			return "Online"
		elif user.status == user.status.idle:
			return "Idle"
		elif user.status == user.status.dnd:
			return "Do not Disturb"
		elif user.status == user.status.offline:
			return "Offline"
		else:
			return "Offline"

	def guild_region(self, guild):
		if guild.region == guild.region.amsterdam:
			return "Amsterdam"
		elif guild.region == guild.region.brazil:
			return "Brazil"
		elif guild.region == guild.region.eu_central:
			return "Central-Europe"
		elif guild.region == guild.region.eu_west:
			return "Western-Europe"
		elif guild.region == guild.region.frankfurt:
			return "Frankfurt"
		elif guild.region == guild.region.hongkong:
			return "Hong-Kong"
		elif guild.region == guild.region.india:
			return "India"
		elif guild.region == guild.region.japan:
			return "Japan"
		elif guild.region == guild.region.london:
			return "London"
		elif guild.region == guild.region.russia:
			return "Russia"
		elif guild.region == guild.region.singapore:
			return "Singapore"
		elif guild.region == guild.region.southafrica:
			return "South-Africa"
		elif guild.region == guild.region.us_central:
			return "Us-Central"
		elif guild.region == guild.region.sydney:
			return "Sydney"
		elif guild.region == guild.region.us_east:
			return "Us-East"
		elif guild.region == guild.region.us_south:
			return "Us-South"
		elif guild.region == guild.region.us_west:
			return "Us-West"
		else:
			return "N/A"

	def guild_notification_settings(self, guild):
		if guild.default_notifications == guild.default_notifications.all_messages:
			return "All messages"
		elif guild.default_notifications == guild.default_notifications.only_mentions:
			return "Only mentions"
		else:
			return "N/A"

	def guild_mfa_level(self, guild):
		if guild.mfa_level == 0:
			return "2FA Not required"
		elif guild.mfa_level == 1:
			return "2FA Required"
		else:
			return "N/A"

	def guild_verification_level(self, guild):
		if guild.verification_level == guild.verification_level.none:
			return "None - No criteria set"
		elif guild.verification_level == guild.verification_level.low:
			return "Low - Must have a verified email"
		elif guild.verification_level == guild.verification_level.medium:
			return "Medium - Must have a verified email and be registered on discord for more than 5 minutes"
		elif guild.verification_level == guild.verification_level.high:
			return "High - Must have a verified email, be registered on discord for more than 5 minutes and be a member of the guild for more then 10 minutes"
		elif guild.verification_level == guild.verification_level.extreme:
			return "Extreme - Must have a verified email, be registered on discord for more than 5 minutes, be a member of the guild for more then 10 minutes and a have a verified phone number."
		else:
			return "N/A"

	def guild_content_filter_level(self, guild):
		if guild.explicit_content_filter == guild.explicit_content_filter.disabled:
			return "None - Content filter disabled"
		elif guild.explicit_content_filter == guild.explicit_content_filter.no_role:
			return "No role - Content filter enabled only for users with no roles"
		elif guild.explicit_content_filter == guild.explicit_content_filter.all_members:
			return "All members - Content filter enabled for all users"
		else:
			return "N/A"

	def do_create_account(self, user):
		new_account = {
			'info': {
				'name': f'{user.name}',
				'votes': 0,
				'birthday': None,
				'timezone': None,
			},
			'economy': {
				'bank': 500,
				'cash': 500
			},
			'config': {
				'background': 'default'
			},
			'status_times': {
				'online': None,
				'offline': None,
				'idle': None,
				'dnd': None
			}
		}
		with open(f'data/accounts/{user.id}.yaml', 'x', encoding='utf8') as x:
			yaml.dump(new_account, x)

	def log_status(self, before, after):
		with open(f'data/accounts/{before.id}.yaml', 'r', encoding='utf8') as r:
			data = yaml.load(r, Loader=yaml.FullLoader)
			status_since = data['status_times'][f'{before.status}_since']
			status_time_before = time.time() - status_since
			status_time_after = data['status_times'][f'{before.status}_time']
			status_time = status_time_before + status_time_after
			data['status_times'][f'{before.status}_time'] = round(status_time)
			with open(f'data/accounts/{before.id}.yaml', 'w', encoding='utf8') as w:
				data['status_times'][f'{after.status}_since'] = time.time()
				data['status_times'][f'{before.status}_since'] = None
				yaml.dump(data, w)

	def logging_check(self, guild, log_type):
		try:
			with open(f'data/guilds/{guild.id}.yaml', 'r', encoding='utf8') as r:
				data = yaml.load(r, Loader=yaml.FullLoader)
				logging_channel = data['config']['logging_channel']
				logging_enabled = data['config']['logging_enabled']
				log_type = data['logging'][f'{log_type}']
				if logging_channel is None or logging_enabled is False or log_type is False:
					return False
				else:
					return True
		except FileNotFoundError:
			return False

	def logging_channel(self, guild):
		with open(f'data/guilds/{guild.id}.yaml', 'r', encoding='utf8') as r:
			data = yaml.load(r, Loader=yaml.FullLoader)
			logging_channel = data['config']['logging_channel']
			return logging_channel

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		if isinstance(error, commands.CommandNotFound):
			print(error)
		elif isinstance(error, commands.CommandOnCooldown):
			return await ctx.send(f"Ratelimited. Try again in {round(error.retry_after, 2)}s")
		elif isinstance(error, commands.NoPrivateMessage):
			return await ctx.send("No commands in DM's")
		elif isinstance(error, commands.DisabledCommand):
			return await ctx.send("This command is disabled.")
		elif isinstance(error, commands.TooManyArguments):
			if isinstance(ctx.command, commands.Group):
				return await ctx.send(f"That subcommand for {ctx.command} was not recongnised. Do `{ctx.prefix}help {ctx.command}` for more information.")
			return await ctx.send(f"{ctx.command} does not take any extra arguments. Do `{ctx.prefix}help {ctx.command}` for more information")
		elif isinstance(error, commands.MissingRequiredArgument):
			return await ctx.send(f"Missing the \"{error.param.name}\" parameter.")
		elif isinstance(error, (commands.NotOwner, commands.MissingPermissions)):
			return await ctx.send("You do not have permission to use this command.")
		elif isinstance(error, commands.BotMissingPermissions):
			return await ctx.send("I don't have permission to run this command.")
		else:
			print(error)

	@commands.Cog.listener()
	async def on_command_completion(self, ctx):
		self.bot.logging.info(f'[COMMAND] - {ctx.author} used the command "{ctx.command}" in the guild {ctx.guild}.')

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		self.bot.logging.info(f'[GUILD] - Joined the guild {guild.name}.')
		channel = self.bot.get_channel(516002789617434664)
		embed = discord.Embed(
			colour=0x57FFF5,
		)
		embed.add_field(name='Guild Join', value=f'MrBot joined a guild.\nName: **{guild.name}**', inline=False)
		return await channel.send(embed=embed)

	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		self.bot.logging.info(f'[GUILD] - Left the guild {guild.name}.')
		channel = self.bot.get_channel(516002789617434664)
		embed = discord.Embed(
			colour=0x57FFF5,
		)
		embed.add_field(name='Guild Leave', value=f'MrBot left a guild.\nName: **{guild.name}**', inline=False)
		return await channel.send(embed=embed)

	@commands.Cog.listener()
	async def on_guild_update(self, before, after):
		# If the guild name has changed
		if not before.name == after.name:
			# Check if this type of logging is enabled.
			guild_name_check = await self.bot.loop.run_in_executor(None, self.logging_check, before, 'guild_name')
			if guild_name_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, before))
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
			guild_region_check = await self.bot.loop.run_in_executor(None, self.logging_check, before, 'guild_region')
			if guild_region_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, before))
				guild_name = before.name
				guild_avatar = before.icon_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"This guilds region has changed.\n\n"
				)
				embed.set_author(icon_url=guild_avatar, name=guild_name)
				embed.description += f'**Before:**\n{self.guild_region(before)}\n**After:**\n{self.guild_region(after)}'
				return await channel.send(embed=embed)
		# If the guilds afk timout has changed.
		if not before.afk_timeout == after.afk_timeout:
			# Check if this type of logging is enabled.
			guild_afk_timeout_check = await self.bot.loop.run_in_executor(None, self.logging_check, before, 'guild_afk_timeout')
			if guild_afk_timeout_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, before))
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
			guild_afk_channel_check = await self.bot.loop.run_in_executor(None, self.logging_check, before, 'guild_afk_channel')
			if guild_afk_channel_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, before))
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
			guild_system_channel_check = await self.bot.loop.run_in_executor(None, self.logging_check, before, 'guild_system_channel')
			if guild_system_channel_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, before))
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
			guild_icon_check = await self.bot.loop.run_in_executor(None, self.logging_check, before, 'guild_icon')
			if guild_icon_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, before))
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
			guild_default_notifications_check = await self.bot.loop.run_in_executor(None, self.logging_check, before, 'guild_default_notifications')
			if guild_default_notifications_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, before))
				guild_name = before.name
				guild_avatar = before.icon_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"This guilds default notification setting has changed.\n\n"
				)
				embed.set_author(icon_url=guild_avatar, name=guild_name)
				embed.description += f'**Before:**\n{self.guild_notification_settings(before)}\n**After:**\n{self.guild_notification_settings(after)}'
				return await channel.send(embed=embed)
		# If the guilds description has changed.
		if not before.description == after.description:
			# Check if this type of logging is enabled.
			guild_description_check = await self.bot.loop.run_in_executor(None, self.logging_check, before, 'guild_description')
			if guild_description_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, before))
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
			guild_mfa_level_check = await self.bot.loop.run_in_executor(None, self.logging_check, before, 'guild_mfa_level')
			if guild_mfa_level_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, before))
				guild_name = before.name
				guild_avatar = before.icon_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"This guilds MFA level has changed.\n\n"
				)
				embed.set_author(icon_url=guild_avatar, name=guild_name)
				embed.description += f'**Before:**\n{self.guild_mfa_level(before)}\n**After:**\n{self.guild_mfa_level(after)}'
				return await channel.send(embed=embed)
		# If the guilds verification level has changed.
		if not before.verification_level == after.verification_level:
			# Check if this type of logging is enabled.
			guild_mfa_level_check = await self.bot.loop.run_in_executor(None, self.logging_check, before, 'guild_verification_level')
			if guild_mfa_level_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, before))
				guild_name = before.name
				guild_avatar = before.icon_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"This guilds verification level has changed.\n\n"
				)
				embed.set_author(icon_url=guild_avatar, name=guild_name)
				embed.description += f'**Before:**\n{self.guild_verification_level(before)}\n**After:**\n{self.guild_verification_level(after)}'
				return await channel.send(embed=embed)
		# If the guilds explicit content filter has changed.
		if not before.explicit_content_filter == after.explicit_content_filter:
			# Check if this type of logging is enabled.
			guild_explicit_content_filter_check = await self.bot.loop.run_in_executor(None, self.logging_check, before, 'guild_explicit_content_filter')
			if guild_explicit_content_filter_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, before))
				guild_name = before.name
				guild_avatar = before.icon_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"This guilds explicit content filter has changed.\n\n"
				)
				embed.set_author(icon_url=guild_avatar, name=guild_name)
				embed.description += f'**Before:**\n{self.guild_content_filter_level(before)}\n**After:**\n{self.guild_content_filter_level(after)}'
				return await channel.send(embed=embed)
		# If the guilds splash has changed.
		if not before.splash == after.splash:
			# Check if this type of logging is enabled.
			guild_splash_check = await self.bot.loop.run_in_executor(None, self.logging_check, before, 'guild_splash')
			if guild_splash_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, before))
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

	@commands.Cog.listener()
	async def on_message_edit(self, before, after):
		guild = before.guild
		# If the user is the bot itself return nothing.
		if before.id == guild.me.id:
			return
		# If message has been pinned/unpinned.
		if not before.pinned == after.pinned:
			# Check if this type of logging is enabled.
			message_pin_check = await self.bot.loop.run_in_executor(None, self.logging_check, guild, 'message_pin')
			if message_pin_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, guild))
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
			message_edit_check = await self.bot.loop.run_in_executor(None, self.logging_check, guild, 'message_edit')
			if message_edit_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, guild))
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
		else:
			return

	@commands.Cog.listener()
	async def on_message_delete(self, message):
		guild = message.guild
		# If the user is the bot itself return nothing.
		if message.author.id == guild.me.id:
			return
		# Check if this type of logging is enabled.
		check = await self.bot.loop.run_in_executor(None, self.logging_check, guild, 'message_delete')
		if check is True:
			# Get the logging channel for the guild.
			channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, guild))
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

	@commands.Cog.listener()
	async def on_member_join(self, member):
		guild = member.guild
		# Check if this type of logging is enabled.
		check = await self.bot.loop.run_in_executor(None, self.logging_check, guild, 'member_join')
		if check is True:
			# Get the logging channel for the guild.
			channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, guild))
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

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		guild = member.guild
		# Check if this type of logging is enabled.
		check = await self.bot.loop.run_in_executor(None, self.logging_check, guild, 'member_leave')
		if check is True:
			# Get the logging channel for the guild.
			channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, guild))
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

	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		guild = before.guild
		# If the user is the bot, return nothing.
		if before.id == guild.me.id:
			return
		# If the members status has changed.
		if not before.status == after.status:
			# Check if this type of logging is enabled.
			member_status_check = await self.bot.loop.run_in_executor(None, self.logging_check, guild, 'member_status')
			if member_status_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, guild))
				author = after.name
				useravatar = after.avatar_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"**{before.name}**'s status has changed.\n\n"
				)
				embed.set_author(icon_url=useravatar, name=author)
				embed.description += f'**Before:**\n{self.user_status(before)}\n**After:**\n{self.user_status(after)}'
				return await channel.send(embed=embed)
			try:
				await self.bot.loop.run_in_executor(None, self.log_status, before, after)
			except FileNotFoundError:
				return
			except TypeError:
				return
		# If the members nickname has changed.
		if not before.nick == after.nick:
			# Check if this type of logging is enabled.
			member_nickname_check = await self.bot.loop.run_in_executor(None, self.logging_check, guild, 'member_nickname')
			if member_nickname_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, guild))
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
			member_role_check = await self.bot.loop.run_in_executor(None, self.logging_check, guild, 'member_role')
			if member_role_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, guild))
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
			member_activity_check = await self.bot.loop.run_in_executor(None, self.logging_check, guild, 'member_activity')
			if member_activity_check is True:
				# Get the logging channel for the guild.
				channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, guild))
				author = after.name
				useravatar = after.avatar_url
				embed = discord.Embed(
					colour=0x57FFF5,
					description=f"**{before.name}**'s activity has changed.\n\n"
				)
				embed.set_author(icon_url=useravatar, name=author)
				embed.description += f'**Before:**\n{self.user_activity(before)}\n**After:**\n{self.user_activity(after)}'
				return await channel.send(embed=embed)
		else:
			return

	@commands.Cog.listener()
	async def on_user_update(self, before, after):
		# Loop through all guilds the bot is in.
		for guild in self.bot.guilds:
			#If the user is not in the guilds, return nothing.
			if before.id or after.id not in guild.members.id:
				return
			# If the users username has changed.
			if not before.name == after.name:
				# Check if this type of logging is enabled.
				user_name_check = await self.bot.loop.run_in_executor(None, self.logging_check, guild, 'user_username')
				if user_name_check is True:
					# Get the logging channel for the guild.
					channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, guild))
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
			if not before.discriminator == after.discriminator:
				# Check if this type of logging is enabled.
				user_discriminator_check = await self.bot.loop.run_in_executor(None, self.logging_check, guild, 'user_discriminator')
				if user_discriminator_check is True:
					# Get the logging channel for the guild.
					channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, guild))
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
			if not before.avatar == after.avatar:
				# Check if this type of logging is enabled.
				user_avatar_check = await self.bot.loop.run_in_executor(None, self.logging_check, guild, 'user_avatar')
				if user_avatar_check is True:
					# Get the logging channel for the guild.
					channel = self.bot.get_channel(await self.bot.loop.run_in_executor(None, self.logging_channel, guild))
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


def setup(bot):
	bot.add_cog(Logging(bot))

