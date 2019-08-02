from discord.ext import commands
from PIL import ImageDraw
from PIL import ImageFont
from io import BytesIO
from PIL import Image
import discord
import aiohttp
import time
import os


class Images(commands.Cog):
	"""
	Image manipulation/generation commands.
	"""

	def __init__(self, bot):
		self.bot = bot
		self.session = aiohttp.ClientSession(loop=bot.loop)

	async def get_image(self, url):
		async with self.session.get(url) as response:
			image_bytes = await response.read()
		return image_bytes

	def round_corners(self, image, rad):
		circle = Image.new("L", (rad * 2, rad * 2))
		draw = ImageDraw.Draw(circle)
		draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
		alpha = Image.new("L", image.size, 255)
		w, h = image.size
		alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
		alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
		alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
		alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
		image.putalpha(alpha)
		return image

	@commands.command(name="bg")
	async def bg(self, ctx):
		"""
		Tells you what background you currently have set.
		"""

		if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", ctx.author.id):
			return await ctx.send("You do not have an account.")
		data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
		return await ctx.send(f"Your current background is `{data['background']}`.")

	@commands.command(name="bg_change", aliases=["bgc"])
	async def bg_change(self, ctx, new_background: str):
		"""
		Changes your "imginfo" background to the one specified.
		"""

		if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", ctx.author.id):
			return await ctx.send("You do not have an account.")
		data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
		if not os.path.isfile(f"images/resources/backgrounds/{new_background}.png"):
			return await ctx.send(f"`{new_background}` is not a recongnised background.")
		await ctx.send(f"Changed your background from `{data['background']}` to `{new_background}`.")
		return await self.bot.pool.execute("UPDATE user_config SET background = $1 WHERE key = $2", new_background, ctx.author.id)

	@commands.command(name="bg_list", aliases=["bgl"])
	async def bg_list(self, ctx):
		"""
		Display a list of possible backgrounds you can have.
		"""

		# Start typing and timer
		start = time.perf_counter()
		await ctx.trigger_typing()

		# Generate image.
		image = await self.bot.loop.run_in_executor(None, self.do_bg_list)

		# Send image
		await ctx.send(file=discord.File(filename=f"bg_list.png", fp=image))

		# End timer and log how long operation took
		end = time.perf_counter()
		return await ctx.send(f"That took {end - start:.3f}sec to complete")

	def do_bg_list(self):

		# Define the fonts.
		font = ImageFont.truetype("images/resources/fonts/OpenSans-Regular.ttf", 120)

		# Open all the images.
		bg0 = Image.open("images/resources/backgrounds/bg_default.png")
		bg1 = Image.open("images/resources/backgrounds/bg_1.png")
		bg2 = Image.open("images/resources/backgrounds/bg_2.png")
		bg3 = Image.open("images/resources/backgrounds/bg_3.png")
		bg4 = Image.open("images/resources/backgrounds/bg_4.png")
		bg5 = Image.open("images/resources/backgrounds/bg_5.png")
		bg6 = Image.open("images/resources/backgrounds/bg_6.png")
		bg7 = Image.open("images/resources/backgrounds/bg_7.png")
		bg8 = Image.open("images/resources/backgrounds/bg_8.png")
		bg9 = Image.open("images/resources/backgrounds/bg_9.png")
		bg10 = Image.open("images/resources/backgrounds/bg_10.png")
		bg11 = Image.open("images/resources/backgrounds/bg_11.png")

		# Make a new image and paste images into it.
		example = Image.new("RGB", (4000, 3600))
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
		example_draw.text((10, 15), f"bg_default", (255, 255, 255),  align="center", font=font)
		example_draw.text((1010, 15), f"bg_1", (255, 255, 255),  align="center", font=font)
		example_draw.text((2010, 15), f"bg_2", (255, 255, 255), align="center", font=font)
		example_draw.text((3010, 15), f"bg_3", (255, 255, 255), align="center", font=font)
		example_draw.text((10, 1215), f"bg_4", (255, 255, 255), align="center", font=font)
		example_draw.text((1010, 1215), f"bg_5", (255, 255, 255), align="center", font=font)
		example_draw.text((2010, 1215), f"bg_6", (255, 255, 255), align="center", font=font)
		example_draw.text((3010, 1215), f"bg_7", (255, 255, 255), align="center", font=font)
		example_draw.text((10, 2415), f"bg_8", (255, 255, 255), align="center", font=font)
		example_draw.text((1010, 2415), f"bg_9", (255, 255, 255), align="center", font=font)
		example_draw.text((2010, 2415), f"bg_10", (255, 255, 255), align="center", font=font)
		example_draw.text((3010, 2415), f"bg_11", (255, 255, 255), align="center", font=font)

		# Resize image and save it.
		example = example.resize([1000,900])

		# prepare the stream to save this image into
		final_buffer = BytesIO()
		example.save(final_buffer, "png")

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

		# Return images
		final_buffer.seek(0)
		return final_buffer

	@commands.command(name="imginfo")
	async def imginfo(self, ctx, *, member: discord.Member = None):
		"""
		Generate an image with information abount you and your account.
		"""

		if not member:
			member = ctx.author

		# Check if the user has a account
		if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", member.id):
			return await ctx.send("User does not have an account.")

		# Get the members info.
		data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", member.id)

		# Start typing and timer
		start = time.perf_counter()
		await ctx.trigger_typing()

		# Get the users avatars as bytes
		avatar_url = str(member.avatar_url_as(format="png", size=1024))
		avatar_bytes = await self.get_image(avatar_url)

		# Generate image.
		image = await self.bot.loop.run_in_executor(None, self.do_imageinfo, data , member, avatar_bytes)

		# Send image
		await ctx.send(file=discord.File(filename=f"{member.id}_imginfo.png", fp=image))

		# End timer and log how long operation took.
		end = time.perf_counter()
		return await ctx.send(f"That took {end - start:.3f}sec to complete")

	def do_imageinfo(self, data, member, avatar_bytes):

		# Define the fonts.
		smallfont = ImageFont.truetype("images/resources/fonts/OpenSans-Regular.ttf", 30)
		font = ImageFont.truetype("images/resources/fonts/OpenSans-Regular.ttf", 40)
		bigfont = ImageFont.truetype("images/resources/fonts/OpenSans-Regular.ttf", 50)

		# Get the members backround based on their choice.
		background = data["background"]
		if background == "bg_1":
			background_img = Image.open("images/resources/backgrounds/bg_1.png")
		elif background == "bg_2":
			background_img = Image.open("images/resources/backgrounds/bg_2.png")
		elif background == "bg_3":
			background_img = Image.open("images/resources/backgrounds/bg_3.png")
		elif background == "bg_4":
			background_img = Image.open("images/resources/backgrounds/bg_4.png")
		elif background == "bg_5":
			background_img = Image.open("images/resources/backgrounds/bg_5.png")
		elif background == "bg_6":
			background_img = Image.open("images/resources/backgrounds/bg_6.png")
		elif background == "bg_7":
			background_img = Image.open("images/resources/backgrounds/bg_7.png")
		elif background == "bg_8":
			background_img = Image.open("images/resources/backgrounds/bg_8.png")
		elif background == "bg_9":
			background_img = Image.open("images/resources/backgrounds/bg_9.png")
		elif background == "bg_10":
			background_img = Image.open("images/resources/backgrounds/bg_10.png")
		elif background == "bg_11":
			background_img = Image.open("images/resources/backgrounds/bg_11.png")
		else:
			background_img = Image.open("images/resources/backgrounds/bg_default.png")

		# Open the members avatar, resize, and then round it.
		avatar_img = Image.open(BytesIO(avatar_bytes))
		avatar_img = avatar_img.resize([250, 250])
		avatar_img = self.round_corners(avatar_img, 50)

		# Copy rounded avatar image to background image.
		avatar_img = avatar_img.copy()
		background_img.paste(avatar_img, (700, 50), avatar_img)

		# Allow for drawing on the background image.
		background_draw = ImageDraw.Draw(background_img)

		# Add text to background image.
		background_draw.text((50, 35), f"{member}", (255, 255, 255),  align="center", font=bigfont)
		if member.nick is not None:
			background_draw.text((50, 90), f"{member.nick}", (255, 255, 255), align="center", font=font)

		# Add status circles to the backround image based on the users status.
		if member.status == discord.Status.online:
			background_draw.ellipse((915, 265, 965, 315), fill=(0 ,128 ,0 , 0))
		if member.status == discord.Status.idle:
			background_draw.ellipse((915, 265, 965, 315), fill=(255 ,165 ,0 , 0))
		if member.status == discord.Status.dnd:
			background_draw.ellipse((915, 265, 965, 315), fill=(255 ,0 ,0 , 0))
		if member.status == discord.Status.offline:
			background_draw.ellipse((915, 265, 965, 315), fill=(128 ,128 ,128 , 0))

		# Round the backround image and resize it.
		background_img = self.round_corners(background_img, 100)

		# prepare the stream to save this image into
		final_buffer = BytesIO()
		background_img.save(final_buffer, "png")

		# Close images.
		background_img.close()
		avatar_img.close()

		# Return images
		final_buffer.seek(0)
		return final_buffer


def setup(bot):
	bot.add_cog(Images(bot))

