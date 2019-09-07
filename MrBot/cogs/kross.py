from discord.ext import commands
from .utils import exceptions
import discord


class KrossServer(commands.Cog):
    """
    Custom server commands.
    """

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        # Check if the guild we are in is a certain guild.
        if ctx.guild.id == 491312179476299786:
            return True
        raise exceptions.WrongGuild

    @commands.Cog.listener()
    async def on_member_join(self, member):

        # Check if we are in a certain guild.
        guild = member.guild
        if not guild.id == 491312179476299786:
            return
        # If the member is not a bot.
        if member.bot is True:
            return
        # Get the roles and the amount of people in each role.
        kodama = discord.utils.get(guild.roles, name="Kodama")
        sylph = discord.utils.get(guild.roles, name="Sylph")
        leviathan = discord.utils.get(guild.roles, name="Leviathan")
        phoenix = discord.utils.get(guild.roles, name="Phoenix")
        kodama_count = len(kodama.members)
        sylph_count = len(sylph.members)
        leviathan_count = len(leviathan.members)
        phoenix_count = len(phoenix.members)
        # Try to add the member that joined to the house with the lowest amount of people in it.
        try:
            if kodama_count <= phoenix_count and kodama_count <= leviathan_count and kodama_count <= sylph_count:
                return await member.add_roles(kodama)
            elif phoenix_count <= kodama_count and phoenix_count <= leviathan_count and phoenix_count <= sylph_count:
                return await member.add_roles(phoenix)
            elif leviathan_count <= phoenix_count and leviathan_count <= kodama_count and leviathan_count <= sylph_count:
                return await member.add_roles(leviathan)
            elif sylph_count <= phoenix_count and sylph_count <= leviathan_count and sylph_count <= kodama_count:
                return await member.add_roles(sylph)
            else:
                await member.add_roles(phoenix)
        except discord.Forbidden:
            return

    @commands.command(name="houses", aliases=["h"], hidden=True)
    async def houses(self, ctx):
        """
        Get how many members are in each house.

        This only works in a specific server.
        """

        # Define counts and get roles.
        bots_count = 0
        heathen_count = 0
        phoenix_count = 0
        leviathan_count = 0
        kodama_count = 0
        sylph_count = 0
        banshee_count = 0
        lost_souls_count = 0
        heathen = discord.utils.get(ctx.guild.roles, name="Heathen")
        phoenix = discord.utils.get(ctx.guild.roles, name="Phoenix")
        leviathan = discord.utils.get(ctx.guild.roles, name="Leviathan")
        kodama = discord.utils.get(ctx.guild.roles, name="Kodama")
        sylph = discord.utils.get(ctx.guild.roles, name="Sylph")
        banshee = discord.utils.get(ctx.guild.roles, name="Banshee")
        lost_souls = discord.utils.get(ctx.guild.roles, name="The Lost Souls")

        # Loop through all members of the guild, checking their roles/bot status.
        for member in ctx.guild.members:
            if member.bot:
                bots_count += 1
                continue
            if heathen in member.roles:
                heathen_count += 1
            if phoenix in member.roles:
                phoenix_count += 1
                continue
            if leviathan in member.roles:
                leviathan_count += 1
                continue
            if kodama in member.roles:
                kodama_count += 1
                continue
            if sylph in member.roles:
                sylph_count += 1
                continue
            if banshee in member.roles:
                banshee_count += 1
                continue
            if lost_souls in member.roles:
                lost_souls_count += 1
                continue
        # Get the total amount of members
        total = phoenix_count + leviathan_count + kodama_count + sylph_count + banshee_count + lost_souls_count + bots_count
        # Create and send the message.
        message = f"```py\n" \
                  f"Heathens: {' ' * int((11 - 9))} {heathen_count}\n" \
                  f"Phoenix: {' ' * int((11 - 8))} {phoenix_count}\n" \
                  f"Leviathan: {' ' * int((11 - 10))} {leviathan_count}\n" \
                  f"Kodama: {' ' * int((11 - 7))} {kodama_count}\n" \
                  f"Sylph: {' ' * int((11 - 6))} {sylph_count}\n" \
                  f"Banshees: {' ' * int((11 - 9))} {banshee_count}\n" \
                  f"Lost Souls: {' ' * int((11 - 11))} {lost_souls_count}\n" \
                  f"Bots: {' ' * int((11 - 5))} {bots_count}\n" \
                  f"Total: {' ' * int((11 - 6))} {total}\n" \
                  f"```"
        return await ctx.send(message)

    @commands.command(name="points", aliases=["p"], hidden=True)
    @commands.has_role(548604302768209920)
    async def points(self, ctx, house: str, operation: str, points: int):
        """
        Add/remove points to/from a house.

        This only works in a specific server.
        `house`: What house to add/remove points to/from. Can be `phoenix`, `leviathan`, `kodama` or `sylph`.
        `operation`: Wheter to add or remove points. Can be `add` or `minus`.
        `points`: The amount of points to add/remove. Can be any number.
        """

        if house == "kodama":
            data = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "kodama")
            if operation == "add":
                await self.bot.db.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", data["points"] + points, "kodama")
                await ctx.send(f"Added `{points}` points to house Kodama. They now have `{data['points'] + points}` points!")
                return await self.refresh_points(ctx)
            elif operation == "minus":
                await self.bot.db.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", data["points"] - points, "kodama")
                await ctx.send(f"Removed `{points}` points from house Kodama. They now have `{data['points'] - points}` points!")
                return await self.refresh_points(ctx)
            else:
                return await ctx.send("That operation was not recognised.")
        elif house == "phoenix":
            data = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "phoenix")
            if operation == "add":
                await self.bot.db.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", data["points"] + points, "phoenix")
                await ctx.send(f"Added `{points}` points to house Phoenix. They now have `{data['points'] + points}` points!")
                return await self.refresh_points(ctx)
            elif operation == "minus":
                await self.bot.db.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", data["points"] - points, "phoenix")
                await ctx.send(f"Removed `{points}` points from house Phoenix. They now have `{data['points'] - points}` points!")
                return await self.refresh_points(ctx)
            else:
                return await ctx.send("That operation was not recognised.")
        elif house == "leviatham":
            data = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "leviathan")
            if operation == "add":
                await self.bot.db.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", data["points"] + points, "leviathan")
                await ctx.send(f"Added `{points}` points to house Leviathan. They now have `{data['points'] + points}` points!")
                return await self.refresh_points(ctx)
            elif operation == "minus":
                await self.bot.db.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", data["points"] - points, "leviathan")
                await ctx.send(f"Removed `{points}` points from house Leviathan. They now have `{data['points'] - points}` points!")
                return await self.refresh_points(ctx)
            else:
                return await ctx.send("That operation was not recognised.")
        elif house == "sylph":
            data = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "sylph")
            if operation == "add":
                await self.bot.db.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", data["points"] + points, "sylph")
                await ctx.send(f"Added `{points}` points to house Sylph. They now have `{data['points'] + points}` points!")
                return await self.refresh_points(ctx)
            elif operation == "minus":
                await self.bot.db.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", data["points"] - points, "sylph")
                await ctx.send(f"Removed `{points}` points from house Sylph. They now have `{data['points'] - points}` points!")
                return await self.refresh_points(ctx)
            else:
                return await ctx.send("That operation was not recognised.")
        else:
            return await ctx.send("That house wasn't recognised.")

    async def refresh_points(self, ctx):
        channel = self.bot.get_channel(547156691985104896)
        try:
            kodama = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "kodama")
            phoenix = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "phoenix")
            leviathan = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "leviathan")
            sylph = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "sylph")
            km = await channel.fetch_message(548311930054639637)
            await km.edit(content=f"Kodama has {kodama['points']} points!")
            pm = await channel.fetch_message(548311654568427533)
            await pm.edit(content=f"Phoenix has {phoenix['points']} points!")
            lm = await channel.fetch_message(548311845434294282)
            await lm.edit(content=f"Leviathan has {leviathan['points']} points!")
            sm = await channel.fetch_message(548311533424476170)
            await sm.edit(content=f"Sylph has {sylph['points']} points!")
            await ctx.send(f"Refreshed the points leaderboard in {channel.mention}")
        except discord.Forbidden:
            return


def setup(bot):
    bot.add_cog(KrossServer(bot))
