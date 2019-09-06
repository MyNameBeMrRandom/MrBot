import asyncio
import discord


class ListPaginator:

    def __init__(self, **kwargs):
        self.ctx = kwargs.get("ctx")
        self.title = kwargs.get("title")
        self.org_entries = kwargs.get("org_entries")
        self.entries = kwargs.get("entries")
        self.entries_per_page = kwargs.get("entries_per_page")
        self.pages = kwargs.get("pages")
        self.page = 0
        self.message = None
        self.looping = True
        self.emotes = {
            "\u2b05": self.page_backward,
            "\u27a1": self.page_forward,
            "\u23f9": self.stop
        }

        # If the title is not set.
        if self.title is None:
            self.title = f"There are `{len(self.org_entries)}` entries in this list and I am showing `{self.entries_per_page}` entries per page."

    async def react(self):
        # If the amount of pages is bigger then 1, add the full range of emotes to the message.
        if self.pages > 1:
            for emote in self.emotes.keys():
                await self.message.add_reaction(emote)
        # Otherwise just add the "stop" emote.
        else:
            return await self.message.add_reaction("\u23f9")

    async def stop(self):
        # Delete the message.
        return await self.message.delete()

    async def page_forward(self):
        # If the current page is bigger then or equal to the amount of pages, return
        if self.page >= self.pages - 1:
            return
        # Edit the message to show the next page.
        await self.message.edit(content=f"{self.title}{self.entries[self.page + 1]}\n\nPage: `{self.page + 2}`/`{self.pages}`")
        self.page += 1

    async def page_backward(self):
        # If the current page is smaller then or equal to 0, return
        if self.page <= 0:
            return
        # Edit the message to show the previous page
        await self.message.edit(content=f"{self.title}{self.entries[self.page - 1]}\n\nPage: `{self.page}`/`{self.pages}`")
        self.page -= 1

    async def paginate(self):
        # Send the message for the first page.
        self.message = await self.ctx.send(f"{self.title}{self.entries[self.page]}\n\nPage: `{self.page + 1}`/`{self.pages}`")

        # Add the reactions.
        await self.react()

        # While we are looping.
        while self.looping:
            try:
                # Wait for a reaction to be added and if the reaction is valid, then execute the function linked to that reaction.
                reaction, _ = await self.ctx.bot.wait_for("reaction_add", timeout=600.0, check=lambda r, u: u == self.ctx.author and str(r.emoji) in self.emotes.keys() and r.message.id == self.message.id)

                # If the reaction is the "stop" reaction, stop looping.
                if str(reaction.emoji) == "\u23f9":
                    self.looping = False
                # Else execute the function linked to the reaction added.
                else:
                    await self.emotes[str(reaction.emoji)]()

            # Stop looping after 600 seconds.
            except asyncio.TimeoutError:
                self.looping = False

        # Delete the message.
        return await self.stop()


class EmbedPaginator:

    def __init__(self, **kwargs):
        self.ctx = kwargs.get("ctx")
        self.title = kwargs.get("title")
        self.org_entries = kwargs.get("org_entries")
        self.entries = kwargs.get("entries")
        self.entries_per_page = kwargs.get("entries_per_page")
        self.pages = kwargs.get("pages")
        self.page = 0
        self.message = None
        self.looping = True
        self.emotes = {
            "\u2b05": self.page_backward,
            "\u27a1": self.page_forward,
            "\u23f9": self.stop
        }

        # If the title is not set.
        if self.title is None:
            self.title = f"There are `{len(self.org_entries)}` entries in this list and I am showing `{self.entries_per_page}` entries per page.\n\n"

    async def react(self):
        # If the amount of pages is bigger then 1, add the full range of emotes to the message.
        if self.pages > 1:
            for emote in self.emotes.keys():
                await self.message.add_reaction(emote)
        # Otherwise just add the "stop" emote.
        else:
            return await self.message.add_reaction("\u23f9")

    async def stop(self):
        # Delete the message.
        return await self.message.delete()

    async def page_forward(self):
        # If the current page is bigger then or equal to the amount of pages, return
        if self.page >= self.pages - 1:
            return

        # Edit the embed.
        embed = discord.Embed(
            colour=0x57FFF5,
            description=f"{self.title}{self.entries[self.page + 1]}"
        )
        embed.set_footer(text=f"Page: {self.page + 2}/{self.pages} | Total entries: {len(self.org_entries)}")
        await self.message.edit(embed=embed)

        self.page += 1

    async def page_backward(self):
        # If the current page is smaller then or equal to 0, return
        if self.page <= 0:
            return

        # Edit the embed.
        embed = discord.Embed(
            colour=0x57FFF5,
            description=f"{self.title}{self.entries[self.page - 1]}"
        )
        embed.set_footer(text=f"Page: {self.page}/{self.pages} | Total entries: {len(self.org_entries)}")
        await self.message.edit(embed=embed)

        self.page -= 1

    async def paginate(self):

        # Send the message for the first page.
        embed = discord.Embed(
            colour=0x57FFF5,
            description=f"{self.title}{self.entries[self.page]}"
        )
        embed.set_footer(text=f"Page: {self.page + 1}/{self.pages} | Total entries: {len(self.org_entries)}")
        self.message = await self.ctx.send(embed=embed)

        # Add the reactions.
        await self.react()

        # While we are looping.
        while self.looping:
            try:
                # Wait for a reaction to be added and if the reaction is valid, then execute the function linked to that reaction.
                reaction, _ = await self.ctx.bot.wait_for("reaction_add", timeout=600.0, check=lambda r, u: u == self.ctx.author and str(r.emoji) in self.emotes.keys() and r.message.id == self.message.id)

                # If the reaction is the "stop" reaction, stop looping.
                if str(reaction.emoji) == "\u23f9":
                    self.looping = False
                # Else execute the function linked to the reaction added.
                else:
                    await self.emotes[str(reaction.emoji)]()

            # Stop looping after 600 seconds.
            except asyncio.TimeoutError:
                self.looping = False

        # Delete the message.
        return await self.stop()


