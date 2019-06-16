from contextlib import redirect_stdout
from discord.ext import commands
import traceback
import textwrap
import io



# noinspection PyMethodMayBeStatic
class Owner(commands.Cog):
	"""
	Bot owner commands.
	"""

	def __init__(self, bot):
		self.bot = bot
		self._last_result = None

	async def cleanup_code(self, content):
		"""Automatically removes code blocks from the code."""
		if content.startswith('```') and content.endswith('```'):
			return '\n'.join(content.split('\n')[1:-1])
		return content.strip('` \n')

	@commands.command(name='eval')
	@commands.is_owner()
	async def eval(self, ctx, *, body: str):
		"""
		Evaluate the entered code.
		"""

		env = {
			'bot': self.bot,
			'ctx': ctx,
			'channel': ctx.channel,
			'author': ctx.author,
			'guild': ctx.guild,
			'message': ctx.message,
			'_': self._last_result
		}

		env.update(globals())

		body = await self.cleanup_code(body)
		stdout = io.StringIO()

		to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

		try:
			exec(to_compile, env)
		except Exception as e:
			return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

		# noinspection PyUnresolvedReferences
		func = env['func']
		# noinspection PyBroadException
		try:
			with redirect_stdout(stdout):
				ret = await func()
		except Exception:
			value = stdout.getvalue()
			await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
		else:
			value = stdout.getvalue()
			# noinspection PyBroadException
			try:
				await ctx.message.add_reaction('\u2705')
			except Exception:
				pass
			if ret is None:
				if value:
					await ctx.send(f'```py\n{value}\n```')
			else:
				self._last_result = ret
				await ctx.send(f'```py\n{value}{ret}\n```')


def setup(bot):
	bot.add_cog(Owner(bot))



