from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions
from discord import Embed
from datetime import datetime, timedelta
from ..db import db

#1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣ 9️⃣

numbers = ("1️⃣", "2⃣", "3⃣", "4⃣", "5⃣",
		   "6⃣", "7⃣", "8⃣", "9⃣", "🔟")
STARBOARD_EMOJI = "⭐"

STARBOARD_CHANNEL = 964016888961204316

class Reactions(Cog):
	def __init__(self, bot):
		self.bot = bot
		self.polls = []

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.starboard_channel = self.bot.get_channel(STARBOARD_CHANNEL)
			self.bot.cogs_ready.ready_up("reactions")


	@command(name="createpoll", aliases=["mkpoll", "poll"])
	@has_permissions(manage_guild=True)
	async def create_poll(self, ctx, seconds: int, question: str, *options):
		embed = Embed(title="Poll", 
					  description=question,
					  color=ctx.author.color,
					  timestamp=datetime.utcnow())

		fields = [("Options", "\n".join([f"{numbers[idx]} {option}" for idx, option in enumerate(options)]), False)]

		for name, value, inline in fields:
			embed.add_field(name=name, value=value, inline=inline)
 
		message = await ctx.send(embed=embed)

		for emoji in numbers[:len(options)]:
			await message.add_reaction(emoji)

		self.polls.append((message.channel.id, message.id))

		self.bot.scheduler.add_job(self.complete_poll, "date", run_date=datetime.now()+timedelta(seconds=seconds),
								   args=[message.channel.id, message.id])

	async def complete_poll(self, channel_id, message_id):
		message = await self.bot.get_channel(channel_id).fetch_message(message_id)

		most_voted = max(message.reactions, key=lambda r: r.count)

		await message.channel.send(f"{most_voted.emoji} was the highest voted with {most_voted.count-1} votes")
		self.polls.remove((message.channel.id, message.id))
		
	@Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		if not self.bot.ready and payload.message_id == self.reaction_message.id:
			pass

	
		elif payload.emoji.name == STARBOARD_EMOJI:
			message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
			


			if not message.author.bot and payload.member.id != message.author.id:
				msg_id, stars = db.record("SELECT StarMessageID, Stars FROM starboard WHERE RootMessageID = ?", 
										  message.id) or (None, 0)
				embed = Embed(title="Starred Message", 
							  color=0x00FF00,
							  timestamp=datetime.utcnow())
				embed.set_thumbnail(url=message.author.avatar_url)

				fields = [("Author", message.author.mention, False),
						  ("Content", message.content or "See attachment", False),
						  ("Stars", stars-1, False),
						  ("Link", message.jump_url, False)]

				for name, value, inline in fields:
					embed.add_field(name=name, value=value, inline=inline)

				if len(message.attachments):
					embed.set_image(url=message.attachments[0].url)

				if not stars-1:
					star_message = await self.starboard_channel.fetch_message(msg_id)
					db.execute("DELETE FROM starboard WHERE StarMessageID = ?",
								star_message.id)
					db.commit()
					await star_message.delete()

				else:
					star_message = await self.starboard_channel.fetch_message(msg_id)
					await star_message.edit(embed=embed)
					db.execute("UPDATE starboard SET Stars = Stars - 1 WHERE RootMessageID = ?", message.id)
					db.commit()
			

	@Cog.listener()
	async def on_raw_reaction_add(self, payload):
		if not self.bot.ready and payload.message_id == self.reaction_message.id:
			pass

		elif payload.message_id in (poll[1] for poll in self.polls):
			message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

			for reaction in message.reactions:
				if (not payload.member.bot
					and payload.member in await reaction.users().flatten()
					and reaction.emoji != payload.emoji.name):
					await message.remove_reaction(reaction.emoji, payload.member)

		elif payload.emoji.name == STARBOARD_EMOJI:
			message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
			


			if not message.author.bot and payload.member.id != message.author.id:
				msg_id, stars = db.record("SELECT StarMessageID, Stars FROM starboard WHERE RootMessageID = ?", 
										  message.id) or (None, 0)
				embed = Embed(color=0x00FF00,
							  timestamp=datetime.utcnow())
				embed.set_thumbnail(url=message.author.avatar_url)

				fields = [("Author", message.author.mention, False),
						  ("Content", message.content or "See attachment", False),
						  ("Stars", stars+1, False),
						  ("Link", message.jump_url, False)]

				for name, value, inline in fields:
					embed.add_field(name=name, value=value, inline=inline)

				if len(message.attachments):
					embed.set_image(url=message.attachments[0].url)

				if not stars:

					star_message = await self.starboard_channel.send(embed=embed)
					db.execute("INSERT INTO starboard (RootMessageID, StarMessageID) VALUES (?, ?)",
								message.id, star_message.id)
					db.commit()
				else:
					star_message = await self.starboard_channel.fetch_message(msg_id)
					await star_message.edit(embed=embed)
					db.execute("UPDATE starboard SET Stars = Stars + 1 WHERE RootMessageID = ?", message.id)
					db.commit()
			else:
				await message.remove_reaction(payload.emoji, payload.member)

	


def setup(bot):
	bot.add_cog(Reactions(bot))