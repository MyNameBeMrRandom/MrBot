from discord.ext import commands
from io import BytesIO
from PIL import Image
import aiofiles
import aiohttp
import discord
import typing
import ascii
import time


# noinspection PyMethodMayBeStatic
class Fun(commands.Cog):
	"""
	MrBot account management commands.
	"""

	def __init__(self, bot):
		self.bot = bot
		self.session = aiohttp.ClientSession(loop=bot.loop)

	async def get_image(self, ctx, url):
		# Get the users avatar and save it.
		async with self.session.get(url) as response:
			file_bytes = await response.read()
		file = Image.open(BytesIO(file_bytes))
		file.save(f'images/original_images/{ctx.author.id}.png')
		file.close()

	def do_ascii(self, ctx, columns, rows):
		ascii_image = ascii.loadFromUrl(ctx, columns=columns, rows=rows, color=False)
		return ascii_image

	@commands.command(name='ascii')
	async def ascii(self, ctx, columns: typing.Optional[int] = 50, rows: typing.Optional[int] = 25, file: typing.Union[discord.User, discord.Member, str] = None):
		"""
		Converts an image into ascii.

		`columns` can be anything from 0 to 1000, This will change how many rows the image is made from.
		`rows` can be anything from 0 to 1000, This will change how many columns the image is made from.
		`file` can be an attachment, url, or another discord user.

		It is recommended to use twice the amount of rows for the columns paramater otherwise the image will appear distorted
		"""
		start = time.perf_counter()
		await ctx.trigger_typing()

		if rows > 1000:
			return await ctx.send('That was not a valid number of rows, please enter something lower then `1000`')
		if columns > 1000:
			return await ctx.send('That was not a valid number of columns, please enter something lower then `1000`')

		if not file:
			if ctx.message.attachments:
				url = ctx.message.attachments[0].url
				await self.get_image(ctx, url)
			else:
				url = str(ctx.author.avatar_url_as(format="png"))
				await self.get_image(ctx, url)
		else:
			if file.startswith('https://') or file.startswith('http://'):
				await self.get_image(ctx, file)
			elif file == discord.User or discord.Member:
				url = str(file.avatar_url_as(format="png"))
				await self.get_image(ctx, url)

		if rows and columns:
			ascii_image = await self.bot.loop.run_in_executor(None, self.do_ascii, ctx, columns, rows)
		else:
			ascii_image = await self.bot.loop.run_in_executor(None, self.do_ascii, ctx, 50, 25)
		if len(ascii_image) > 2000:
			async with aiofiles.open(f'images/ascii/{ctx.author.id}.txt', mode='w') as f:
				await f.write(ascii_image)
			await ctx.send('The resulting art was too long, so i put it in this text file!', file=discord.File(f'images/ascii/{ctx.author.id}.txt'))
		else:
			await ctx.send(f'```{ascii_image}```')

		end = time.perf_counter()
		return await ctx.send(f'That took {end - start:.3f}sec to complete')

def setup(bot):
	bot.add_cog(Fun(bot))
