from random import choice, randint
from typing import Optional
from discord import Member
from discord.errors import HTTPException
from discord.ext.commands import Cog
from discord.ext.commands import command

class Fun(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="hello", aliases=["hi"])
	async def say_hello(self, ctx):
		await ctx.send(f"Hello {ctx.author.mention}!")

	@command(name="dice", aliases=["roll"])
	async def roll_dice(self, ctx, die_string: str):
		dice, value = (int(term) for term in die_string.split("d"))
		rolls = [randint(1, value) for i in range(dice)]

		await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

	@command(name="dink")
	async def dink_member(self, ctx, member: Member, *, reason: Optional[str] = "just because"):
		await ctx.send(f"{ctx.author.mention} dinked {member.mention} {reason}")

	@dink_member.error
	async def dink_member_error(self, ctx, exc):
		if isinstance(exc, BadArgument):
			await ctx.send("Can't find that user")

	@command(name="echo", aliases=["say"])
	async def echo_message(self, ctx, *, message):
		await ctx.message.delete()
		await ctx.send(message)


	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("fun")

def setup(bot):
	bot.add_cog(Fun(bot))