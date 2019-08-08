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

        if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", ctx.author.id):
            return await ctx.send('You dont have an account.')
        data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
        bank = data["bank"]
        cash = data["cash"]
        embed = discord.Embed(
            colour=0x57FFF5,
            timestamp=ctx.message.created_at,
            title=f"{ctx.author.name}'s balance:"
        )
        embed.add_field(name='Bank:', value=f'**£{bank}**')
        embed.add_field(name='Cash:', value=f'**£{cash}**')
        embed.add_field(name='Total:', value=f'**£{cash + bank}**')
        embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
        return await ctx.send(embed=embed)

    @commands.command(name='deposit', aliases=['dep'])
    async def deposit(self, ctx, amount):
        """
        Desposit an amount of money to your bank.
        """

        if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", ctx.author.id):
            return await ctx.send('You dont have an account.')
        data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
        bank_amount = data["bank"]
        cash_amount = data["cash"]
        if amount == 'all':
            if cash_amount == 0:
                embed = discord.Embed(
                    colour=0x57FFF5,
                    timestamp=ctx.message.created_at,
                    description=f'You have no money to deposit.'
                )
                embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
                return await ctx.send(embed=embed)
            await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", bank_amount + cash_amount, ctx.author.id)
            await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", cash_amount - cash_amount, ctx.author.id)
            embed = discord.Embed(
                colour=0x57FFF5,
                timestamp=ctx.message.created_at,
                description=f'Deposited **£{cash_amount}** to your bank.'
            )
            embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
            return await ctx.send(embed=embed)
        else:
            try:
                amount = int(amount)
                if amount > cash_amount or amount <= 0:
                    embed = discord.Embed(
                        colour=0x57FFF5,
                        timestamp=ctx.message.created_at,
                        description=f'You cant deposit that amount of money, you either dont have enough money or tried to deposit an amount less then or equal to 0'
                    )
                    embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
                    return await ctx.send(embed=embed)
                await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", bank_amount + amount, ctx.author.id)
                await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", cash_amount - amount, ctx.author.id)
                embed = discord.Embed(
                    colour=0x57FFF5,
                    timestamp=ctx.message.created_at,
                    description=f'Deposited **£{amount}** to your bank.'
                )
                embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
                return await ctx.send(embed=embed)
            except ValueError:
                return await ctx.send('That was not a valid amount of money, do not use commas or spaces. e.g `mb deposit 999999`')

    @commands.command(name='withdraw', aliases=['wd'])
    async def withdraw(self, ctx, amount):
        """
        Withdraw an amount of money from your bank.
        """

        if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", ctx.author.id):
            return await ctx.send('You dont have an account.')
        data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
        bank_amount = data["bank"]
        cash_amount = data["cash"]
        if amount == 'all':
            if bank_amount == 0:
                embed = discord.Embed(
                    colour=0x57FFF5,
                    timestamp=ctx.message.created_at,
                    description=f'You have no money to withdraw.'
                )
                embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
                return await ctx.send(embed=embed)
            await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", cash_amount + bank_amount, ctx.author.id)
            await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", bank_amount - bank_amount, ctx.author.id)
            embed = discord.Embed(
                colour=0x57FFF5,
                timestamp=ctx.message.created_at,
                description=f'Withdrew **£{bank_amount}** from your bank.'
            )
            embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
            return await ctx.send(embed=embed)
        elif not amount == 'all':
            try:
                amount = int(amount)
                if amount > bank_amount or amount <= 0:
                    embed = discord.Embed(
                        colour=0x57FFF5,
                        timestamp=ctx.message.created_at,
                        description=f'You cant withdraw that amount of money, you either dont have enough money or tried to withdraw an amount less then or equal to 0'
                    )
                    embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
                    return await ctx.send(embed=embed)
                await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", cash_amount + amount, ctx.author.id)
                await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", bank_amount - amount, ctx.author.id)
                embed = discord.Embed(
                    colour=0x57FFF5,
                    timestamp=ctx.message.created_at,
                    description=f'Withdrew **£{amount}** from your bank.'
                )
                embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
                return await ctx.send(embed=embed)
            except ValueError:
                return await ctx.send('That was not a valid amount of money, do not use commas or spaces. e.g `mb deposit 999999`')

    @commands.command(name='claim')
    async def claim(self, ctx):

        if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", ctx.author.id):
            return await ctx.send('You dont have an account.')

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
