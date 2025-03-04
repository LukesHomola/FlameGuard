import discord
from discord.ext import commands

class Challenges(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def active_challenges(self, ctx):
        # Check if player has the permissions to proceed
        required_role = "FlameKnight"
        member = ctx.author
        
        # Check if player has the permissions to proceed
        if discord.utils.get(member.roles, name=required_role):
            await ctx.send(f"{member.display_name} has the {required_role} role!")
        else:
            await ctx.send(f"{member.display_name} does not have the {required_role} role!")
            return
        
        embed = discord.Embed(
            title="❔**CHALLENGE - ACTIVE CHALLENGES**❔",
            description="‎ ‎ ‎ ‎‎ ‎ ‎  - This feature is under rework.\n",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def challenge_hall_of_frames(self, ctx):
        # Check if player has the permissions to proceed
        required_role = "FlameKnight"
        member = ctx.author
        
        # Check if player has the permissions to proceed
        if discord.utils.get(member.roles, name=required_role):
            await ctx.send(f"{member.display_name} has the {required_role} role!")
        else:
            await ctx.send(f"{member.display_name} does not have the {required_role} role!")
            return

        embed = discord.Embed(
            title="**CHALLENGE - HALL OF FRAMES**",
            description="❔ **CHALLENGE DESCRIPTION** ❔\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - Competition in best looking WynnShot.\n"
                        "‎ ‎ ‎ ‎ ‎ ‎  - Use the subthread for this challenge.\n"
                        "‎ ‎ ‎ ‎ ‎ ‎  - **HINT**: Photoshop / similar programs are allowed.\n\n"
                        "❓ **CHALLENGE RULES** ❓\n\n"
                        "‎ ‎ ‎ ‎ ‎ ‎  - At least 3 submissions are needed to prevent challenge cancellation.\n"
                        "‎ ‎ ‎ ‎ ‎ ‎  - Only one submission per player\n"
                        "‎ ‎ ‎ ‎ ‎ ‎  - The screenshot must be taken in the world of Wynncraft.\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - The posted image must be entirely your own work!\n\n"
                        "📘 Recommended level: Any level\n\n"
                        "📜 **CHALLENGE INFORMATION** 📜\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - Challenge starts <t:1740999600:R>\n"
                        "‎ ‎ ‎ ‎ ‎ ‎  - Challenge ends <t:1743674400:R>\n"
                        "💰 **CHALLENGE PRIZE POOL** 💰\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - 🥇 1 Guild Tome + 15 LE\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - 🥈 10 LE\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - 🥉 5 LE + 5 uth runes",
            color=discord.Color.yellow()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def challenge_xp_weekly(self, ctx):
        # Check if player has the permissions to proceed
        required_role = "FlameKnight"
        member = ctx.author
        
        # Check if player has the permissions to proceed
        if discord.utils.get(member.roles, name=required_role):
            await ctx.send(f"{member.display_name} has the {required_role} role!")
        else:
            await ctx.send(f"{member.display_name} does not have the {required_role} role!")
            return

        embed = discord.Embed(
            title="**CHALLENGE - XP WEEKLY**",
            description="❔ **CHALLENGE DESCRIPTION** ❔\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - Contribute most xp to the guild in next week.\n"
                        "‎ ‎ ‎ ‎ ‎ ‎  - You can check current **top** players by **contributed **xp - **/guild list**\n"
                        "‎ ‎ ‎ ‎ ‎ ‎  - **HINT**: Use command /guild xp <% number> to contribute xp\n\n"
                        "❓ **CHALLENGE RULES** ❓\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - Minimum contributed in this period: 50,000,000 guild xp.\n\n"
                        "📘 Recommended level: 105\n\n"
                        "📜 **CHALLENGE INFORMATION** 📜\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - Challenge starts <t:1740351600:R>\n"
                        "‎ ‎ ‎ ‎ ‎ ‎  - Challenge ends <t:1740956400:R>\n\n"
                        "💰 **CHALLENGE PRIZE POOL** 💰\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - 🥇 1 Guild Tome + 5 LE\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - 🥈 3 LE\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - 🥉 1 LE + 5 uth runes",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def challenge_xp_monthly(self, ctx):
        # Check if player has the permissions to proceed
        required_role = "FlameKnight"
        member = ctx.author
        
        # Check if player has the permissions to proceed
        if discord.utils.get(member.roles, name=required_role):
            await ctx.send(f"{member.display_name} has the {required_role} role!")
        else:
            await ctx.send(f"{member.display_name} does not have the {required_role} role!")
            return
        
        embed = discord.Embed(
            title="**CHALLENGE - XP MONTHLY**",
            description="❔ **CHALLENGE DESCRIPTION** ❔\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - Contribute most xp to the guild in next month.\n"
                        "‎ ‎ ‎ ‎ ‎ ‎  - You can check current **top** players by **contributed **xp - **/guild list**\n"
                        "‎ ‎ ‎ ‎ ‎ ‎  - **HINT**: Use command /guild xp <% number> to contribute xp\n\n"
                        "❓ **CHALLENGE RULES** ❓\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - Minimum contributed in this period: 300,000,000 guild xp.\n\n"
                        "📘 Recommended level: 105\n\n"
                        "📜 **CHALLENGE INFORMATION** 📜\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - Challenge starts <t:1740783600:R>\n"
                        "‎ ‎ ‎ ‎ ‎ ‎  - Challenge ends <t:1743458400:R>\n\n"
                        "💰 **CHALLENGE PRIZE POOL** 💰\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - 🥇 1 Guild Tome + 15 LE\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - 🥈 5 LE + 15 uth runes\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - 🥉 3 LE + 5 uth runes",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def challenge_guild_streak(self, ctx):
        # Check if player has the permissions to proceed
        required_role = "FlameKnight"
        member = ctx.author
        
        # Check if player has the permissions to proceed
        if discord.utils.get(member.roles, name=required_role):
            await ctx.send(f"{member.display_name} has the {required_role} role!")
        else:
            await ctx.send(f"{member.display_name} does not have the {required_role} role!")
            return

        embed = discord.Embed(
            title="**CHALLENGE - GUILD OBJECTIVE STREAK - MONTHLY**",
            description="❔ **CHALLENGE DESCRIPTION** ❔\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - Have the highest guild objective streak.\n"
                        "‎ ‎ ‎ ‎ ‎ ‎  - **HINT**: Use compass -> guild banner -> key -> Look at player's streaks.\n\n"
                        "❓ **CHALLENGE RULES** ❓\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - Minimum streak: 1\n" + 
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - If multiple players have same value, player who have joined the guild erlier, wins.\n\n"

                        "📘 Recommended level: **Any level**\n\n"
                        "📜 **CHALLENGE INFORMATION** 📜\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - Challenge starts <t:1740783600:R>\n"
                        "‎ ‎ ‎ ‎ ‎ ‎  - Challenge ends <t:1743458400:R>\n\n"
                        "💰 **CHALLENGE PRIZE POOL** 💰\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - 🥇 5 LE\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - 🥈 3 LE\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - 🥉 1 LE + 5 uth runes",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    # Challenge closed messages

    @commands.command()
    async def challenge_xp_weekly_closed(self, ctx):
        # Check if player has the permissions to proceed
        required_role = "FG_Admin"
        member = ctx.author
        
        # Check if player has the permissions to proceed
        if discord.utils.get(member.roles, name=required_role):
            await ctx.send(f"{member.display_name} has the {required_role} role!")
        else:
            await ctx.send(f"{member.display_name} does not have the {required_role} role!")
            return

        embed = discord.Embed(
            title="**CHALLENGE CLOSED  - XP WEEKLY**",
            description="🏆 **WINNER ANNOUCEMENT** 🏆\n\n"
                        "📜 **CHALLENGE INFORMATION** 📜\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - Contribute most xp to the guild in next week.\n"
                        "‎ ‎ ‎ ‎ ‎ ‎  - Challenge ended <t:1740956400:R>\n\n"
                        "❓ **CHALLENGE RULES** ❓\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - Minimum contributed in this period: 50,000,000 guild xp.\n\n"
                        "🏆 **CHALLENGE WINNERS** 🏆\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - 🥇 <@931870081913339974> - 1 Guild Tome + 5 LE\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - 🥈 **NONE** - 3 LE\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - 🥉 **NONE** - 1 LE + 5 uth runes\n\n"
                        "❔ **REWARD CLAIM** ❔\n\n"
                        "‎ ‎ ‎ ‎‎ ‎ ‎  - To claim your reward, please contact <@437685536585547797>\n\n"
                        "🎉 **CONGRATULATIONS!** 🎉\n\n",

            color=discord.Color.green()
        )
        await ctx.send(embed=embed)


# Register cog
async def setup(bot):
    await bot.add_cog(Challenges(bot))


# Register cog
async def setup(bot):
    await bot.add_cog(Challenges(bot))
