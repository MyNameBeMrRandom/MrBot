from discord.ext import commands
import discord
import asyncio
import config
import time
import dbl


class BgTasks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.update_presence = self.bot.loop.create_task(self.activity_changing())
        self.dblpy = dbl.Client(self.bot, config.DBL_TOKEN, webhook_path='/dblwebhook', webhook_auth=f'{config.DBL_TOKEN}', webhook_port=5000)
        self.update_count = self.bot.loop.create_task(self.update_guild_count())

    async def activity_changing(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f'{len(self.bot.guilds)} Guilds', ))
            await asyncio.sleep(60)
            await self.bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.watching, name=f'{len(self.bot.users)} Users'))
            await asyncio.sleep(60)
            await self.bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.playing, name=f"Do 'mb help'!"))
            await asyncio.sleep(60)

    async def update_guild_count(self):
        while not self.bot.is_closed():
            try:
                await self.dblpy.post_guild_count()
            except discord.Forbidden:
                return
            await asyncio.sleep(21600)

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        user = self.bot.get_user(int(data['user']))
        if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", user.id):
            return
        user_data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", user.id)
        cash_amount = user_data["cash"]
        vote_count = user_data["vote_count"]
        await self.bot.pool.execute(f"UPDATE user_config SET vote_count = $1 WHERE key = $2", vote_count + 1, user.id)
        await self.bot.pool.execute(f"UPDATE user_config SET vote_time = $1 WHERE key = $2", time.time(), user.id)
        if data['isWeekend'] is True:
            try:
                await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", cash_amount + 500, user.id)
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f'Thank you for voting, You gained **£500** because you voted on a weekend and earned double rewards!'
                )
                return await user.send(embed=embed)
            except Exception:
                return
        else:
            try:
                await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", cash_amount + 250, user.id)
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f'Thank you for voting, You gained **£250**.!'
                )
                return await user.send(embed=embed)
            except Exception:
                return

    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        user = self.bot.get_user(int(data['user']))
        if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", user.id):
            return
        user_data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", user.id)
        cash_amount = user_data["cash"]
        vote_count = user_data["vote_count"]
        await self.bot.pool.execute(f"UPDATE user_config SET vote_count = $1 WHERE key = $2", vote_count + 1, user.id)
        await self.bot.pool.execute(f"UPDATE user_config SET vote_time = $1 WHERE key = $2", time.time(), user.id)
        if data['isWeekend'] is True:
            try:
                await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", cash_amount + 500, user.id)
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f'Thank you for voting, You gained **£500** because you voted on a weekend and earned double rewards!'
                )
                return await user.send(embed=embed)
            except Exception:
                return
        else:
            try:
                await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", cash_amount + 250, user.id)
                embed = discord.Embed(
                    colour=0x57FFF5,
                    description=f'Thank you for voting, You gained **£250**.!'
                )
                return await user.send(embed=embed)
            except Exception:
                return


def setup(bot):
    bot.add_cog(BgTasks(bot))