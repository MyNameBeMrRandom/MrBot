from discord.ext import commands
import asyncpg
import discord
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
        Get information about your account.
        """

        # Check if the user has an account.
        data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
        if not data:
            return await ctx.send("You don't have an account. Use `mb account create` to make one.")

        # Send information.
        message = f">>> __**Information about {ctx.author.name}'s account.**__\n\n" \
                  f"**Configuration:**\n    **Background:** {data['background']}\n\n" \
                  f"**Economy information:**\n    **Bank:** £{data['bank']}\n    **Cash:** £{data['cash']}\n\n" \
                  f"**General information:**\n    **Timezone:** {data['timezone']}\n    **Votes:** {data['vote_count']}\n"
        return await ctx.send(message)

    @account.command(name='create')
    async def create_account(self, ctx):
        """
        Create an account.
        """

        # Try to create an account with unique id and if they already one it will raise error.
        try:
            await self.bot.pool.execute(f"INSERT INTO user_config VALUES ($1, 'bg_default', NULL, False, False, 0, 1000, 1000)", ctx.author.id)
            return await ctx.send(f'Account created with ID `{ctx.author.id}`')
        except asyncpg.UniqueViolationError:
            return await ctx.send('You already have an account.')

    @account.command(name='delete')
    async def delete_account(self, ctx):
        """
        Delete your account.
        """

        # Check if the user has an account.
        data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
        if not data:
            return await ctx.send("You don't have an account. Use `mb account create` to make one.")
        # Delete account.
        await self.bot.pool.execute(f"DELETE FROM user_config WHERE key = $1", ctx.author.id)
        return await ctx.send('Deleted your account.')

    @commands.command(name="background", aliases=['bg'])
    async def background(self, ctx):
        """
        Get your current background.
        """

        # Check if the user has an account.
        data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
        if not data:
            return await ctx.send("You don't have an account. Use `mb account create` to make one.")
        # Get current background and upload picture of it.
        return await ctx.send(content=f"Your current background is `{data['background']}`.", file=discord.File(filename=f'{data["background"]}.png', fp=f'images/resources/backgrounds/{data["background"]}.png'))

    @commands.command(name="bg_change", aliases=["bgc"])
    async def bg_change(self, ctx, new_background: str):
        """
        Change your background to the one specified.
        """

        # Check if the user has an account.
        data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
        if not data:
            return await ctx.send("You don't have an account. Use `mb account create` to make one.")
        # Check is the new background is valid.
        if not os.path.isfile(f"images/resources/backgrounds/{new_background}.png"):
            return await ctx.send(f"`{new_background}` is not a recongnised background.")
        # Update background and notify user.
        await self.bot.pool.execute("UPDATE user_config SET background = $1 WHERE key = $2", new_background, ctx.author.id)
        return await ctx.send(f"Changed your background from `{data['background']}` to `{new_background}`.")


def setup(bot):
    bot.add_cog(Accounts(bot))
