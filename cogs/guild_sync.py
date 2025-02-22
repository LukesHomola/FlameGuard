import discord
from discord.ext import commands
import requests
import re
import os
from dotenv import load_dotenv
import time

# Load .env file to get your token
load_dotenv()

# Replace with the FlameKnights API URL
FLAMEKNIGHTS_API_URL = "https://api.wynncraft.com/v3/guild/FlameKnights"
GUILD_ROLE_NAME = "FlameKnight"
# Mapping Wynncraft ranks to Discord roles
RANK_ROLE_MAPPING = {
    "owner": "👑Emperor",
    "chief": "🌟High King",
    "strategist": "⭐ArchDuke",
    "captain": "⚜️Baron",
    "recruiter": "🛡️Duke",
    "recruit": "🔱Knight"
}

# Normalize the player name by removing emojis, special characters, and converting to lowercase.
def normalize_name(name):
    """Remove emojis, special characters, and convert to lowercase."""
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name.lower()

class GuildSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def assign_roles_silent(self, ctx):
        """Assign the correct in-game rank role to matching guild members without sending messages."""
        guild = ctx.guild  # Use the context guild
        # Fetch guild data from Wynncraft API
        response = requests.get(FLAMEKNIGHTS_API_URL)
        if response.status_code != 200:
            print("Failed to fetch guild data. Please try again later. 😢")
            return

        guild_data = response.json()
        if "members" not in guild_data:
            print("Failed to find members in guild data. 😢")
            return

        # Extract player names from the guild
        flameknights_players = []
        for role, role_members in guild_data["members"].items():
            if isinstance(role_members, dict):
                flameknights_players.extend(role_members.keys())

        # Normalize names
        normalized_guild_players = [normalize_name(player) for player in flameknights_players]

        # Normalize both Discord usernames and display names
        normalized_discord_users = {
            normalize_name(member.name): member for member in guild.members
        }
        normalized_discord_display_names = {
            normalize_name(member.display_name): member for member in guild.members
        }

        assigned_count = 0

        # Go through each in-game rank and assign the corresponding role
        for in_game_rank, discord_role_name in RANK_ROLE_MAPPING.items():
            if in_game_rank in guild_data["members"]:
                discord_role = discord.utils.get(guild.roles, name=discord_role_name)
                if discord_role:
                    for player_name in guild_data["members"][in_game_rank].keys():
                        normalized_player_name = normalize_name(player_name)
                        member = normalized_discord_users.get(normalized_player_name) or normalized_discord_display_names.get(
                            normalized_player_name)

                        if member:
                            # Assign the correct in-game rank role (one role only)
                            if discord_role not in member.roles:
                                try:
                                    await member.add_roles(discord_role)
                                    assigned_count += 1
                                    print(f"Assigned {discord_role.name} role to {member.display_name}")
                                except discord.Forbidden:
                                    print(f"❌ No permission to assign the {discord_role_name} role to {member.display_name}.")
                                except discord.HTTPException:
                                    print(f"⚠️ Failed to assign the {discord_role_name} role to {member.display_name}.")
        
        print(f"Assigned roles silently to {assigned_count} members.")

    @commands.command()
    async def assign_roles(self, ctx):
        # Permissions required to use
        required_role = "FG_Admin"
        member = ctx.author
        
        # Check if player has the permissions to proceed
        if discord.utils.get(member.roles, name=required_role):
            await ctx.send(f"{member.display_name} has the {required_role} role!")
        else:
            await ctx.send(f"{member.display_name} does not have the {required_role} role!")
            return

        
        """Assign the 'FlameKnights' role and highest rank role to matching guild members."""
        await ctx.send("Assigning roles... 🔥")

        # Fetch guild data from Wynncraft API
        response = requests.get(FLAMEKNIGHTS_API_URL)
        if response.status_code != 200:
            await ctx.send("Failed to fetch guild data. Please try again later. 😢")
            return

        guild_data = response.json()
        if "members" not in guild_data:
            await ctx.send("Failed to find members in guild data. 😢")
            return

        # Extract player names from the guild
        flameknights_players = []
        for role, role_members in guild_data["members"].items():
            if isinstance(role_members, dict):
                flameknights_players.extend(role_members.keys())

        # Normalize names
        normalized_guild_players = [normalize_name(player) for player in flameknights_players]

        # Normalize both Discord usernames and display names
        normalized_discord_users = {
            normalize_name(member.name): member for member in ctx.guild.members
        }
        normalized_discord_display_names = {
            normalize_name(member.display_name): member for member in ctx.guild.members
        }

        assigned_count = 0

        # Assign the "FlameKnight" role to members
        flameknight_role = discord.utils.get(ctx.guild.roles, name=GUILD_ROLE_NAME)
        if flameknight_role:
            for player_name in normalized_guild_players:
                member = normalized_discord_users.get(player_name) or normalized_discord_display_names.get(player_name)

                if member and flameknight_role not in member.roles:
                    try:
                        await member.add_roles(flameknight_role)
                        assigned_count += 1
                        await ctx.send(f"Assigned {flameknight_role.name} role to {member.display_name}")
                    except discord.Forbidden:
                        await ctx.send(f"❌ No permission to assign the {flameknight_role.name} role to {member.display_name}.")
                    except discord.HTTPException:
                        await ctx.send(f"⚠️ Failed to assign the {flameknight_role.name} role to {member.display_name}.")

        # Go through each in-game rank and assign the corresponding role
        for in_game_rank, discord_role_name in RANK_ROLE_MAPPING.items():
            if in_game_rank in guild_data["members"]:
                discord_role = discord.utils.get(ctx.guild.roles, name=discord_role_name)
                if discord_role:
                    for player_name in guild_data["members"][in_game_rank].keys():
                        normalized_player_name = normalize_name(player_name)
                        member = normalized_discord_users.get(normalized_player_name) or normalized_discord_display_names.get(
                            normalized_player_name)

                        if member:
                            # Assign the rank role as well
                            if discord_role not in member.roles:
                                try:
                                    await member.add_roles(discord_role)
                                    assigned_count += 1
                                    await ctx.send(f"Assigned {discord_role.name} role to {member.display_name}")
                                except discord.Forbidden:
                                    await ctx.send(f"❌ No permission to assign the {discord_role_name} role to {member.display_name}.")
                                except discord.HTTPException:
                                    await ctx.send(f"⚠️ Failed to assign the {discord_role_name} role to {member.display_name}.")

        await ctx.send(f"Assigned {assigned_count} roles. 🔥")

    @commands.command()
    async def check_discord(self, ctx):
                # Permissions required to use
        required_role = "FG_Admin"
        member = ctx.author
        
        # Check if player has the permissions to proceed
        if discord.utils.get(member.roles, name=required_role):
            await ctx.send(f"{member.display_name} has the {required_role} role!")
        else:
            await ctx.send(f"{member.display_name} does not have the {required_role} role!")
            return

        
        await ctx.send("Checking members... 🔍")

        # Fetch guild data from Wynncraft API
        response = requests.get(FLAMEKNIGHTS_API_URL)
        if response.status_code != 200:
            await ctx.send("Failed to fetch guild data. Please try again later. 😢")
            return

        # Parse the guild data
        guild_data = response.json()

        # Debugging print to inspect the structure of the guild data
        print(guild_data)  # This will show you the data structure

        if "members" not in guild_data:
            await ctx.send("Failed to find members in guild data. 😢")
            return

        # Extract player names from the guild data (case-insensitive)
        flameknights_players = []
        for role, role_members in guild_data["members"].items():
            if role == "total":
                continue  # Skip the "total" key
            if isinstance(role_members, dict):
                for member_name in role_members.keys():
                    flameknights_players.append(member_name)
            else:
                await ctx.send(f"Unexpected format for role members: {role_members}")
                return

        # Fetch the list of Discord members (both display name and username)
        discord_members = [normalize_name(member.display_name) for member in ctx.guild.members] + \
            [normalize_name(member.name) for member in ctx.guild.members]

        # Normalize the in-game player names
        normalized_flameknights_players = [normalize_name(
            player) for player in flameknights_players]

        # Find missing players
        missing_players = [
            player for player in normalized_flameknights_players if player not in discord_members]

        if not missing_players:
            await ctx.send("All FlameKnights are in the Discord server! 👑🎉")
        else:
            # Prepare the table header
            table_header = "```markdown\n" + \
                "{:<25}  {:<10}".format("Player Name", "Status") + "\n"
            table_separator = "-" * 50  # Create a separator for the table

            # Prepare the rows for missing players
            missing_rows = "\n".join(
                [f"{player:<25}  {'Missing':<10}" for player in missing_players])

            # Combine the header, separator, and rows
            table_message = table_header + table_separator + "\n" + missing_rows + "\n```"

            await ctx.send(table_message)
            await ctx.send("Make sure to double check missing players! 👀")



# Register cog
async def setup(bot):
    await bot.add_cog(GuildSync(bot))

