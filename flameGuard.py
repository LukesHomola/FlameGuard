import discord
from discord.ext import commands
import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()

# Bot setup
intents = discord.Intents.all()
intents.members = True  # Required to fetch members from the Discord server
intents.messages = True  # Required to read messages for commands

bot = commands.Bot(command_prefix="!", intents=intents)

# Replace with your Discord Bot Token
token = os.getenv("BOT_TOKEN")

# Replace with the FlameKnights API URL
FLAMEKNIGHTS_API_URL = "https://api.wynncraft.com/v3/guild/FlameKnights"
GUILD_ROLE_NAME = "FlameKnight"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Bot is ready to guard FlameKnights! 👑")

@bot.command()
async def guard_help(ctx):
    """Show the list of available commands"""
    embed = discord.Embed(title="FlameGuard Commands",   
                          description="**!guard_help** - Show the list of available commands. " + "\n" +
                          "**!check_discord** - List of guild members missing on our discord. " + "\n" +
                          "**!assign_roles** - Assign discord member role if player is part of the guild. " , 
                          color=discord.Color.red() )
    await ctx.send(embed=embed)

""" Normalize the player name by removing emojis, special characters, and converting to lowercase. For missing players"""
def normalize_name(name):
    """Remove emojis, special characters, and convert to lowercase."""
    # Remove common symbols, including those used for Discord and emojis
    name = re.sub(r'[^\w\s]', '', name)  # Remove everything except word characters and spaces
    name = re.sub(r'\s+', ' ', name).strip()  # Clean up extra spaces and normalize spacing
    return name.lower()

@bot.command()
async def check_discord(ctx):
    """Check if all FlameKnights are in the Discord server."""
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
    normalized_flameknights_players = [normalize_name(player) for player in flameknights_players]

    # Find missing players
    missing_players = [player for player in normalized_flameknights_players if player not in discord_members]


    if not missing_players:
        await ctx.send("All FlameKnights are in the Discord server! 👑🎉")
    else:
        # Prepare the table header
        table_header = "```markdown\n" + "{:<25}  {:<10}".format("Player Name", "Status") + "\n"
        table_separator = "-" * 50  # Create a separator for the table

        # Prepare the rows for missing players
        missing_rows = "\n".join([f"{player:<25}  {'Missing':<10}" for player in missing_players])
        
        # Combine the header, separator, and rows
        table_message = table_header + table_separator + "\n" + missing_rows + "\n```"

        await ctx.send(table_message)
        await ctx.send("Make sure to double check missing players! 👀")

@bot.command()
async def assign_roles(ctx):
    """Assign the 'FlameKnights' role to matching guild members in Discord."""
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
            print(f"Role: {role}, Members Found: {len(role_members)}")  # Debugging
            flameknights_players.extend(role_members.keys())  # Add members
        else:
            print(f"Unexpected format in role: {role}")  # Debugging for errors

    print("Total Players Extracted:", len(flameknights_players))  # Final count

    # Normalize names
    normalized_guild_players = [normalize_name(player) for player in flameknights_players]

    # Normalize both Discord usernames and display names
    normalized_discord_users = {
        normalize_name(member.name): member for member in ctx.guild.members
    }
    normalized_discord_display_names = {
        normalize_name(member.display_name): member for member in ctx.guild.members
    }

    # Get the "FlameKnights" role
    role = discord.utils.get(ctx.guild.roles, name=GUILD_ROLE_NAME)
    if not role:
        await ctx.send(f"❌ Role '{GUILD_ROLE_NAME}' not found! Please create the role first.")
        return
    
    # Debugging information
    print("\n")
    print("Total Discord Members:", len(normalized_discord_users))
    print("Total Guild Members:", len(normalized_guild_players))

    assigned_count = 0
    unmatched_players = []  # List of players not found in Discord

    for player in normalized_guild_players:
        member = None

        # Try to match the player with Discord usernames or display names
        if player in normalized_discord_users:
            member = normalized_discord_users[player]
        elif player in normalized_discord_display_names:
            member = normalized_discord_display_names[player]

        if member:
            if role not in member.roles:
                try:
                    await member.add_roles(role)
                    assigned_count += 1
                except discord.Forbidden:
                    await ctx.send(f"❌ I do not have permission to assign roles to {member.mention}.")
                except discord.HTTPException:
                    await ctx.send(f"⚠️ Failed to assign role to {member.mention}. Please try again.")
        else:
            unmatched_players.append(player)  # Store the names that didn't match

    print(f"✅ Successfully Assigned Roles: {assigned_count}")
    print(f"❌ Players Not Found in Discord: {len(unmatched_players)}")
    print("Unmatched Players:", unmatched_players)  # Print missing players for debugging

    if unmatched_players:
        unmatched_list = "\n".join(unmatched_players)
        await ctx.send(f"⚠️ The following **{len(unmatched_players)}** players were not found in Discord:\n```{unmatched_list}```")
        await ctx.send("Make sure their Discord usernames match their in-game names!")

    await ctx.send(f"✅ Assigned '{GUILD_ROLE_NAME}' role to **{assigned_count}** members!")

    # Check for discord members not in the guild
    for member in ctx.guild.members:
        if any(role.name == "🤖BOT" or role.name != "FlameKnight" for role in member.roles):
            continue # Skip the bot
        normalized_member_name = normalize_name(member.name)
        normalized_member_display_name = normalize_name(member.display_name)
        if normalized_member_name not in normalized_guild_players and normalized_member_display_name not in normalized_guild_players:
            await ctx.send(f"❌ {member.display_name} ({member.name}) is not part of the FlameKnights guild.")
    
    await ctx.send("🔥 FlameKnights have been guarded! 👑")


            
# Run the bot
bot.run(token = os.getenv("BOT_TOKEN")
)
