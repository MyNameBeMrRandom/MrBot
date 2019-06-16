import asyncio
import yaml
import time


def do_account_creation(ctx):
	new_account = {
		'info': {
			'name': f'{ctx.author}',
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
			'dnd_since': None,
			'dnd_time': 0,
			'idle_since': None,
			'idle_time': 0,
			'offline_since': None,
			'offline_time': 0,
			'online_since': None,
			'online_time': 0,
		}
	}
	with open(f'data/accounts/{ctx.author.id}.yaml', 'x', encoding='utf8') as x:
		yaml.dump(new_account, x)
	with open(f'data/accounts/{ctx.author.id}.yaml', 'r', encoding='utf8') as r:
		data = yaml.load(r, Loader=yaml.FullLoader)
		data['status_times'][f'{ctx.author.status}_since'] = time.time()
		with open(f'data/accounts/{ctx.author.id}.yaml', 'w', encoding='utf8') as w:
			yaml.dump(data, w)

def do_config_creation(ctx):
	new_config = {
		'config': {
			'logging_enabled': False,
			'logging_channel': None,
		},
		'logging': {
			'member_activity': False,
			'member_join': False,
			'member_leave': False,
			'member_nickname': False,
			'member_role': False,
			'member_status': False,
			'message_delete': False,
			'message_edit': False,
			'message_pin': False,
			'user_avatar': False,
			'user_discriminator': False,
			'user_username': False,
			'guild_name': False,
			'guild_region': False,
			'guild_afk_timeout': False,
			'guild_afk_channel': False,
			'guild_system_channel': False,
			'guild_icon': False,
			'guild_default_notifications': False,
			'guild_description': False,
			'guild_mfa_level': False,
			'guild_verification_level': False,
			'guild_explicit_content_filter': False,
			'guild_splash': False,
		}
	}
	with open(f'data/guilds/{ctx.guild.id}.yaml', 'x', encoding='utf8') as x:
		yaml.dump(new_config, x)

async def account_creation(ctx):
	await ctx.send(f'\nWould you like to create an account? Type `yes` to continue account creation.')
	def check(msg):
		return ctx.author == msg.author and ctx.channel == msg.channel
	try:
		response = await ctx.bot.wait_for('message', timeout=30.0, check=check)
	except asyncio.TimeoutError:
		return await ctx.send('You took to long to respond, ending account creation.')
	if response.content.lower() == 'yes':
		await ctx.send(f'Account created with ID `{ctx.author.id}`!')
		return await ctx.bot.loop.run_in_executor(None, do_account_creation, ctx)
	else:
		return await ctx.send('An account was not created.')

async def config_creation(ctx):
	await ctx.send(f'Would you like to create a config for this guild? Type `yes` to continue config creation.')
	def check(msg):
		return ctx.author == msg.author and ctx.channel == msg.channel
	try:
		response = await ctx.bot.wait_for('message', timeout=30.0, check=check)
	except asyncio.TimeoutError:
		return await ctx.send('You took to long to respond, ending config creation.')
	if response.content == 'yes':
		await ctx.send(f'Config created with ID `{ctx.guild.id}`!')
		return await ctx.bot.loop.run_in_executor(None, do_config_creation, ctx)
	else:
		return await ctx.send('A config file was no generated')
