import discord

# Get a users activity.
def user_activity(user):
	try:
		if user.status == user.status.offline:
			return 'N/A'
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

# Get a users status.
def user_status(user):
	if user.status == discord.Status.online:
		return "Online"
	elif user.status == discord.Status.idle:
		return "Idle"
	elif user.status == discord.Status.dnd:
		return "Do not Disturb"
	elif user.status == discord.Status.offline:
		return "Offline"
	else:
		return "Offline"

# Get a guilds region.
def guild_region(guild):
	if guild.region == discord.VoiceRegion.amsterdam:
		return "Amsterdam"
	elif guild.region == discord.VoiceRegion.brazil:
		return "Brazil"
	elif guild.region == discord.VoiceRegion.eu_central:
		return "Central-Europe"
	elif guild.region == discord.VoiceRegion.eu_west:
		return "Western-Europe"
	elif guild.region == discord.VoiceRegion.frankfurt:
		return "Frankfurt"
	elif guild.region == discord.VoiceRegion.hongkong:
		return "Hong-Kong"
	elif guild.region == discord.VoiceRegion.india:
		return "India"
	elif guild.region == discord.VoiceRegion.japan:
		return "Japan"
	elif guild.region == discord.VoiceRegion.london:
		return "London"
	elif guild.region == discord.VoiceRegion.russia:
		return "Russia"
	elif guild.region == discord.VoiceRegion.singapore:
		return "Singapore"
	elif guild.region == discord.VoiceRegion.southafrica:
		return "South-Africa"
	elif guild.region == discord.VoiceRegion.sydney:
		return "Sydney"
	elif guild.region == discord.VoiceRegion.us_central:
		return "Us-Central"
	elif guild.region == discord.VoiceRegion.us_east:
		return "Us-East"
	elif guild.region == discord.VoiceRegion.us_south:
		return "Us-South"
	elif guild.region == discord.VoiceRegion.us_west:
		return "Us-West"
	else:
		return "N/A"

# Get a guilds default notification level.
def guild_notification_level(guild):
	if guild.default_notifications == discord.NotificationLevel.all_messages:
		return "All messages"
	elif guild.default_notifications == discord.NotificationLevel.only_mentions:
		return "Only mentions"
	else:
		return "N/A"

# Get a guilds 2FA level.
def guild_mfa_level(guild):
	if guild.mfa_level == 0:
		return "2FA Not required"
	elif guild.mfa_level == 1:
		return "2FA Required"
	else:
		return "N/A"

# Get a guilds verification level.
def guild_verification_level(guild):
		if guild.verification_level == discord.VerificationLevel.none:
			return "None - No criteria set"
		elif guild.verification_level == discord.VerificationLevel.low:
			return "Low - Must have a verified email"
		elif guild.verification_level == discord.VerificationLevel.medium:
			return "Medium - Must have a verified email and be registered on discord for more than 5 minutes"
		elif guild.verification_level == discord.VerificationLevel.high:
			return "High - Must have a verified email, be registered on discord for more than 5 minutes and be a member of the guild for more then 10 minutes"
		elif guild.verification_level == discord.VerificationLevel.extreme:
			return "Extreme - Must have a verified email, be registered on discord for more than 5 minutes, be a member of the guild for more then 10 minutes and a have a verified phone number."
		else:
			return "N/A"

# Get a guilds content filter level.
def guild_content_filter_level(guild):
		if guild.explicit_content_filter == discord.ContentFilter.disabled:
			return "None - Content filter disabled"
		elif guild.explicit_content_filter == discord.ContentFilter.no_role:
			return "No role - Content filter enabled only for users with no roles"
		elif guild.explicit_content_filter == discord.ContentFilter.all_members:
			return "All members - Content filter enabled for all users"
		else:
			return "N/A"