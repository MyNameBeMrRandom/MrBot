from discord.ext import commands
import asyncpg
import os


class Accounts(commands.Cog):
    """
    MrBot account management commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='account', aliases=['profile'], invoke_without_command=True)
    async def account(self, ctx):
        """
        Display information about your account.
        """

        if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", ctx.author.id):
            return await ctx.send('You dont have an account.')
        message = f">>> __**Information about {ctx.author.name}'s account.**__\n\n"
        data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
        message += f'**Configuration:**\n    **Background:** {data["background"]}\n\n'
        message += f'**Economy information:**\n    **Bank:** £{data["bank"]}\n    **Cash:** £{data["cash"]}\n\n'
        message += f'**General information:**\n    **Timezone:** {data["timezone"]}\n    **Last vote time:** {data["vote_time"]}\n    **Votes:** {data["vote_count"]}\n'
        return await ctx.send(message)

    @account.command(name='create')
    async def create_account(self, ctx):
        """
        Creates an account.
        """

        try:
            await self.bot.pool.execute(f"INSERT INTO user_config VALUES ($1, 'default', NULL, False, False, 0, 500, 500)", ctx.author.id)
            return await ctx.send(f'Account created with ID `{ctx.author.id}`')
        except asyncpg.UniqueViolationError:
            return await ctx.send('You already have an account.')

    @account.command(name='delete')
    async def delete_account(self, ctx):
        """
        Deletes your account.
        """

        if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", ctx.author.id):
            return await ctx.send('You dont have an account.')
        await self.bot.pool.execute(f"DELETE FROM user_config WHERE key = $1", ctx.author.id)
        return await ctx.send('Deleted your account.')

    @commands.command(name="background", aliases=['bg'])
    async def background(self, ctx):
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


def setup(bot):
    bot.add_cog(Accounts(bot))
