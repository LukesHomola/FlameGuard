import discord
from discord.ext import commands
import requests
import re
import os
from dotenv import load_dotenv

# Load .env file to get your token
load_dotenv()

# Replace with the FlameKnights API URL
FLAMEKNIGHTS_API_URL = "https://api.wynncraft.com/v3/guild/FlameKnights"
GUILD_ROLE_NAME = "FlameKnight"

# Normalize the player name by removing emojis, special characters, and converting to lowercase.
def normalize_name(name):
    """Remove emojis, special characters, and convert to lowercase."""
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name.lower()

class Challenges(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def challenges_help(self, ctx):
        # Permissions required to use
        required_role = "flameKnight"
        member = ctx.author
        
        # Check if player has the permissions to proceed
        if discord.utils.get(member.roles, name=required_role):
            await ctx.send(f"{member.display_name} has the {required_role} role!")
        else:
            await ctx.send(f"{member.display_name} does not have the {required_role} role!")
            return

        embed = discord.Embed(title="Guild challenges informative board",
                            description="**!guard_help** - Show the list of available commands. " + "\n" +
                            "**!check_discord** - List of guild members missing on our discord. " + "\n" +
                            "**!assign_roles** - Assign discord member role if player is part of the guild. ",
                            color=discord.Color.red())
        await ctx.send(embed=embed)





# Register cog
async def setup(bot):
    await bot.add_cog(GuildSync(bot))

