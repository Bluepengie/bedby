from youtubesearchpython import *
from discord.ext.commands import Cog
from discord.ext.commands import *
from discord import Embed
from typing import Optional
from datetime import datetime



class YouTube(Cog):
	def __init__(self, bot):
		self.bot = bot

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("youtube")

	@command(name="yt", aliases=["youtube", "video"])
	@cooldown(1, 60, BucketType.user)
	async def yt_search(self, ctx, *, search_term: Optional[str]=""):
		if ctx.channel.id == self.bot.main_spamchannel:
			ctx.command.reset_cooldown(ctx)
		if search_term == "":
			pass
		else:
			search = CustomSearch(search_term, VideoSortOrder.uploadDate, limit=5)
			result = search.result()['result']
			no_live = [r for r in result if r["duration"]]
			link = no_live[0]["link"]
			embed = Embed(color=ctx.author.color,
						  timestamp=datetime.utcnow(),
						  thumbnail=ctx.author.avatar_url)
			fields = [("Requested by", ctx.author.mention, True),
					  ("Search term", search_term, True),
					  ("Link", link, True)]
			msg = f"Requested by: {ctx.author.mention}\nSearch term: \"{search_term}\"\n{link}"
			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)
			await ctx.message.delete()
			await ctx.send(msg)

def setup(bot):
	bot.add_cog(YouTube(bot))