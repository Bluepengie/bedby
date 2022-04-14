from random import choice, randint
from typing import Optional
from discord import Member
from discord.errors import HTTPException
from discord.ext.commands import Cog
from discord.ext.commands import command
from ..db import db


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
		if member.id == self.bot.user.id:
			await ctx.send("You can't dink me!")

		elif member.bot:
			await ctx.send(f"{ctx.author.mention} dinked {member.mention} {reason}\nBe advised, bots do not count for the dinkboard!")
		else:
			await ctx.send(f"{ctx.author.mention} dinked {member.mention} {reason}")
			db.execute("UPDATE dinkboard SET DinkOut = DinkOut + 1 WHERE UserID = ?", ctx.author.id)
			db.execute("UPDATE dinkboard SET DinkIn = DinkIn + 1 WHERE UserID = ?", member.id)
			db.commit()

	@command(name="dinklist", aliases=["dinkinit"])
	async def dinklist(self, ctx):
		members = ctx.guild.members
		new_members = 0
		existing_members = 0
		bots = 0
		for user in members:
			print(user.display_name)
			bots += 1
			if user.bot:
				print("Bot detected")
			elif db.record("SELECT UserID FROM dinkboard WHERE UserID = ?", user.id):
				print("Existing member detected")
				existing_members += 1
			else:
				print("New member detected")
				db.record("INSERT INTO dinkboard (UserID) VALUES (?)", user.id)
				new_members += 1
		db.commit()
		await ctx.send(f"Successfully added {new_members} new members to the dinkboard, and verified {existing_members} members.")

	@command(name="dinkscore", aliases=["dinkboard", "leaderboard", "rankings"])
	async def dink_leaderboard(self, ctx, rankings = 5, dinkOut = False):
		guild = ctx.guild
		if dinkOut:
			rows = db.records("SELECT UserID, DinkOut FROM dinkboard ORDER BY DinkOut DESC")
			names = [guild.get_member(row[0]).display_name for row in rows]
			vals = [row[1] for row in rows]

			if len(rows) < rankings:
				rankings = len(rows)

			finalStr = ""

			for i in range(rankings):
				finalStr += f"{i+1}. {names[i]}\t{vals[i]}\n"
			await ctx.send(finalStr)
		else:
			rows = db.records("SELECT UserID, DinkIn FROM dinkboard ORDER BY DinkIn DESC")
			names = [guild.get_member(row[0]).display_name for row in rows]
			vals = [row[1] for row in rows]

			if len(rows) < rankings:
				rankings = len(rows)

			finalStr = ""
			
			for i in range(rankings):
				finalStr += f"{i+1}. {names[i]}\t{vals[i]}\n"
			await ctx.send(finalStr)


	# @dink_member.error
	# async def dink_member_error(self, ctx, exc):
	# 	if isinstance(exc, BadArgument):
	# 		await ctx.send("Can't find that user")

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