from discord.ext import commands
from discord.ext import buttons
from io import BytesIO
from PIL import Image
import aiofiles
import aiohttp
import discord
import typing
import ascii
import time
import art
import re


class MyPaginator(buttons.Paginator):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


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

	def do_newline(self, text, amount):
		words = text.split(' ')
		grouped_words = ['  '.join(words[i: i + amount]) for i in range(0, len(words), amount)]
		newline_text = ''
		for value in grouped_words:
			newline_text += f'{value}\n'
		return newline_text

	@commands.command(name='ascii')
	async def ascii(self, ctx, columns: typing.Optional[int] = 50, rows: typing.Optional[int] = 25, image: typing.Union[discord.Member, discord.User, str] = None):
		"""
		Converts an image into ascii.

		`columns` can be anything from 0 to 1000, This will change how many rows the image is made from.
		`rows` can be anything from 0 to 1000, This will change how many columns the image is made from.
		`image` can be an attachment, url, or another discord user.

		- When defining the amount of rows or columns, be sure to try and keep the aspect ratio of the image the same. For example if the image is square shaped, use twice the amount of columns as rows (1000, 500), if it is a rectangle use three times as many rows as columns (900, 300).
		"""
		start = time.perf_counter()
		await ctx.trigger_typing()

		if 0 >= rows or rows > 1000:
			return await ctx.send('That was not a valid number of rows, please enter something lower then `1000` and higher then `0`')
		if 0 >= columns or columns > 1000:
			return await ctx.send('That was not a valid number of columns, please enter something lower then `1000` and higher then `0`')

		if image:
			if isinstance(image, discord.Member or discord.User):
				url = str(image.avatar_url_as(format="png"))
				await self.get_image(ctx, url)
			else:
				match_url = re.compile('https?://(?:www\.)?.+/?')
				check = match_url.match(image)
				if check:
					try:
						await self.get_image(ctx, image)
					except OSError:
						return await ctx.send('That URL was not an image.')
				else:
					return await ctx.send('That was not recognised as a URL.')
		else:
			if ctx.message.attachments:
				url = ctx.message.attachments[0].url
				await self.get_image(ctx, url)
			else:
				url = str(ctx.author.avatar_url_as(format="png"))
				await self.get_image(ctx, url)

		if rows and columns:
			ascii_image = await self.bot.loop.run_in_executor(None, self.do_ascii, ctx, columns, rows)
		else:
			ascii_image = await self.bot.loop.run_in_executor(None, self.do_ascii, ctx, 50, 25)
		if len(ascii_image) > 2000:
			async with aiofiles.open(f'images/ascii/{ctx.author.id}_ascii.txt', mode='w') as f:
				await f.write(ascii_image)
			await ctx.send('The resulting art was too long, so I put it in this text file.', file=discord.File(f'images/ascii/{ctx.author.id}_ascii.txt'))
		else:
			await ctx.send(f'```{ascii_image}```')

		end = time.perf_counter()
		return await ctx.send(f'That took {end - start:.3f}sec to complete')

	@commands.command(name='font')
	async def font(self, ctx, font: str, *, text: str):
		"""
		Generate ascii text with different fonts.

		`font` can be anything from `mb fonts`.
		`text` is the text you want the art to say.

		- If you spell the fonts name wrong the bot will pick the closest matching one and use that, if you do not specify the font, a random font will be used.
		- If the art generated is over 2000 characters, it will be put into a .txt file.
		"""

		start = time.perf_counter()
		await ctx.trigger_typing()

		if not font:
			ascii_text = art.text2art(self.do_newline(text, 3), chr_ignore=True)
			if len(ascii_text) > 2000:
				async with aiofiles.open(f'images/ascii/{ctx.author.id}_font.txt', mode='w') as f:
					await f.write(ascii_text)
				await ctx.send('The resulting art was too long, so I put it in this text file.', file=discord.File(f'images/ascii/{ctx.author.id}_font.txt'))
			else:
				await ctx.send(f'```{ascii_text}```')
		else:
			try:
				if isinstance(text, discord.Emoji):
					return await ctx.send(f'Do not use emojis in the text')
				ascii_text = art.text2art(self.do_newline(text, 3),font=font, chr_ignore=True)
				if len(ascii_text) > 2000:
					async with aiofiles.open(f'images/ascii/{ctx.author.id}_font.txt', mode='w') as f:
						await f.write(ascii_text)
					await ctx.send('The resulting art was too long, so i put it in this text file.', file=discord.File(f'images/ascii/{ctx.author.id}_font.txt'))
				else:
					await ctx.send(f'```{ascii_text}```')
			except art.artError:
				return await ctx.send(f'That was not a valid font.')

		end = time.perf_counter()
		return await ctx.send(f'That took {end - start:.3f}sec to complete')

	@commands.command(name='fonts')
	async def fonts(self, ctx):

		pagey = MyPaginator(title='Silly Paginator', colour=0xc67862, embed=True, timeout=90, use_defaults=True,
		                    entries=art.font_list(), length=1, format='**')

		await pagey.start(ctx)


def setup(bot):
	bot.add_cog(Fun(bot))
