from discord.ext.commands.cooldowns import BucketType
from discord.ext import commands
from .utils import file_handling
import matplotlib.pyplot as plt
from PIL import ImageEnhance
from PIL import ImageDraw
from PIL import ImageFont
from io import BytesIO
from PIL import Image
import numpy as np
import discord
import asyncio
import aiohttp
import typing
import time
import yaml
import os


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class Images(commands.Cog):
	"""
	Image manipulation/generation commands.
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

	def round_corners(self, image, rad):
		circle = Image.new('L', (rad * 2, rad * 2), 0)
		draw = ImageDraw.Draw(circle)
		draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
		alpha = Image.new('L', image.size, 255)
		w, h = image.size
		alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
		alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
		alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
		alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
		image.putalpha(alpha)
		return image

	def do_imginfo(self, ctx, user):

		#Define the fonts.
		smallfont = ImageFont.truetype('images/resources/fonts/OpenSans-Regular.ttf', 30)
		font = ImageFont.truetype('images/resources/fonts/OpenSans-Regular.ttf', 40)
		bigfont = ImageFont.truetype('images/resources/fonts/OpenSans-Regular.ttf', 50)

		#Open the background images.
		try:
			with open(f'data/accounts/{ctx.author.id}.yaml', 'r', encoding='utf8') as r:
				data = yaml.load(r, Loader=yaml.FullLoader)
				background = data['config']['background']
				if background == 'bg_1':
					background_img = Image.open('images/resources/backgrounds/bg_1.png')
				elif background == 'bg_2':
					background_img = Image.open('images/resources/backgrounds/bg_2.png')
				elif background == 'bg_3':
					background_img = Image.open('images/resources/backgrounds/bg_3.png')
				elif background == 'bg_4':
					background_img = Image.open('images/resources/backgrounds/bg_4.png')
				elif background == 'bg_5':
					background_img = Image.open('images/resources/backgrounds/bg_5.png')
				elif background == 'bg_6':
					background_img = Image.open('images/resources/backgrounds/bg_6.png')
				elif background == 'bg_7':
					background_img = Image.open('images/resources/backgrounds/bg_7.png')
				elif background == 'bg_8':
					background_img = Image.open('images/resources/backgrounds/bg_8.png')
				elif background == 'bg_9':
					background_img = Image.open('images/resources/backgrounds/bg_9.png')
				elif background == 'bg_10':
					background_img = Image.open('images/resources/backgrounds/bg_10.png')
				elif background == 'bg_11':
					background_img = Image.open('images/resources/backgrounds/bg_11.png')
				else:
					background_img = Image.open('images/resources/backgrounds/bg_default.png')
		except FileNotFoundError:
			background_img = Image.open('images/resources/backgrounds/bg_default.png')

		# Get the users avatar and resize, and then round it.
		avatar_img = Image.open(f'images/original_images/{ctx.author.id}.png')
		avatar_img = avatar_img.resize([250, 250])
		avatar_img = self.round_corners(avatar_img, 50)

		# Copy rounded avatar image to background image.
		avatar_img = avatar_img.copy()
		background_img.paste(avatar_img, (700, 50), avatar_img)

		# Allow for drawing on the background image.
		background_draw = ImageDraw.Draw(background_img)

		# Add text to background image.
		background_draw.text((50, 35), f'{user}', (255, 255, 255),  align='center', font=bigfont)
		if user.nick is not None:
			background_draw.text((50, 90), f'{user.nick}', (255, 255, 255), align='center', font=font)

		# Add status circles to the backround image based on the users status.
		if user.status == discord.Status.online:
			background_draw.ellipse((915, 265, 965, 315), fill=(0 ,128 ,0 , 0))
		if user.status == discord.Status.idle:
			background_draw.ellipse((915, 265, 965, 315), fill=(255 ,165 ,0 , 0))
		if user.status == discord.Status.dnd:
			background_draw.ellipse((915, 265, 965, 315), fill=(255 ,0 ,0 , 0))
		if user.status == discord.Status.offline:
			background_draw.ellipse((915, 265, 965, 315), fill=(128 ,128 ,128 , 0))

		# Round the backround image and resize it.
		backround_img = self.round_corners(background_img, 100)
		backround_img = backround_img.resize([500, 500])

		# Save image.
		backround_img.save(f'images/imginfo/{user.id}_imginfo.png')

		# Close images.
		backround_img.close()
		avatar_img.close()

	def do_bg_list(self):

		# Defind the fonts.
		font = ImageFont.truetype('images/resources/fonts/OpenSans-Regular.ttf', 120)

		# Open all the images.
		bg0 = Image.open('images/resources/backgrounds/bg_default.png')
		bg1 = Image.open('images/resources/backgrounds/bg_1.png')
		bg2 = Image.open('images/resources/backgrounds/bg_2.png')
		bg3 = Image.open('images/resources/backgrounds/bg_3.png')
		bg4 = Image.open('images/resources/backgrounds/bg_4.png')
		bg5 = Image.open('images/resources/backgrounds/bg_5.png')
		bg6 = Image.open('images/resources/backgrounds/bg_6.png')
		bg7 = Image.open('images/resources/backgrounds/bg_7.png')
		bg8 = Image.open('images/resources/backgrounds/bg_8.png')
		bg9 = Image.open('images/resources/backgrounds/bg_9.png')
		bg10 = Image.open('images/resources/backgrounds/bg_10.png')
		bg11 = Image.open('images/resources/backgrounds/bg_11.png')

		# Make a new image and paste images into it.
		example = Image.new('RGB', (4000, 3600))
		example.paste(im=bg0, box=(0, 200))
		example.paste(im=bg1, box=(1000, 200))
		example.paste(im=bg2, box=(2000, 200))
		example.paste(im=bg3, box=(3000, 200))
		example.paste(im=bg4, box=(0, 1400))
		example.paste(im=bg5, box=(1000, 1400))
		example.paste(im=bg6, box=(2000, 1400))
		example.paste(im=bg7, box=(3000, 1400))
		example.paste(im=bg8, box=(0, 2600))
		example.paste(im=bg9, box=(1000, 2600))
		example.paste(im=bg10, box=(2000, 2600))
		example.paste(im=bg11, box=(3000, 2600))

		# Allow for drawing on the image.
		example_draw = ImageDraw.Draw(example)

		# Names for each background.
		example_draw.text((10, 15), f'bg_default', (255, 255, 255),  align='center', font=font)
		example_draw.text((1010, 15), f'bg_1', (255, 255, 255),  align='center', font=font)
		example_draw.text((2010, 15), f'bg_2', (255, 255, 255), align='center', font=font)
		example_draw.text((3010, 15), f'bg_3', (255, 255, 255), align='center', font=font)
		example_draw.text((10, 1215), f'bg_4', (255, 255, 255), align='center', font=font)
		example_draw.text((1010, 1215), f'bg_5', (255, 255, 255), align='center', font=font)
		example_draw.text((2010, 1215), f'bg_6', (255, 255, 255), align='center', font=font)
		example_draw.text((3010, 1215), f'bg_7', (255, 255, 255), align='center', font=font)
		example_draw.text((10, 2415), f'bg_8', (255, 255, 255), align='center', font=font)
		example_draw.text((1010, 2415), f'bg_9', (255, 255, 255), align='center', font=font)
		example_draw.text((2010, 2415), f'bg_10', (255, 255, 255), align='center', font=font)
		example_draw.text((3010, 2415), f'bg_11', (255, 255, 255), align='center', font=font)

		# Resize image and save it.
		example = example.resize([1000,900])
		example.save(f'images/resources/example/example.png')

		# Close images.
		bg0.close()
		bg1.close()
		bg2.close()
		bg3.close()
		bg4.close()
		bg5.close()
		bg6.close()
		bg7.close()
		bg8.close()
		bg9.close()
		bg10.close()
		bg11.close()
		example.close()

	def do_bg_change(self, user, new_background):
		with open(f'data/accounts/{user.id}.yaml', 'r', encoding='utf8') as r:
			data = yaml.load(r, Loader=yaml.FullLoader)
			old_background = data['config']['background']
			data['config']['background'] = new_background
			with open(f'data/accounts/{user.id}.yaml', 'w', encoding='utf8') as w:
				yaml.dump(data, w)
		return old_background

	def do_sharpen(self, ctx, amount):
		file = Image.open(f'images/original_images/{ctx.author.id}.png')
		enhancer = ImageEnhance.Sharpness(file)
		file = enhancer.enhance(amount)
		file.save(f'images/edited_images/{ctx.author.id}_sharpness_{amount}.png')
		file.close()

	def do_contrast(self, ctx, amount):
		file = Image.open(f'images/original_images/{ctx.author.id}.png')
		enhancer = ImageEnhance.Contrast(file)
		file = enhancer.enhance(amount)
		file.save(f'images/edited_images/{ctx.author.id}_contrast_{amount}.png')
		file.close()

	def do_colour(self, ctx, amount):
		file = Image.open(f'images/original_images/{ctx.author.id}.png')
		enhancer = ImageEnhance.Color(file)
		file = enhancer.enhance(amount)
		file.save(f'images/edited_images/{ctx.author.id}_colour_{amount}.png')
		file.close()

	def do_brightness(self, ctx, amount):
		file = Image.open(f'images/original_images/{ctx.author.id}.png')
		enhancer = ImageEnhance.Brightness(file)
		file = enhancer.enhance(amount)
		file.save(f'images/edited_images/{ctx.author.id}_brightness_{amount}.png')
		file.close()

	def calculate_status_percentages(self, online_time, offline_time, idle_time, dnd_time):
		total = online_time + offline_time + idle_time + dnd_time
		online_p = online_time / total
		offline_p = offline_time / total
		idle_p = idle_time / total
		dnd_p = dnd_time / total
		online_percent = round(online_p * 100, 3)
		offline_percent = round(offline_p * 100, 3)
		idle_percent = round(idle_p * 100, 3)
		dnd_percent = round(dnd_p * 100, 3)
		return online_percent, offline_percent, idle_percent, dnd_percent

	def do_status_pie(self, ctx):
		# Get the times in seconds.
		online_time, offline_time, idle_time, dnd_time = await self.bot.loop.run_in_executor(None, file_handling.get_status_times, ctx)
		# Calculate the percentages of each status.
		online_percent, offline_percent, idle_percent, dnd_percent = self.calculate_status_percentages(online_time, offline_time, idle_time, dnd_time)

		# Set labels sizes and colours.
		labels = [f'Online: {online_percent}%', f'Idle: {idle_percent}%', f'DnD: {dnd_percent}%', f'Offline: {offline_percent}%']
		sizes = [online_time, idle_time, dnd_time, offline_time]
		colors = ['#7acba6', '#fcc15d', '#f57e7e', '#9ea4af']

		# Create pie chart.
		fig, axs = plt.subplots()
		axs.pie(sizes, colors=colors,shadow=True, startangle=90)
		axs.legend(labels, loc="best")
		axs.axis('equal')
		plt.tight_layout()
		# Save and close pie chart.
		plt.savefig(f'images/charts/{ctx.author.id}_status_pie.png', transparent=True)
		plt.close()

	def do_pie_chart(self, ctx, names, numbers):

		labels = []
		percentages = []

		total = sum(numbers)
		for value in numbers:
			value = round(value / total * 100, 2)
			percentages.append(value)

		for name, percentage in zip(names, percentages):
			labels.append(f'{name}: {percentage}%')

		sizes = numbers

		fig, axs = plt.subplots()
		axs.pie(sizes, shadow=True, startangle=90)
		axs.legend(labels, loc="best")
		axs.axis('equal')
		plt.tight_layout()
		plt.savefig(f'images/charts/{ctx.author.id}_pie_chart.png', transparent=True)
		plt.close()

	def do_bar_chart(self, ctx, title, xlabel, ylabel, names, numbers):

		x_pos = np.arange(len(names))

		plt.bar(x_pos, numbers)
		plt.ylabel(ylabel)
		plt.ylabel(xlabel)
		plt.title(title)
		plt.xticks(x_pos, names)
		plt.tight_layout()
		plt.savefig(f'images/charts/{ctx.author.id}_bar_chart.png')
		plt.close()

	@commands.command(name='imginfo')
	async def imginfo(self, ctx, *, user: discord.Member = None):
		"""
		Generate an image with information abount you and your account.
		"""
		if not user:
			user = ctx.author

		# Start typing and timer
		await ctx.trigger_typing()
		start = time.perf_counter()

		# Get the users avatar.
		url = str(user.avatar_url_as(format="png"))
		await self.get_image(ctx, url)

		# Generate image.
		await self.bot.loop.run_in_executor(None, self.do_imginfo, ctx, user)
		await ctx.send(file=discord.File(f'images/imginfo/{user.id}_imginfo.png'))

		# End timer and log how long operation took.
		end = time.perf_counter()
		return await ctx.send(f'That took {end - start:.3f}sec to complete')

	@commands.command(name='bg_list', aliases=['bg_l', 'bgl'])
	async def bg_list(self, ctx):
		"""
		Display a list of possible backgrounds you can have.
		"""
		# Start typing and timer
		start = time.perf_counter()
		await ctx.trigger_typing()

		# Generate image.
		await self.bot.loop.run_in_executor(None, self.do_bg_list)
		await ctx.send(file=discord.File(f'images/resources/example/example.png'))

		# End timer and log how long operation took
		end = time.perf_counter()
		return await ctx.send(f'That took {end - start:.3f}sec to complete')

	@commands.command(name='bg_change', aliases=['bg_c', 'bgc'])
	async def bg_change(self, ctx, new_background):
		"""
		Changes your "imginfo" background to the one specified.
		"""
		try:
			author = ctx.author.name
			useravatar = ctx.author.avatar_url
			if not os.path.isfile(f'images/resources/backgrounds/{new_background}.png'):
				return await ctx.send('That was not a recognised background.')
			else:
				old_background = await self.bot.loop.run_in_executor(None, self.do_bg_change, ctx.author, new_background)
				embed = discord.Embed(
					colour=0x57FFF5,
					timestamp=ctx.message.created_at,
					description=f'Changed your background from `{old_background}` to `{new_background}`'
				)
				embed.set_author(icon_url=useravatar, name=author)
				return await ctx.send(embed=embed)
		except FileNotFoundError:
			await ctx.send(f'You dont have an account.')
			return await file_handling.account_creation(ctx)

	@commands.command(name='sharpen')
	async def sharpen(self, ctx, amount: float, file: typing.Union[discord.User, discord.Member, str] = None):
		"""
		Sharpens an image by the factor specified.

		`amount` can be anything from 0 to 999999999.
		`file` can be an attachment, url, or another discord user.
		"""
		start = time.perf_counter()
		await ctx.trigger_typing()
		if not 0 <= amount <= 999999999:
			return await ctx.send('That was not a valid amount.')
		if ctx.message.attachments:
			url = ctx.message.attachments[0].url
			await self.get_image(ctx, url)
		elif file == discord.User or discord.Member:
			url = str(file.avatar_url_as(format="png"))
			await self.get_image(ctx, url)
		elif not file:
			url = str(ctx.author.avatar_url_as(format="png"))
			await self.get_image(ctx, url)
		else:
			await self.get_image(ctx, file)

		await self.bot.loop.run_in_executor(None, self.do_sharpen, ctx, amount)
		await ctx.send(f'Sharpened by a factor of `{amount}`.' ,file=discord.File(f'images/edited_images/{ctx.author.id}_sharpness_{amount}.png'))

		end = time.perf_counter()
		return await ctx.send(f'That took {end - start:.3f}sec to complete')

	@commands.command(name='contrast')
	async def contrast(self, ctx, amount: float, file: typing.Union[discord.User, discord.Member, str] = None):
		"""
		Changes the contrast of an image by the factor specified.

		`amount` can be anything from 0 to 999999999.
		`file` can be an attachment, url, or another discord user.
		"""
		start = time.perf_counter()
		await ctx.trigger_typing()
		if not 0 <= amount <= 999999999:
			return await ctx.send('That was not a valid amount.')
		if ctx.message.attachments:
			url = ctx.message.attachments[0].url
			await self.get_image(ctx, url)
		elif file == discord.User or discord.Member:
			url = str(file.avatar_url_as(format="png"))
			await self.get_image(ctx, url)
		elif not file:
			url = str(ctx.author.avatar_url_as(format="png"))
			await self.get_image(ctx, url)
		else:
			await self.get_image(ctx, file)

		await self.bot.loop.run_in_executor(None, self.do_contrast, ctx, amount)
		await ctx.send(f'Contrast changed by a factor of `{amount}`.' ,file=discord.File(f'images/edited_images/{ctx.author.id}_contrast_{amount}.png'))

		end = time.perf_counter()
		return await ctx.send(f'That took {end - start:.3f}sec to complete')

	@commands.command(name='colour')
	async def colour(self, ctx, amount: float, file: typing.Union[discord.User, discord.Member, str] = None):
		"""
		Changes the colour of an image by the factor specified.

		`amount` can be anything from 0 to 999999999. 0.00 to 1.00 will produce an image with less colour and anything above 1 will increase the colour.
		`file` can be an attachment, url, or another discord user.
		"""
		start = time.perf_counter()
		await ctx.trigger_typing()
		if not 0 <= amount <= 999999999:
			return await ctx.send('That was not a valid amount.')
		if ctx.message.attachments:
			url = ctx.message.attachments[0].url
			await self.get_image(ctx, url)
		elif file == discord.User or discord.Member:
			url = str(file.avatar_url_as(format="png"))
			await self.get_image(ctx, url)
		elif not file:
			url = str(ctx.author.avatar_url_as(format="png"))
			await self.get_image(ctx, url)
		else:
			await self.get_image(ctx, file)

		await self.bot.loop.run_in_executor(None, self.do_colour, ctx, amount)
		await ctx.send(f'Colour shifted by a factor of `{amount}`.' ,file=discord.File(f'images/edited_images/{ctx.author.id}_colour_{amount}.png'))

		end = time.perf_counter()
		return await ctx.send(f'That took {end - start:.3f}sec to complete')

	@commands.command(name='brightness')
	async def brightness(self, ctx, amount: float, file: typing.Union[discord.User, discord.Member, str] = None):
		"""
		Changes the brightness of an image by the factor specified.

		`amount` can be anything from 0 to 999999999. 0.00 to 1.00 will produce an image with less brightness and anything above 1 will increase the brightness.
		`file` can be an attachment, url, or another discord user.
		"""
		start = time.perf_counter()
		await ctx.trigger_typing()
		if not 0 <= amount <= 999999999:
			return await ctx.send('That was not a valid amount.')
		if ctx.message.attachments:
			url = ctx.message.attachments[0].url
			await self.get_image(ctx, url)
		elif file == discord.User or discord.Member:
			url = str(file.avatar_url_as(format="png"))
			await self.get_image(ctx, url)
		elif not file:
			url = str(ctx.author.avatar_url_as(format="png"))
			await self.get_image(ctx, url)
		else:
			await self.get_image(ctx, file)

		await self.bot.loop.run_in_executor(None, self.do_brightness, ctx, amount)
		await ctx.send(f'Brightness changed by a factor of `{amount}`.' ,file=discord.File(f'images/edited_images/{ctx.author.id}_brightness_{amount}.png'))

		end = time.perf_counter()
		return await ctx.send(f'That took {end - start:.3f}sec to complete')

	@commands.command(name='status_pie', aliases=['status_p', 'sp'])
	async def status_pie(self, ctx):
		"""
		Generates a pie chart with values corresponding to the amount of time you have been online, offline, dnd, idle.

		You must have an account for this to work, use `mb account create` to create one.
		"""
		try:
			start = time.perf_counter()
			await ctx.trigger_typing()
			await self.bot.loop.run_in_executor(None, self.do_status_pie, ctx)
			await ctx.send(file=discord.File(f'images/charts/{ctx.author.id}_status_pie.png'))
			end = time.perf_counter()
			return await ctx.send(f'That took {end - start:.3f}sec to complete')
		except FileNotFoundError:
			await ctx.send(f'You dont have an account.')
			return await file_handling.account_creation(ctx)

	@commands.cooldown(1, 10, BucketType.user)
	@commands.command(name='pie_chart', aliases=['pie_c', 'pc'])
	async def pie_chart(self, ctx):
		"""
		Launches an interactive pie chart creator.

		Make sure you use this in a quiet channel, otherwise the message will get lost in the chat.
		"""

		def check(msg):
			return ctx.author == msg.author and ctx.channel == msg.channel

		message = await ctx.send(f'How many values would you like in your pie chart? (1 - 50). You can type `cancel` at any point to end creation.')

		try:
			number_of_values = await ctx.bot.wait_for('message', timeout=30.0, check=check)
			if number_of_values.content.startswith(ctx.prefix):
				return await ctx.send(f'{ctx.author.mention}, That is not a valid amount of values, do not use a bot command as a value.')
			if number_of_values.content == 'cancel':
				return await ctx.send('Ended pie chart creation.')
			number_of_values = int(number_of_values.content)
			if number_of_values <= 0 or number_of_values >= 51:
				return await ctx.send(f'{ctx.author.mention}, That is not avalid number of values, please choose a value between 1 and 50.')
		except asyncio.TimeoutError:
			return await ctx.send(f'{ctx.author.mention}, You took to long to respond, ending pie chart creation.')
		except ValueError:
			return await ctx.send(f'{ctx.author.mention}, That was not a valid number of values, make sure you use a number.')

		number_values = []
		name_values = []
		value = 1

		for i in range(number_of_values):

			await message.edit(content=f'Enter a name for value `{value}`:')
			try:
				name = await ctx.bot.wait_for('message', timeout=30.0, check=check)
				if name.content.startswith(ctx.prefix):
					return await ctx.send(f'{ctx.author.mention}, That is not a valid name for a value, do not use a bot command as a value.')
				if name.content == 'cancel':
					return await ctx.send(f'Ended pie chart creation.')
				name_values.append(name.content)
			except asyncio.TimeoutError:
				return await ctx.send(f'{ctx.author.mention}, You took to long to respond, ending pie chart creation.')

			await message.edit(content=f'Enter a number for value `{value}`:')
			try:
				number = await ctx.bot.wait_for('message', timeout=30.0, check=check)
				if name.content.startswith(ctx.prefix):
					return await ctx.send(f'{ctx.author.mention}, That is not a valid number for a value, do not use a bot command as a value.')
				if number.content == 'cancel':
					return await ctx.send(f'Ended pie chart creation.')
				number_values.append(int(number.content))
			except asyncio.TimeoutError:
				return await ctx.send(f'{ctx.author.mention}, You took to long to respond, ending pie chart creation.')
			except ValueError:
				return await ctx.send(f'{ctx.author.mention}, You did not enter a valid number.')
			value += 1

		try:
			start = time.perf_counter()
			await ctx.trigger_typing()
			await self.bot.loop.run_in_executor(None, self.do_pie_chart, ctx, name_values, number_values)
			await ctx.send(file=discord.File(f'images/charts/{ctx.author.id}_pie_chart.png'))
			end = time.perf_counter()
			return await ctx.send(f'That took {end - start:.3f}sec to complete')
		except FileNotFoundError:
			await ctx.send(f'You dont have an account.')
			return await file_handling.account_creation(ctx)

	@commands.cooldown(1, 10, BucketType.user)
	@commands.command(name='bar_chart', aliases=['bar_c', 'bc'])
	async def bar_chart(self, ctx):
		"""
		Launches an interactive bar chart creator.

		Make sure you use this in a quiet channel, otherwise the message will get lost in the chat.
		"""

		def check(msg):
			return ctx.author == msg.author and ctx.channel == msg.channel

		message = await ctx.send(f'How many values would you like in your bar chart? (1 - 10). You can type `cancel` at any point to end creation.')

		try:
			number_of_values = await ctx.bot.wait_for('message', timeout=30.0, check=check)
			if number_of_values.content.startswith(ctx.prefix):
				return await ctx.send(f'{ctx.author.mention}, That is not a valid amount of values, do not use a bot command as a value.')
			if number_of_values.content == 'cancel':
				return await ctx.send('Ended bar chart creation.')
			number_of_values = int(number_of_values.content)
			if number_of_values <= 0 or number_of_values >= 11:
				return await ctx.send(f'{ctx.author.mention}, That is not avalid number of values, please choose a value between 1 and 10.')
		except asyncio.TimeoutError:
			return await ctx.send(f'{ctx.author.mention}, You took to long to respond, ending bar chart creation.')
		except ValueError:
			return await ctx.send(f'{ctx.author.mention}, That was not a valid number of values, make sure you use a number.')

		await message.edit(content=f'What would you like the `title` of the bar chart to be?')
		try:
			title = await ctx.bot.wait_for('message', timeout=30.0, check=check)
			if title.content.startswith(ctx.prefix):
				return await ctx.send(f'{ctx.author.mention}, That is not a valid title for the chart, do not use a bot command as a title.')
			if title.content == 'cancel':
				return await ctx.send(f'Ended bar chart creation.')
			title = title.content
		except asyncio.TimeoutError:
			return await ctx.send(f'{ctx.author.mention}, You took to long to respond, ending bar chart creation.')

		await message.edit(content=f'What would you like the x-axis label of the bar chart to be?')
		try:
			xlabel = await ctx.bot.wait_for('message', timeout=30.0, check=check)
			if xlabel.content.startswith(ctx.prefix):
				return await ctx.send(f'{ctx.author.mention}, That is not a valid x-axis label for the chart, do not use a bot command as a label.')
			if xlabel.content == 'cancel':
				return await ctx.send(f'Ended bar chart creation.')
			xlabel = xlabel.content
		except asyncio.TimeoutError:
			return await ctx.send(f'{ctx.author.mention}, You took to long to respond, ending bar chart creation.')

		await message.edit(content=f'What would you like the y-axis label of the bar chart to be?')
		try:
			ylabel = await ctx.bot.wait_for('message', timeout=30.0, check=check)
			if ylabel.content.startswith(ctx.prefix):
				return await ctx.send(f'{ctx.author.mention}, That is not a valid y-axis label for the chart, do not use a bot command as a label.')
			if ylabel.content == 'cancel':
				return await ctx.send(f'Ended bar chart creation.')
			ylabel = ylabel.content
		except asyncio.TimeoutError:
			return await ctx.send(f'{ctx.author.mention}, You took to long to respond, ending bar chart creation.')

		number_values = []
		name_values = []
		value = 1

		for i in range(number_of_values):

			await message.edit(content=f'Enter a name for value `{value}`:')
			try:
				name = await ctx.bot.wait_for('message', timeout=30.0, check=check)
				if name.content.startswith(ctx.prefix):
					return await ctx.send(f'{ctx.author.mention}, That is not a valid name for a value, do not use a bot command as a value.')
				if name.content == 'cancel':
					return await ctx.send(f'Ended bar chart creation.')
				name_values.append(name.content)
			except asyncio.TimeoutError:
				return await ctx.send(f'{ctx.author.mention}, You took to long to respond, ending pie chart creation.')

			await message.edit(content=f'Enter a number for value `{value}`:')
			try:
				number = await ctx.bot.wait_for('message', timeout=30.0, check=check)
				if name.content.startswith(ctx.prefix):
					return await ctx.send(f'{ctx.author.mention}, That is not a valid number for a value, do not use a bot command as a value.')
				if number.content == 'cancel':
					return await ctx.send(f'Ended bar chart creation.')
				number_values.append(int(number.content))
			except asyncio.TimeoutError:
				return await ctx.send(f'{ctx.author.mention}, You took to long to respond, ending bar chart creation.')
			except ValueError:
				return await ctx.send(f'{ctx.author.mention}, You did not enter a valid number.')
			value += 1

		try:
			start = time.perf_counter()
			await ctx.trigger_typing()
			await self.bot.loop.run_in_executor(None, self.do_bar_chart, ctx, title, xlabel, ylabel, name_values, number_values)
			await ctx.send(file=discord.File(f'images/charts/{ctx.author.id}_bar_chart.png'))
			end = time.perf_counter()
			return await ctx.send(f'That took {end - start:.3f}sec to complete')
		except FileNotFoundError:
			await ctx.send(f'You dont have an account.')
			return await file_handling.account_creation(ctx)


def setup(bot):
	bot.add_cog(Images(bot))

