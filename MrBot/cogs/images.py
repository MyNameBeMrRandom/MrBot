from discord.ext.commands.cooldowns import BucketType
from discord.ext import commands
from .utils import file_handling
import matplotlib.pyplot as plt
from PIL import ImageEnhance
from PIL import ImageDraw
from PIL import ImageFont
from io import BytesIO
from PIL import Image
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

		# Font
		font = ImageFont.truetype('data/fonts/OpenSans-Regular.ttf', 120)

		#Open images
		bg0 = Image.open('images/backgrounds/bg_default.png')
		bg1 = Image.open('images/backgrounds/bg_1.png')
		bg2 = Image.open('images/backgrounds/bg_2.png')
		bg3 = Image.open('images/backgrounds/bg_3.png')
		bg4 = Image.open('images/backgrounds/bg_4.png')
		bg5 = Image.open('images/backgrounds/bg_5.png')
		bg6 = Image.open('images/backgrounds/bg_6.png')
		bg7 = Image.open('images/backgrounds/bg_7.png')
		bg8 = Image.open('images/backgrounds/bg_8.png')
		bg9 = Image.open('images/backgrounds/bg_9.png')
		bg10 = Image.open('images/backgrounds/bg_10.png')
		bg11 = Image.open('images/backgrounds/bg_11.png')


		#Make new image
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

		#Allow for drawing on image
		example_draw = ImageDraw.Draw(example)

		#Names for each background
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

		#Resize image and save it
		example = example.resize([1000,900])
		example.save(f'images/example/example.png')
		output = BytesIO()
		example.save(output, 'png')
		output.seek(0)

		#Close images
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

		#Return image
		return output

	def do_sharpen(self, ctx, amount):
		file = Image.open(f'images/files/{ctx.author.id}.png')
		enhancer = ImageEnhance.Sharpness(file)
		file = enhancer.enhance(amount)
		file.save(f'images/files/{ctx.author.id}_sharpened_{amount}.png')
		output = BytesIO()
		file.save(output, 'png')
		output.seek(0)
		return output

	def do_contrast(self, ctx, amount):
		file = Image.open(f'images/files/{ctx.author.id}.png')
		enhancer = ImageEnhance.Contrast(file)
		file = enhancer.enhance(amount)
		file.save(f'images/files/{ctx.author.id}_contrast_{amount}.png')
		output = BytesIO()
		file.save(output, 'png')
		output.seek(0)
		return output

	def do_colour(self, ctx, amount):
		file = Image.open(f'images/files/{ctx.author.id}.png')
		enhancer = ImageEnhance.Color(file)
		file = enhancer.enhance(amount)
		file.save(f'images/files/{ctx.author.id}_color_{amount}.png')
		output = BytesIO()
		file.save(output, 'png')
		output.seek(0)
		return output

	def do_brightness(self, ctx, amount):
		file = Image.open(f'images/files/{ctx.author.id}.png')
		enhancer = ImageEnhance.Brightness(file)
		file = enhancer.enhance(amount)
		file.save(f'images/files/{ctx.author.id}_brightness_{amount}.png')
		output = BytesIO()
		file.save(output, 'png')
		output.seek(0)
		return output

	def do_change_background(self, user, new_background):
		with open(f'data/accounts/{user.id}.yaml', 'r', encoding='utf8') as r:
			data = yaml.load(r, Loader=yaml.FullLoader)
			old_background = data['config']['background']
			data['config']['background'] = new_background
			with open(f'data/accounts/{user.id}.yaml', 'w', encoding='utf8') as w:
				yaml.dump(data, w)
		return old_background

	def do_status_times(self, ctx):
		with open(f'data/accounts/{ctx.author.id}.yaml', 'r', encoding='utf8') as r:
			data = yaml.load(r, Loader=yaml.FullLoader)

			status_since = data['status_times'][f'{ctx.author.status}_since']
			status_time_before = time.time() - status_since
			current_status = round(status_time_before)

			online_time = data['status_times'][f'online_time']
			offline_time = data['status_times'][f'offline_time']
			idle_time = data['status_times'][f'idle_time']
			dnd_time = data['status_times'][f'dnd_time']
			if ctx.author.status == discord.Status.online:
				return online_time + current_status, offline_time, idle_time, dnd_time
			elif ctx.author.status == discord.Status.offline:
				return online_time, offline_time + current_status, idle_time, dnd_time
			elif ctx.author.status == discord.Status.idle:
				return online_time, offline_time, idle_time + current_status, dnd_time
			elif ctx.author.status == discord.Status.dnd:
				return online_time, offline_time, idle_time, dnd_time + current_status
			else:
				return online_time, offline_time, idle_time, dnd_time

	def calculate_status_percent(self, online, offline, idle, dnd):
		total = online + offline + idle + dnd
		online_p = online / total
		offline_p = offline / total
		idle_p = idle / total
		dnd_p = dnd / total
		online_percent = round(online_p * 100, 1)
		offline_percent = round(offline_p * 100, 1)
		idle_percent = round(idle_p * 100, 1)
		dnd_percent = round(dnd_p * 100, 1)
		return online_percent, offline_percent, idle_percent, dnd_percent

	def do_status_pie(self, ctx):
		online_time, offline_time, idle_time, dnd_time = self.do_status_times(ctx)
		online_percent, offline_percent, idle_percent, dnd_percent = self.calculate_status_percent(online_time, offline_time, idle_time, dnd_time)

		labels = [f'Online: {online_percent}%', f'Idle: {idle_percent}%', f'DnD: {dnd_percent}%', f'Offline: {offline_percent}%']
		sizes = [online_time, idle_time, dnd_time, offline_time]
		colors = ['#7acba6', '#fcc15d', '#f57e7e', '#9ea4af']

		fig, axs = plt.subplots()
		axs.pie(sizes, colors=colors,shadow=True, startangle=90)
		axs.legend(labels, loc="best")
		axs.axis('equal')
		plt.tight_layout()
		plt.savefig(f'images/pie_charts/{ctx.author.id}_status_pie.png', transparent=True)
		plt.close()

	def do_pie_chart(self, ctx, names, numbers):

		labels = []
		percentages = []

		total = sum(numbers)
		for value in numbers:
			value = round(value / total * 100, 2)
			percentages.append(value)

		for name, number in zip(names, percentages):
			labels.append(f'{name}: {number}%')

		sizes = numbers

		fig, axs = plt.subplots()
		axs.pie(sizes, shadow=True, startangle=90)
		axs.legend(labels, loc="best")
		axs.axis('equal')
		plt.tight_layout()
		plt.savefig(f'images/pie_charts/{ctx.author.id}_pie_chart.png', transparent=True)
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

		# End timer and log how long operation took
		end = time.perf_counter()
		return await ctx.send(f'That took {end - start:.3f}sec to complete')

	@commands.command(name='bg_list', aliases=['bg_l', 'bgl'])
	async def bg_list(self, ctx):
		"""
		Display a list of possible backgrounds you can have.
		"""
		start = time.perf_counter()
		await ctx.trigger_typing()
		await ctx.send(file=discord.File(await self.bot.loop.run_in_executor(None, self.do_bg_list), filename=f'example.png',))
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
			if not os.path.isfile(f'images/backgrounds/{new_background}.png'):
				return await ctx.send('That was not a recognised background.')
			else:
				old_background = await self.bot.loop.run_in_executor(None, self.do_change_background, ctx.author, new_background)
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
	async def sharpen(self, ctx, amount: float, file: typing.Union[str, discord.User] = None):
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
		elif not file:
			url = str(ctx.author.avatar_url_as(format="png"))
			await self.get_image(ctx, url)
		elif file == discord.User:
			url = str(file.avatar_url_as(format="png"))
			await self.get_image(ctx, url)
		else:
			await self.get_image(ctx, file)
		await ctx.send(f'Sharpened by a factor of `{amount}`.' ,file=discord.File(await self.bot.loop.run_in_executor(None, self.do_sharpen, ctx, amount), filename = f'example.png',))
		end = time.perf_counter()
		return await ctx.send(f'That took {end - start:.3f}sec to complete')

	@commands.command(name='contrast')
	async def contrast(self, ctx, amount: float, file: typing.Union[str, discord.User] = None):
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
		elif not file:
			url = str(ctx.author.avatar_url_as(format="png"))
			await self.get_image(ctx, url)
		elif file == discord.User:
			url = str(file.avatar_url_as(format="png"))
			await self.get_image(ctx, url)
		else:
			await self.get_image(ctx, file)
		await ctx.send(f'Contrast changed by a factor of `{amount}`.' ,file=discord.File(await self.bot.loop.run_in_executor(None, self.do_contrast, ctx, amount), filename = f'example.png',))
		end = time.perf_counter()
		return await ctx.send(f'That took {end - start:.3f}sec to complete')

	@commands.command(name='colour')
	async def colour(self, ctx, amount: float, file: typing.Union[str, discord.User] = None):
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
		elif not file:
			url = str(ctx.author.avatar_url_as(format="png"))
			await self.get_image(ctx, url)
		elif file == discord.User:
			url = str(file.avatar_url_as(format="png"))
			await self.get_image(ctx, url)
		else:
			await self.get_image(ctx, file)
		await ctx.send(f'Colour shifted by a factor of `{amount}`.' ,file=discord.File(await self.bot.loop.run_in_executor(None, self.do_colour, ctx, amount), filename = f'example.png',))
		end = time.perf_counter()
		return await ctx.send(f'That took {end - start:.3f}sec to complete')

	@commands.command(name='brightness')
	async def brightness(self, ctx, amount: float, file: typing.Union[str, discord.User, discord.User] = None):
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
		elif not file:
			url = str(ctx.author.avatar_url_as(format="png"))
			await self.get_image(ctx, url)
		elif file == discord.User:
			url = str(file.avatar_url_as(format="png"))
			await self.get_image(ctx, url)
		else:
			await self.get_image(ctx, file)
		await ctx.send(f'Brightness changed by a factor of `{amount}`.' ,file=discord.File(await self.bot.loop.run_in_executor(None, self.do_brightness, ctx, amount), filename=f'example.png'))
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
			await ctx.send(file=discord.File(f'images/pie_charts/{ctx.author.id}_status_pie.png'))
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

		message = await ctx.send(f'How many values would you like in your pie chart? (e.g 5, 10, 15). You can type `cancel` at any point to end creation.')

		try:
			number_of_values = await ctx.bot.wait_for('message', timeout=20.0, check=check)
			if number_of_values.content == 'cancel':
				return await ctx.send('Ended pie chart creation.')
			number_of_values = int(number_of_values.content)
		except asyncio.TimeoutError:
			return await message.edit(content='You took to long to respond, ending pie chart creation.')
		except ValueError:
			return await message.edit(content=f'That was not a valid number of values, make sure you use a number.')

		if number_of_values <= 0 or number_of_values >= 51:
			return await message.edit(content='That was not a valid number of values, Please choose a value between 1 and 50.')



		number_values = []
		name_values = []
		name_and_numbers = []
		value = 1

		for i in range(number_of_values):

			await message.edit(content=f'Enter a name for value `{value}`:')
			try:
				name = await ctx.bot.wait_for('message', timeout=30.0, check=check)
				if name.content.startswith(ctx.prefix):
					return await ctx.send('That is not a valid name for a value, do not use a bot command as a value.')
				if name.content == 'cancel':
					return await ctx.send('Ended pie chart creation.')
				name_values.append(name.content)
			except asyncio.TimeoutError:
				return await message.edit(content='You took to long to respond, ending pie chart creation.')

			await message.edit(content=f'Enter a number for value `{value}`:')
			try:
				number = await ctx.bot.wait_for('message', timeout=30.0, check=check)
				if number.content == 'cancel':
					return await ctx.send('Ended pie chart creation.')
				number_values.append(int(number.content))
			except asyncio.TimeoutError:
				return await message.edit(content='You took to long to respond, ending pie chart creation.')
			except ValueError:
				return await message.edit(content='You did not enter a valid number.')
			value += 1

		try:
			start = time.perf_counter()
			await ctx.trigger_typing()
			await self.bot.loop.run_in_executor(None, self.do_pie_chart, ctx, name_values, number_values)
			await ctx.send(file=discord.File(f'images/pie_charts/{ctx.author.id}_pie_chart.png'))
			end = time.perf_counter()
			return await ctx.send(f'That took {end - start:.3f}sec to complete')
		except FileNotFoundError:
			await ctx.send(f'You dont have an account.')
			return await file_handling.account_creation(ctx)


def setup(bot):
	bot.add_cog(Images(bot))

