from discord.ext import commands
import itertools
import discord
import random
import typing
import time


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

        `amount`: The amount to deposit. Can be `all` or a number.
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

        `amount`: The amount to withdraw. Can be `all` or a number.
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

    @commands.command(name='transfer')
    async def transfer(self, ctx, amount, member: typing.Optional[discord.Member] = None):
        """
        Transfer money from your bank to another user.

        `amount`: The amount to transfer. Can be `all` or a number.
        `member`: The user to tranfer money too. This can be a mention, id, nickname or name.
        """

        # If the user doesnt specify a target
        if not member:
            return await ctx.send('You need to specify a target.')
        # If the user targets themself.
        if ctx.author.id == member.id:
            return await ctx.send("You can't transfer money to yourself.")
        # Check if the user has an account.
        author = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
        if not author:
            return await ctx.send("You don't have an account. Use `mb account create` to make one.")
        # Check if the target has an account.
        target = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", member.id)
        if not target:
            return await ctx.send("The target does not have an account. They can use `mb account create` to make one.")
        # If the user wants to transfer all of their money.
        if amount == 'all':
            # Check if the author has any money in their bank.
            if author["bank"] == 0:
                return await ctx.send("You have no money in your bank to send.")
            # Transfer money.
            await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", target["bank"] + author["bank"], member.id)
            await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", author["bank"] - author["bank"], ctx.author.id)
            return await ctx.send(f'You transferred **£{author["bank"]}** to {member.mention}.')
        # If the user want to transfer a specific amount of money. Check if amount is an int.
        try:
            amount = int(amount)
        except ValueError:
            return await ctx.send('That was not a valid amount of money, do not use commas or spaces. e.g `mb withdraw 999999`')
        # If the amount is lower then or equal to 0.
        if amount <= 0:
            return await ctx.send("You can't transfer an amount lower then or equal to 0.")
        # If the amount is bigger then the amount of money in the "bank" the user has.
        if amount > author["bank"]:
            return await ctx.send("You can't transfer an amount of money higher then the amount of money you have in your bank.")
        # Transfer money.
        await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", target["bank"] + amount, member.id)
        await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", author["bank"] - amount, ctx.author.id)
        return await ctx.send(f'You transferred **£{amount}** to {member.mention}.')

    @commands.command(name='leaderboard', aliases=['lb'])
    async def leaderboard(self, ctx, lb_type: typing.Optional[str] = 'guild'):
        """
        Get the leaderboard for the current guild.

        `lb_type`: Can be `global` for a global leaderboard or `guild` for a guild specific leaderboard.
        """

        # Get data
        data = await self.bot.pool.fetch("SELECT * FROM user_config ORDER BY bank + cash DESC")
        # If there are no accounts.
        if not data:
            return await ctx.send('There are no accounts.')
        # Create an embed.
        embed = discord.Embed(
            colour=0x57FFF5,
            timestamp=ctx.message.created_at,
            description=""
        )
        # If the user wants the leaderboard for the current guild.
        if lb_type == 'guild':
            # Get all accounts which belong to people in the current guild.
            guild_accounts = [account for account in data if account["key"] in [member.id for member in ctx.guild.members]]
            # If there are no user with account in this guild.
            if not guild_accounts:
                return await ctx.send('There are no users with accounts in this guild.')
            # Get the first 5 from the list of accounts.
            first_5 = list(itertools.islice(guild_accounts, 0, 5))
            # Add text to embed.
            embed.description += f"__**{ctx.guild.name}'s Leaderboard:**__\nShowing the top 5 accounts in terms of total balance.\n\n"
            # Add text for each account.
            counter = 1
            for account in first_5:
                user = self.bot.get_user(account["key"])
                embed.description += f"**{counter}.** {user}\nTotal money: **£{account['bank'] + account['cash']}**\n\n"
                counter += 1
        # If the user wants the global leaderboard.
        elif lb_type == 'global' or lb_type == 'g':
            # Get the first 5 from the list of accounts.
            first_5 = list(itertools.islice(data, 0, 5))
            # Add text to embed.
            embed.description += f"__**MrBot's Global Leaderboard:**__\nShowing the top 5 accounts in terms of total balance.\n\n"
            # Add text for each account.
            counter = 1
            for account in first_5:
                user = self.bot.get_user(account["key"])
                embed.description += f"**{counter}.** {user}\nTotal money: **£{account['bank'] + account['cash']}**\n\n"
                counter += 1
        # If a valid option is not picked.
        else:
            return await ctx.send('That was not a valid leaderboard option. Choose either `global` or `guild`')
        # If the user has an account, display thier position.
        if ctx.author.id in [account["key"] for account in data]:
            embed.set_footer(text=f"Your rank: {[account['key'] for account in data].index(ctx.author.id)+1}")
        # Send embed.
        return await ctx.send(embed=embed)

    @commands.cooldown(1, 3600, commands.BucketType.user)
    @commands.command(name='steal', aliases=['rob'])
    async def steal(self, ctx, member: typing.Optional[discord.Member] = None):
        """
        Steal money from another user.

        `member`: The user to tranfer money too. This can be a mention, id, nickname or name.
        """

        # If the user doesnt specify a target
        if not member:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send('You need to specify a target.')
        # If the user targets themself.
        if ctx.author.id == member.id:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("You can't steal from yourself.")
        # Check if the user has an account.
        author = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
        if not author:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("You don't have an account. Use `mb account create` to make one.")
        # Check if the target has an account.
        target = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", member.id)
        if not target:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("The target does not have an account. They can use `mb account create` to make one.")
        # Check if the target has any money in cash.
        if target["cash"] == 0:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("The target has no money to steal.")
        # Select a random chance.
        chance = random.randint(1, 100)
        # If the chance is 70 or higher the user will succeed in stealing, gaining half of the targets cash
        if chance >= 70:
            to_steal = random.randint(1, target["cash"])
            await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", author["cash"] + to_steal, ctx.author.id)
            await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", target["cash"] - to_steal, member.id)
            return await ctx.send(f'You stole **£{to_steal}** from {member.mention}')
        # If the chance is lower then 70, the user failes to steal the money and is fined
        fine = random.randint(100, 500)
        await self.bot.pool.execute(f"UPDATE user_config SET cash = $1 WHERE key = $2", author["cash"] - fine, ctx.author.id)
        return await ctx.send(f'You failed to steal from {member.mention} and was fined **£{fine}**.')

    @commands.command(name='claim')
    async def claim(self, ctx):
        """
        Claim money if you have voted.
        """

        # Check if the user has an account.
        data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
        if not data:
            return await ctx.send("You don't have an account. Use `mb account create` to make one.")

        # Check if it is a weekend.
        is_weekend = await self.bot.dblpy.get_weekend_status()

        # If the user has already claimed.
        if data["vote_claimed"] is True:
            return await ctx.send('You have already claimed your vote. You can claim again after voting which you can do every 12 hours.')

        # If the user has not voted.
        if data["voted"] is False:
            return await ctx.send('You have not voted yet. Please vote here https://discordbots.org/bot/424637852035317770/vote')

        # Set "vote_claimed" to true and "voted" to false (for consistancy).
        await self.bot.pool.execute(f"UPDATE user_config SET vote_claimed = $1 WHERE key = $2", True, ctx.author.id)
        await self.bot.pool.execute(f"UPDATE user_config SET voted = $1 WHERE key = $2", False, ctx.author.id)

        # If its the weekend give user 200, else 100.
        if is_weekend is True:
            await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", data['bank'] + 200, ctx.author.id)
            return await ctx.send(f'Thank you for voting, because you voted on a weekend you were given `£200`!')
        await self.bot.pool.execute(f"UPDATE user_config SET bank = $1 WHERE key = $2", data['bank'] + 100, ctx.author.id)
        return await ctx.send(f'Thank you for voting, You were given `£100`!')

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        # Get the user.
        user = self.bot.get_user(int(data['user']))

        # If the user doesn't have an account, create one.
        if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", user.id):
            await self.bot.pool.execute(f"INSERT INTO user_config VALUES ($1, 'default', NULL, False, False, 0, 1000, 1000)", user.id)
        data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", user.id)

        # Set "voted" to True.
        await self.bot.pool.execute(f"UPDATE user_config SET voted = $1 WHERE key = $2", True, user.id)

        # Set "vote_claimed" to False.
        await self.bot.pool.execute(f"UPDATE user_config SET vote_claimed = $1 WHERE key = $2", False, user.id)

        # Increase vote count.
        await self.bot.pool.execute(f"UPDATE user_config SET vote_count = $1 WHERE key = $2", data['vote_count'] + 1, user.id)

    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        # Get the user.
        user = self.bot.get_user(int(data['user']))

        # If the user doesn't have an account, create one.
        if not await self.bot.pool.fetchrow("SELECT key FROM user_config WHERE key = $1", user.id):
            await self.bot.pool.execute(f"INSERT INTO user_config VALUES ($1, 'default', NULL, False, False, 0, 1000, 1000)", user.id)
        data = await self.bot.pool.fetchrow("SELECT * FROM user_config WHERE key = $1", user.id)

        # Set "voted" to True.
        await self.bot.pool.execute(f"UPDATE user_config SET voted = $1 WHERE key = $2", True, user.id)

        # Set "vote_claimed" to False.
        await self.bot.pool.execute(f"UPDATE user_config SET vote_claimed = $1 WHERE key = $2", False, user.id)

        # Increase vote count.
        await self.bot.pool.execute(f"UPDATE user_config SET vote_count = $1 WHERE key = $2", data['vote_count'] + 1, user.id)

def setup(bot):
    bot.add_cog(Economy(bot))
