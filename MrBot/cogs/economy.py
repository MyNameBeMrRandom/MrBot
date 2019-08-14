from discord.ext import commands
import discord


class Economy(commands.Cog):
    """
    Economy management commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='balance', aliases=['bal'])
    async def balance(self, ctx):
        """
        Display the amount of money you have.
        """

        # Check if the user has an account.
        data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
        if not data:
            return await ctx.send("You don't have an account. Use `mb account create` to make one.")

        # Show the user how much money they have.
        embed = discord.Embed(
            colour=0x57FFF5,
            timestamp=ctx.message.created_at,
            title=f"{ctx.author.name}'s balance:"
        )
        embed.add_field(name='Bank:', value=f'**£{data["bank"]}**')
        embed.add_field(name='Cash:', value=f'**£{data["cash"]}**')
        embed.add_field(name='Total:', value=f'**£{data["bank"] + data["cash"]}**')
        embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
        return await ctx.send(embed=embed)

    @commands.command(name='deposit', aliases=['dep'])
    async def deposit(self, ctx, amount):
        """
        Desposit an amount of money to your bank.
        """

        # Check if the user has an account.
        data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
        if not data:
            return await ctx.send("You don't have an account. Use `mb account create` to make one.")
        # If the user wants to deposit all of their money.
        if amount == 'all':
            # If the user has no money in "cash" return.
            if data["cash"] == 0:
                return await ctx.send("You have no money to deposit.")
            # Add the cash money to bank money and then remove all cash money.
            await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", data["bank"] + data["cash"], ctx.author.id)
            await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", data["cash"] - data["cash"], ctx.author.id)
            return await ctx.send(f"Deposited **£{data['cash']}** to your bank.")
        # If the user want to deposit a specific amount of money. Check if amount is an int.
        try:
            amount = int(amount)
        except ValueError:
            return await ctx.send('That was not a valid amount of money, do not use commas or spaces. e.g `mb deposit 999999`')
        # If the amount is lower then or equal to 0.
        if amount <= 0:
            return await ctx.send("You can't deposit an amount lower then or equal to 0.")
        # If the amount is bigger then the amount of "cash" the user has.
        if amount > data["cash"]:
            return await ctx.send("You can't deposit an amount of money higher then the amount of cash you have.")
        # Add the amount to bank and remove amount from cash.
        await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", data["bank"] + amount, ctx.author.id)
        await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", data["cash"] - amount, ctx.author.id)
        return await ctx.send(f'Deposited **£{amount}** to your bank.')

    @commands.command(name='withdraw', aliases=['wd'])
    async def withdraw(self, ctx, amount):
        """
        Withdraw an amount of money from your bank.
        """

        # Check if the user has an account.
        data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
        if not data:
            return await ctx.send("You don't have an account. Use `mb account create` to make one.")
        # If the user wants to withdraw all of their money.
        if amount == 'all':
            # If the user has no money in "bank" return.
            if data["bank"] == 0:
                return await ctx.send("You have no money to withdraw.")
            # Add the bank amount to cash and remove bank amount from amount.
            await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", data["cash"] + data["bank"], ctx.author.id)
            await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", data["bank"] - data["bank"], ctx.author.id)
            return await ctx.send(f"Withdrew **£{data['bank']}** from your bank.")
        # If the user want to withdraw a specific amount of money. Check if amount is an int.
        try:
            amount = int(amount)
        except ValueError:
            return await ctx.send('That was not a valid amount of money, do not use commas or spaces. e.g `mb withdraw 999999`')
        # If the amount is lower then or equal to 0.
        if amount <= 0:
            return await ctx.send("You can't withdraw an amount lower then or equal to 0.")
        # If the amount is bigger then the amount of "bank" the user has.
        if amount > data["bank"]:
            return await ctx.send("You can't withdraw an amount of money higher then the amount of money you have in your bank.")
        # Add the amount to cash and remove amount from bank.
        await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", data["cash"] + amount, ctx.author.id)
        await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", data["bank"] - amount, ctx.author.id)
        return await ctx.send(f'Withdrew **£{amount}** from your bank.')


    @commands.command(name='claim')
    async def claim(self, ctx):

        if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", ctx.author.id):
            return await ctx.send("You don't have an account.")

        # Get users account.
        data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)

        # Check if the user voted, if they havent then return.
        vote = await self.bot.dblpy.get_user_vote(ctx.author.id)
        if vote is False:
            return await ctx.send('You have not voted, if you have only just voted please keep in mind that the vote can take a few minutes to register.')

        # Check if it is a weekend.
        is_weekend = await self.bot.dblpy.get_weekend_status()

        # If the user has not voted yet.
        if data['voted'] is False:
            return await ctx.send('You have not voted yet. Please vote here https://discordbots.org/bot/424637852035317770/vote')

        # If the user has already claimed their vote.
        if data['vote_claimed'] is True:
            return await ctx.send(f'You have already voted today. You can only vote once every 12 hours.')

        # Set vote_claimed to true.
        await self.bot.pool.execute(f"UPDATE user_config SET vote_claimed = $1 WHERE key = $2", True, ctx.author.id)

        # If its the weekend give user 500, else 250.
        if is_weekend is True:
            await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", data['bank'] + 500, ctx.author.id)
            return await ctx.send(f'Thank you for voting, because you voted on a weekend you were given `£500`!')
        await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", data['bank'] + 250, ctx.author.id)
        return await ctx.send(f'Thank you for voting, You were given `£250`!')

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        # Get the user.
        user = self.bot.get_user(int(data['user']))

        # If the user doesn't have an account, create one.
        if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", user.id):
            await self.bot.pool.execute(f"INSERT INTO user_config VALUES ($1, 'default', NULL, False, False, 0, 500, 500)", user.id)

        # Get the users account.
        data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", user.id)

        # Set 'voted' status to true.
        await self.bot.pool.execute(f"UPDATE user_config SET voted = $1 WHERE key = $2", True, user.id)

        # Increase vote count.
        await self.bot.pool.execute(f"UPDATE user_config SET vote_count = $1 WHERE key = $2", data['vote_count'] + 1, user.id)

    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        # Get the user.
        user = self.bot.get_user(int(data['user']))

        # If the user doesn't have an account, create one.
        if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", user.id):
            await self.bot.pool.execute(f"INSERT INTO user_config VALUES ($1, 'default', NULL, False, False, 0, 500, 500)", user.id)

        # Get the users account.
        data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", user.id)

        # Set 'voted' status to true.
        await self.bot.pool.execute(f"UPDATE user_config SET voted = $1 WHERE key = $2", True, user.id)

        # Set 'voted_claimed' to false
        await self.bot.pool.execute(f"UPDATE user_config SET vote_claimed = $1 WHERE key = $2", False, user.id)


        # Increase vote count.
        await self.bot.pool.execute(f"UPDATE user_config SET vote_count = $1 WHERE key = $2", data['vote_count'] + 1, user.id)


def setup(bot):
    bot.add_cog(Economy(bot))
