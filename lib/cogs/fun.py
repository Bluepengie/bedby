from random import choice, randint
from typing import Optional
from discord import Member, Embed
from discord.errors import HTTPException
from discord.ext.commands import Cog
from discord.ext.commands import *
from ..db import db
import requests
import json

# sex_choice = [f"{ctx.author.mention} and {member.mention}? 😳",
# 			  f"Hey {member.mention}... {ctx.author.mention} wants you 😏",
# 			  f"LITERALLY {ctx.author.mention} AND {member.mention} RIGHT NOW 😩😩😩"]
apikey = "YK14B1TP47V4"

class Fun(Cog):
	def __init__(self, bot):
		self.bot = bot

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("fun")

	@command(name="hello", aliases=["hi"])
	async def say_hello(self, ctx):
		await ctx.send(f"Hello {ctx.author.mention}!")

	@command(name="dice", aliases=["roll"])
	async def roll_dice(self, ctx, die_string: str):
		dice, value = (int(term) for term in die_string.split("d"))
		rolls = [randint(1, value) for i in range(dice)]

		await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

	@command(name="dink")
	@cooldown(3, 30, BucketType.user)
	async def dink_member(self, ctx, member: Member, *, reason: Optional[str] = "just because"):
		if member.id == self.bot.user.id:
			await ctx.send("You can't dink me!")

		elif member.bot:
			await ctx.send(f"Be advised, bots do not count for the dinkboard!")
		else:
			await ctx.send(f"{ctx.author.mention} dinked {member.mention} {reason}")
			await ctx.message.delete()
			db.execute("UPDATE dinkboard SET DinkOut = DinkOut + 1 WHERE UserID = ?", ctx.author.id)
			db.execute("UPDATE dinkboard SET DinkIn = DinkIn + 1 WHERE UserID = ?", member.id)
			db.commit()

	@command(name="dinklist", aliases=["dinkinit"], pass_context=True)
	@is_owner()
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
	@is_owner()
	async def echo_message(self, ctx, *, message):
		await ctx.message.delete()
		await ctx.send(message)

	@command(name="hug")
	async def hug_gif(self, ctx, member: Member):
		gif_link = await random_gif(self, ctx, "hug")
		msg = f"Hug from {ctx.author.display_name} to {member.mention} ❤️"
		await ctx.send(msg)
		await ctx.send(gif_link)

	@command(name="sex")
	async def sex_gif(self, ctx, member: Member):
		sex_choice = [f"{ctx.author.display_name} and {member.mention}? 😳",
			  f"Hey {member.display_name}... {ctx.author.mention} wants you 😏",
			  f"LITERALLY {ctx.author.display_name} AND {member.mention} RIGHT NOW 😩😩😩"]
		gif_link = await random_gif(self, ctx, "sex")
		msg = choice(sex_choice)
		await ctx.send(msg)
		await ctx.send(gif_link)

	@command(name="gif", aliases=["randomgif"], pass_context=True)
	async def gif_rand(self, ctx, *, search_term: Optional[str] =""):
		if search_term == "":
			gif_link = await trending_gif(self,ctx)
		else:
			gif_link = await random_gif(self, ctx, search_term)
		await ctx.send(gif_link)



def setup(bot):
	bot.add_cog(Fun(bot))

async def random_gif(self, ctx, search_term):
	lmt = 1
	r = requests.get(
		f"https://g.tenor.com/v1/random?q={search_term}&key={apikey}&limit={lmt}")
	if r.status_code == 200:
		data = json.loads(r.content)
		gif = data['results'][0]['media'][0]['gif']['url']
		return gif

async def trending_gif(self, ctx):
	lmt = 50
	r = requests.get(
		f"https://g.tenor.com/v1/trending?key={apikey}&limit={lmt}")
	if r.status_code == 200:
		data = json.loads(r.content)
		gif = data['results'][randint(0,49)]['media'][0]['gif']['url']
		return gif