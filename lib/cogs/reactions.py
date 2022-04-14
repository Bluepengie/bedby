from discord.ext.commands import Cog
from discord.ext.commands import command
from discord import Embed
from datetime import datetime
from ..db import db



STARBOARD_EMOJI = "⭐"

class Reactions(Cog):
	def __init__(self, bot):
		self.bot = bot

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.starboard_channel = self.bot.get_channel(964016888961204316)
			self.bot.cogs_ready.ready_up("reactions")


	@Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		if not self.bot.ready and payload.message_id == self.reaction_message.id:
			pass
		elif payload.emoji.name == STARBOARD_EMOJI:
			message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
			


			if not message.author.bot: #and payload.member.id != message.author.id:
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
		elif payload.emoji.name == STARBOARD_EMOJI:
			message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
			


			if not message.author.bot: #and payload.member.id != message.author.id:
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