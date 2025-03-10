import discord
from discord.ext import commands
import mysql.connector
import os
import requests
import schedule
import time

class Referral(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.connect_db()

    # Connecting to database
    def connect_db(self):
        try:
            conn = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password=os.getenv("DB_PASS"),
                database=os.getenv("DB_NAME")  
            )
            print("✅ Connected to MySQL")
            return conn
        except mysql.connector.Error as e:
            print(f"❌ Failed to connect to MySQL: {e}")
            return None


    @commands.command(name="refer")
    async def refer(self, ctx, referred_ign: str = None):
        """Command to add a referral (only IGN is needed)"""
        # Permissions required to use
        required_role = "Recruiting"
        member = ctx.author
        
        # Check if player has the permissions to proceed
        if discord.utils.get(member.roles, name=required_role):
            print(f"{member.display_name} has the {required_role} role!")
        else:
            await ctx.send(f"{member.display_name} does not have the {required_role} role!")
            return

        if not referred_ign:
            await ctx.send("❌ Incorrect usage \n\n **Usage:** `!refer <IGN>`\n Example: `!refer Steve`")
            return
        
        referred_member = None

        # Fetching guild players to get playtime at join
        response = requests.get("https://api.wynncraft.com/v3/player/" + referred_ign)
        referred = response.json() 
        playtime = referred.get("playtime", 0) 

        # Print raw response (before converting to JSON)
        #print(f"Response Status Code: {response.status_code}")
        #print(f"Raw Response Text: {response.text}")
        #print(f"Player Playtime: {playtime} hours")
        

        if response.status_code != 200:
            return await print(f"❌ Failed to fetch player data for `{referred_ign}`. Try again later.")
        else:
            guild_data = response.json()
            print(guild_data)  # Print the full JSON response for debugging


        # If mention is used (ex: !refer @Steve), extract user ID
        if referred_ign.startswith("<@") and referred_ign.endswith(">"):
            mentioned_id = referred_ign.strip("<@!>")  # Remove <@ and > and also handle <@!ID> format
            referred_member = ctx.guild.get_member(int(mentioned_id))
        else:
            # Normalize the input (convert to lowercase and remove leading emoji/symbol)
            normalized_ign = referred_ign.lower().lstrip("🔱🛡️⚜️⭐🌟👑📃")  # Add more symbols if needed

            # Try matching by exact Discord username
            referred_member = discord.utils.find(lambda m: m.name.lower() == normalized_ign, ctx.guild.members)

            # If not found, try matching by Discord server nickname (display_name)
            if not referred_member:
                referred_member = discord.utils.find(lambda m: m.display_name.lower().lstrip("🔥⭐🌟💀") == normalized_ign, ctx.guild.members)

        if not referred_member:
            return await ctx.send(f"❌ Member not found \n\n Could not find the user `{referred_ign}` in the server.")

        bot_role = discord.utils.get(ctx.guild.roles, name="🤖BOT")

        if referred_member.bot or (bot_role and bot_role in referred_member.roles):
            return await ctx.send(f"❌ `{referred_member.display_name}` cannot referr a bot.")

        referred_ign = referred_member.display_name  # Store clean username in the database
        referred_id = referred_member.id  

        referrer_ign = ctx.author.name
        referrer_id = ctx.author.id

        # Send message to verify in to the referral log
        channel = self.bot.get_channel(1346441543996674131)


        if not self.db:
            await ctx.send("❌ Database connection is unavailable.")
            return

        query = """
        INSERT INTO referrals (referrer_ign, referrer_id, referred_ign, referred_id, logged_at, referred_since, last_activity, valid, hours)
        VALUES (%s, %s, %s, %s, NOW(), NUll, NULL, FALSE, %s)
        """
        values = (referrer_ign, referrer_id, referred_ign, referred_id, playtime)



        try:
            cursor = self.db.cursor()
            cursor.execute(query, values)
            self.db.commit()
            await ctx.send(f"✅ Referral created \n\n {referred_ign} has been referred by {referrer_ign}, but is **not verified yet**.")
            if channel:
                embed = discord.Embed(
                    title="🚫 **New referral - Approval needed**",
                    description="A new referral request has been submitted and requires verification.",
                    color=discord.Color.orange()
                )

                embed.add_field(name="🙍 Referred by:", value=f"⠀- {referrer_ign}", inline=False)  # ⠀ Invisible space for indent
                embed.add_field(name="🙍 Referred player:", value=f"⠀- {referred_ign}", inline=False)

                # Add an empty field for spacing (gap between rows)
                embed.add_field(name="\u200b", value="\u200b", inline=False)  # Invisible character to create a gap

                embed.add_field(name="Instructions:", value="Use !verify <IGN> to approve this referral.", inline=False)
                embed.set_footer(text="React with ✅ to verify this referral. React with ❌ to remove the referral.")

                message = await channel.send(embed=embed)


                # Add reactions to the message
                await message.add_reaction("✅")  # Verify reaction
                await message.add_reaction("❌")  # Remove reaction

                # Add the "🔁" reaction before processing any other actions
                if "🔁" not in [reaction.emoji for reaction in reaction.message.reactions]:
                    await reaction.message.add_reaction("🔁")  # Allow changing decision

            else:
                await ctx.send("❌ Unable to find referral channel.") 
        except mysql.connector.Error as e:
            await ctx.send(f"❌ Error adding referral: {e}")
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Handles reactions to verify or deny referrals."""
        if user.bot:  # Ignore bot reactions
            return

        print(f"Reaction added by {user.name}: {reaction.emoji}")  # Debug

        # Ensure the message has an embed and matches the referral message
        if not reaction.message.embeds:
            print("No embed found.")
            return
        
        embed = reaction.message.embeds[0]
        if embed.title != "🚫 **New referral - Approval needed**":
            print("Embed title does not match.")
            return

        # Extract referral data
        referrer_ign = embed.fields[0].value.split("⠀- ")[1]
        referred_ign = embed.fields[1].value.split("⠀- ")[1]
        
        print(f"Processing referral: {referrer_ign} → {referred_ign}")  # Debug

        # Determine action based on reaction
        if reaction.emoji == "✅":
            status_text = f"✅ Verified by {user.display_name}"
            color = discord.Color.green()
            valid_status = 1
        elif reaction.emoji == "❌":
            status_text = f"❌ Denied by {user.display_name}"
            color = discord.Color.red()
            valid_status = 0
        else:
            return  # Ignore other reactions

        message = reaction.message

        # **Step 1: Clear All Reactions Immediately**
        try:
            await reaction.message.clear_reactions()
            print("Reactions cleared.")  # Debug
        except Exception as e:
            print(f"Clear reactions error: {e}")

        # **Step 2: Re-register the reaction event to allow future changes**
        def check(reaction, user):
            return reaction.message.id == message.id and not user.bot  # Ensure it's the same message

        try:
            query = "UPDATE referrals SET valid = %s, referred_since = NOW() WHERE referred_ign = %s"
            cursor = self.db.cursor()
            cursor.execute(query, (valid_status, referred_ign))
            self.db.commit()
            print("Database updated successfully.")  # Debug
        except Exception as e:
            print(f"Database update error: {e}")

        # **Step 3: Update Embed Message**
        try:
            new_embed = embed.copy()
            new_embed.title = status_text
            new_embed.color = color
            await reaction.message.edit(embed=new_embed)
            print("Message edited successfully.")  # Debug
            # Add option to change decision
        except Exception as e:
            print(f"Message edit error: {e}")

    @commands.command(name="refer_admin")
    async def refer_admin(self, ctx, referrer_ign: str = None, referred_ign: str = None):
        """Refer a player to the server."""
        # Permissions required to use
        required_role = "FG_Admin"
        member = ctx.author
        
        # Check if player has the permissions to proceed
        if discord.utils.get(member.roles, name=required_role):
            print(f"{member.display_name} has the {required_role} role!")
        else:
            await ctx.send(f"{member.display_name} does not have the {required_role} role!")
            return

        if not referred_ign:
            await ctx.send("❌ Incorrect usage \n\n **Usage:** `!refer_admin <REFERRER> <REFERRED>`\n Example: `!refer Steve Alex`")
            return

        if not referrer_ign:
            await ctx.send("❌ Incorrect usage \n\n **Usage:** `!refer_admin <REFERRER> <REFERRED>`\n Example: `!refer Steve Alex`")
            return

        # Normalize the input to handle possible emojis or extra characters
        normalized_referrer_ign = referrer_ign.lower().strip("🔱🛡️⚜️⭐🌟📃👑")  # Adjust for other emojis if needed
        normalized_referred_ign = referred_ign.lower().strip("🔱🛡️⚜️⭐🌟📃👑")

        # Find the referrer by name or display_name
        referrer_member = discord.utils.find(
            lambda m: m.name.lower() == normalized_referrer_ign or m.display_name.lower() == normalized_referrer_ign,
            ctx.guild.members
        )
        # Find the referred player by name or display_name
        referred_member = discord.utils.find(
            lambda m: m.name.lower() == normalized_referred_ign or m.display_name.lower() == normalized_referred_ign,
            ctx.guild.members
        )



        print("PRINT 1 \n")
        print("REFERRER: ", referrer_ign)
        print("REFERRED: ", referred_ign)
        print("REFERRER MEMBER: ", referrer_member)
        print("REFERRED MEMBER: ", referred_member)


        if not referrer_member:
            await ctx.send(f"❌ Referrer `{referrer_ign}` not found in the guild.")
            return

        if not referred_member:
            await ctx.send(f"❌ Referred player `{referred_ign}` not found in the guild.")
            return



        # Get the Discord IDs for both users
        referrer_id = referrer_member.id
        referred_id = referred_member.id

        # Check if the referred player is already in the server

        response = requests.get(f"https://api.wynncraft.com/v3/player/{referred_ign}")
        referred = response.json()
        playtime = referred.get("playtime", 0)
        
        if response.status_code != 200:
            return await ctx.send(f"❌ Failed to fetch player data for `{referred_ign}`. Try again later.")

        print("PRINT 2 \n")
        print("REFERRER: ", referrer_ign)
        print("REFERRED: ", referred_ign)

        query = """
        INSERT INTO referrals (referrer_ign, referrer_id, referred_ign, referred_id, logged_at, referred_since, last_activity, valid, hours)
        VALUES (%s, %s, %s, %s, NOW(), NOW(), NULL, TRUE, %s)
        """
        values = (referrer_ign, referrer_id, referred_ign, referred_id, playtime)

        try:
            cursor = self.db.cursor()
            cursor.execute(query, values)
            self.db.commit()
            await ctx.send(f"✅ Referral created \n\n {referred_ign} has been referred by {referrer_ign}, and **has been verified.**.")
        except mysql.connector.Error as e:
            await ctx.send(f"❌ Error adding referral: {e}")



    @commands.command(name="referal_list")
    async def referal_list(self, ctx):
        required_role = "FlameKnight"
        member = ctx.author

        if not discord.utils.get(member.roles, name=required_role):
            await ctx.send(f"❌ {member.display_name} does not have the `{required_role}` role!")
            return

        if not self.db:
            return await ctx.send("❌ Database connection is unavailable.")

        query = "SELECT id, referrer_ign, referred_ign, logged_at, valid FROM referrals"

        try:
            cursor = self.db.cursor()
            cursor.execute(query)
            referrals = cursor.fetchall()
            cursor.close()

            if not referrals:
                await ctx.send("📜 No referrals found.")
                return

            # 📜 Simple Test Embed
            embed = discord.Embed(
                title="📜 Referral List",
                description="List of all referrals in the database. \n",
                color=discord.Color.blue()
            )
            referral_text = ""

            for row in referrals[:10]:  # Limit to avoid issues
                ref_id, referrer, referred, logged_at, valid = row
                logged_at = logged_at.strftime("%Y-%m-%d %H:%M") if logged_at else "N/A"
                verified = "✅" if valid else "❌"

                # Append each referral with clear spacing
                referral_text += (
                    f"⠀⠀⠀⠀⠀⠀⠀\n" 
                    f"**#️⃣ Referral #{ref_id}**\n"
                    f"👤 Recruiter: **{referrer}**\n"
                    f"👥 New Member: **{referred}**\n"
                    f"🕒 Logged: **{logged_at}**\n"
                    f"📝 Verified: **{verified}**\n"
                    f"⠀⠀⠀⠀⠀⠀⠀\n" 
                )

            # Add final text as a single field
            embed.add_field(name="", value=referral_text, inline=False)

            await ctx.send(embed=embed)  # ✅ Test if Embed Sends
        except mysql.connector.Error as e:
            await ctx.send(f"❌ Database error: {e}")

    def update_referral_data(self, referred_player, new_data):
            """Updates referral data in the database or in-memory store."""
            
            if not self.db:
                print("❌ Database connection is unavailable.")
                return

            query = """
                UPDATE referrals
                SET hours_now = %s
                WHERE referred_id = %s
            """
            values = (new_data['hours_played'], referred_player)

            try:
                cursor = self.db.cursor()
                cursor.execute(query, values)
                self.db.commit()
                print(f"✅ Referral data updated for {referred_player}.")
            except mysql.connector.Error as e:
                print(f"❌ Error updating referral data: {e}")

    @commands.command(name="update_referral")
    async def update_referral(self, ctx, referred_ign: str):
        """Updates referral data for a player"""
        required_role = "FG_Admin"
        member = ctx.author

        if not discord.utils.get(member.roles, name=required_role):
            await ctx.send(f"❌ {member.display_name} does not have the `{required_role}` role!")
            return
        
        self.update_referral_data()
        await ctx.send(f"✅ Referral data has been manually updated for all players.")

    @commands.command(name="verify")
    async def verify(self, ctx, referred_ign: str):
        """Verify a referral"""
        required_role = "FG_Admin"
        member = ctx.author

        # Check if player has the permissions to proceed
        if discord.utils.get(member.roles, name=required_role):
            print(f"{member.display_name} has the {required_role} role!")
        else:
            await ctx.send(f"{member.display_name} does not have the {required_role} role!")
            return

        if not self.db:
            return await ctx.send("❌ Database connection is unavailable.")

        # Normalize the referred_ign (to avoid case and extra spaces issues)
        referred_ign = referred_ign.lower().strip()
        
        if not referred_ign:
            await ctx.send("❌ Incorrect usage \n\n **Usage:** `!verify <IGN>`\n Example: `!verify Steve`")
            return

        # Find the referred player by matching both name and display_name
        referred_member = discord.utils.find(lambda m: m.name.lower() == referred_ign or m.display_name.lower() == referred_ign, ctx.guild.members)
        if referred_ign.startswith("<@") and referred_ign.endswith(">"):
            mentioned_id = referred_ign.strip("<@!>")
            referred_member = ctx.guild.get_member(int(mentioned_id))
            if not referred_member:
                await ctx.send(f"❌ User with ID {mentioned_id} not found.")
                return
            if not referred_member:
                await ctx.send(f"❌ User with ID {mentioned_id} not found.")
                return
        
        if not referred_member:
            await ctx.send(f"❌ Player `{referred_ign}` not found in the guild.")
            return

        referred_id = referred_member.id
        
        # Adjust hours played based on the player's playtime
        response = requests.get("https://api.wynncraft.com/v3/player/" + referred_ign)
        referred_data = response.json()
        
        # Check if the player data was successfully retrieved
        if response.status_code != 200:
            await ctx.send(f"❌ Failed to fetch data for `{referred_ign}` from Wynncraft API.")
            return
        
        # Extract the playtime from the player data
        playtime = referred_data.get("playtime", 0)
        

        # Check if the entry is already verified
        query = "SELECT id, referrer_ign, referred_ign, logged_at, valid FROM referrals WHERE referred_id = %s"
        values = (referred_id,)

        cursor = self.db.cursor()
        cursor.execute(query, values)
        referral = cursor.fetchone()
        cursor.close()

        # If no referral entry is found, notify user
        if not referral:
            await ctx.send(f"❌ No referral entry found for `{referred_ign}`.")
            return

        # Check if already verified
        print(f"Current verification status: {referral[4]}")  # Log current verification status (1 or 0)
        if referral[4] == 1:  # `valid` is stored as 1 for verified
            print("PLAYTIME: ", playtime)
            await ctx.send(f"✅ `{referred_ign}` is already verified!")
            update_query = "UPDATE referrals SET hours_now = %s WHERE valid = 1"    
            cursor = self.db.cursor()
            cursor.execute(update_query, (playtime,))
            self.db.commit()
            cursor.close()        
            return
        # Update hours for all valid players
        

        # Proceed to verify the referral
        update_query = "UPDATE referrals SET valid = 1, referred_since = NOW(), last_activity = NULL WHERE referred_id = %s"
        cursor = self.db.cursor()
        cursor.execute(update_query, (referred_id,))
        self.db.commit()
        cursor.close()

        await ctx.send(f"✅ Referral for player `{referred_ign}` has been successfully verified!")



# Register cog
async def setup(bot):
    await bot.add_cog(Referral(bot))
