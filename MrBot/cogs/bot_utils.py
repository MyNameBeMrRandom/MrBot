from discord.ext import commands
import discord
import asyncio


class HelpCommand(commands.HelpCommand):

	def __init__(self):
		super().__init__(command_attrs={
			'help': "Shows help about the bot, an Extension or a command.\n\n**<arguement>** means the arguement is **required.**\n**[arguement]** means the arguement is **optional.**\n**[a|b]** means it can be **'A' or 'B'.**\n**[arguement...]** means you can have **multiple arguements.**"
		})

	async def on_help_command_error(self, ctx, error):
		if isinstance(error, commands.CommandInvokeError):
			await ctx.send(str(error.original))

	def get_command_signature(self, command):
		parent = command.full_parent_name
		if len(command.aliases) > 0:
			aliases = '/'.join(command.aliases)
			command_name = f'{command.name}/{aliases}'
			if parent:
				command_name = f'{self.context.prefix} {parent} {command_name}'
			else:
				command_name = f'{self.context.prefix} {command_name}'
		else:
			if parent:
				command_name = f'{self.context.prefix} {parent} {command.name}'
			else:
				command_name = f'{self.context.prefix} {command.name}'
		return command_name

	async def send_bot_help(self, mapping):
		owner = self.context.bot.get_user(238356301439041536)
		embed = discord.Embed(
			colour=0xFF0000,
			timestamp=self.context.message.created_at,
			title=f"MrBot's help page.\n\n",
			description=''
		)
		for cog in self.context.bot.cogs.values():
			if sum(1 for c in cog.get_commands() if not (self.context.author != owner and c.hidden)) == 0:
				continue
			if cog.__doc__:
				cog_help = cog.__doc__.strip().split('\n')[0]
			else:
				cog_help = 'No Help for this extension.'
			embed.description += f"**{cog.qualified_name}**:\n{cog_help}\n"
		embed.description += f"\n**Tips:**\n-You can do `{self.context.prefix} help <extension_name>` for more information on an extension and its commands.\n" \
							 f"-Make sure you use the correct capitalisation when getting help for an extension, eg `{self.context.prefix} help Images`.\n" \
							 f"-The voice extension does not currently check for permissions so be sure to give the bot the required voice chat permissions."
		return await self.context.send(embed=embed)

	async def send_cog_help(self, cog):
		owner = self.context.bot.get_user(238356301439041536)
		embed = discord.Embed(
			colour=0xFF0000,
			timestamp=self.context.message.created_at,
			description=''
		)
		embed.description += f"__**{cog.qualified_name} extension help page.**__\n\n"
		for command in cog.get_commands():
			command_name = f'{self.get_command_signature(command)}'
			if self.context.author != owner:
				if command.hidden is True:
					continue
				else:
					if command.help:
						command_help = f' - ' + command.help.strip().split('\n')[0]
					else:
						command_help = f' - No help provided for this command.'
			else:
				if command.help:
					command_help = f' - ' + command.help.strip().split('\n')[0]
				else:
					command_help = f' - No help provided for this command.'
			embed.description += f'**{command_name}**{command_help}\n'
			if isinstance(command, commands.Group):
				for group_command in command.commands:
					group_command_name = f'{self.get_command_signature(group_command)}'
					if group_command.help:
						group_command_help = f' - ' + group_command.help.strip().split('\n')[0]
					else:
						group_command_help = f' - No help provided for this command.'
					embed.description += f'\u200b \u200b \u200b \u200b \u200b**{group_command_name}**{group_command_help}\n'
		embed.description += f"\n**Tip:**\nYou can do `{self.context.prefix} <command_name>` for more information on a command and it's uses."
		return await self.context.send(embed=embed)

	async def send_command_help(self, command):
		embed = discord.Embed(
			colour=0xFF0000,
			description=''
		)
		command_name = f'{self.get_command_signature(command)}'
		if command.help:
			command_help = f'{command.help}'
		else:
			command_help = f'No help provided for this command.'
		if command.signature:
			embed.description += f'**{command_name} {command.signature}:**\n\n{command_help}\n'
		else:
			embed.description += f'**{command_name}:**\n\n{command_help}\n'
		return await self.context.send(embed=embed)

	async def send_group_help(self, group):
		embed = discord.Embed(
			colour=0xFF0000,
			description=''
		)
		group_name = f'{self.get_command_signature(group)}'
		if group.help:
			group_help = group.help.strip().split('\n')[0]
		else:
			group_help = f'No help provided for this command.'
		if group.signature:
			embed.description += f'**{group_name} {group.signature}:**\n{group_help}\n\n'
		else:
			embed.description += f'**{group_name}:**\n{group_help}\n\n'

		for command in group.commands:
			group_command_name = f'**{self.get_command_signature(command)}**'
			if command.help:
				group_command_help = f' - ' + command.help.strip().split('\n')[0]
			else:
				group_command_help = f' - No help provided for this command.'
			embed.description += f'{group_command_name}{group_command_help}\n'
		return await self.context.send(embed=embed)

class Help(commands.Cog):
	"""
	Help with how to understand and use the bots commands.
	"""

	def __init__(self, bot):
		self.bot = bot
		self.presence_task = self.bot.loop.create_task(self.activity_changing())
		self.old_help_command = bot.help_command
		bot.help_command = HelpCommand()
		bot.help_command.cog = self

	async def activity_changing(self):
		await self.bot.wait_until_ready()
		while not self.bot.is_closed():
			await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{len(self.bot.guilds)} Guilds'))
			await asyncio.sleep(60)
			await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{len(self.bot.users)} Members'))
			await asyncio.sleep(60)


def setup(bot):
	bot.add_cog(Help(bot))