import os
import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# TerminalX999 - Standard License Key Discord Bot (Python)
# ==========================================
TOKEN    = os.getenv("BOT_TOKEN")
GUILD_IDS = [1549781771560685608]

API_URL  = "https://prtvshow.online/api_admin.php"
API_KEY  = "TX999_API_88d9a44fdc05493049f24dc831119d98"
APP_ID   = "9f087d585fbd666572fc24b7"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    for g_id in GUILD_IDS:
        try:
            guild = discord.Object(id=g_id)
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"Synced {len(synced)} slash commands to guild {g_id}.")
        except Exception as e:
            print(f"Failed to sync commands to guild {g_id}: {e}")

# ── Global Interaction Listener for Persistent UI Buttons ──
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get("custom_id", "")
        if ":" in custom_id:
            action, key = custom_id.split(":", 1)
            await interaction.response.defer(ephemeral=True)
            try:
                params = {"action": action, "api_key": API_KEY, "key": key}
                resp = requests.get(API_URL, params=params, timeout=10)
                data = resp.json()
                if data.get("success"):
                    await interaction.followup.send(f"✓ Action **{action}** completed for key: `{key}`", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ Failed: {data.get('message')}", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

# ── Command: Generate License Key ──
@bot.tree.command(name="genkey", description="Generate a license key remotely.")
@discord.app_commands.choices(package=[
         discord.app_commands.Choice(name="UID BYPASS", value="cb921031dc43197e8ccb6828")
    ])
@discord.app_commands.describe(
    package="Select the target package",
    days="Number of validity days (0 = lifetime)",
    count="Number of keys to generate (max 100)"
)
async def genkey(interaction: discord.Interaction, package: str, days: int = 30, count: int = 1):
    await interaction.response.defer(ephemeral=False)
    params = {"action": "generate_key", "api_key": API_KEY, "app_id": APP_ID, "package_id": package, "days": days, "count": count}
    try:
        resp = requests.get(API_URL, params=params, timeout=10)
        data = resp.json()
        if data.get("success"):
            keys = data.get("keys") or data.get("data", {}).get("keys", [])
            dur = "Lifetime" if days == 0 else f"{days} Days"
            embed = discord.Embed(title="🔑 Keys Generated", description=f"Generated {len(keys)} key(s)\nDuration: {dur}", color=0xdc2626)
            embed.add_field(name="Keys", value="\n".join([f"`{k}`" for k in keys]))
            view = discord.ui.View()
            if len(keys) == 1:
                view.add_item(discord.ui.Button(label="Reset HWID", custom_id=f"reset_hwid:{keys[0]}"))
                view.add_item(discord.ui.Button(label="Delete", custom_id=f"delete_key:{keys[0]}", style=discord.ButtonStyle.danger))
            await interaction.followup.send(embed=embed, view=view if len(keys)==1 else None)
        else:
            await interaction.followup.send(f"❌ {data.get('message')}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ {str(e)}", ephemeral=True)

bot.run(TOKEN)
