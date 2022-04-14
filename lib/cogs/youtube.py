from youtubesearchpython import *
from discord.ext.commands import Cog
from discord.ext.commands import command
from typing import Optional

class YouTube(Cog):
	def __init__(self, bot):
		self.bot = bot

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("youtube")

	@command(name="yt", aliases=["youtube", "video"])
	async def yt_search(self, ctx, *, search_term: Optional[str]=""):
		if search_term == "":
			pass
		else:
			search = CustomSearch(search_term, VideoSortOrder.uploadDate, limit=10)
			result = search.result()['result']
			no_live = [r for r in result if r["duration"]]
			await ctx.send(no_live[0]["link"])

def setup(bot):
	bot.add_cog(YouTube(bot))