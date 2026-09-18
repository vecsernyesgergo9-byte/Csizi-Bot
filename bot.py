import os
import discord
from discord.ext import commands

# Discord jogosultságok / események
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Csizi-Bot elindult: {bot.user}")
    
    guild = discord.Object(id=1449737996436766802)
    synced = await bot.tree.sync(guild=guild)
    print(f"Szinkronizált parancsok: {len(synced)}")
    await bot.change_presence(
        activity=discord.Game(name="Csizi szerverét figyelem")
)


@bot.event
async def on_member_join(member):
    role = member.guild.get_role(1450270408464011417)

    if role:
        try:
            await member.add_roles(role, reason="Automatikus rangadás")
            print(f"Rang kiosztva: {member}")
        except discord.Forbidden:
            print("Nem tudom kiosztani a rangot: nincs megfelelő jogosultság.")
    # Megkeresi az „üdvözlő” nevű szöveges csatornát
    channel = member.guild.get_channel(1449737997686804603)

    if channel:
        embed = discord.Embed(
            title="Üdvözlünk!",
            description=f"Szia {member.mention}! Üdv a {member.guild.name} szerveren!"
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(
            name="Első lépések",
            value="Olvasd el a szabályzatot, és érezd jól magad!",
            inline=False
        )

        await channel.send(embed=embed)


@bot.event
async def on_member_remove(member):
    channel = member.guild.get_channel(1449737997686804603)

    if channel:
        embed = discord.Embed(
            title="👋 Egy tag kilépett",
            description=f"**{member.display_name}** elhagyta a szervert."
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        await channel.send(embed=embed)
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    log_channel = message.guild.get_channel(1550209636362227833)

    if log_channel:
        embed = discord.Embed(
            title="🗑️ Üzenet törölve",
            description=message.content or "Az üzenet nem tartalmazott szöveget."
        )

        embed.add_field(
            name="Felhasználó",
            value=message.author.mention,
            inline=False
        )

        embed.add_field(
            name="Csatorna",
            value=message.channel.mention,
            inline=False
        )

        await log_channel.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot:
        return

    if before.content == after.content:
        return

    log_channel = before.guild.get_channel(1550209636362227833)

    if log_channel:
        embed = discord.Embed(
            title="✏️ Üzenet szerkesztve"
        )

        embed.add_field(
            name="Felhasználó",
            value=before.author.mention,
            inline=False
        )

        embed.add_field(
            name="Eredeti üzenet",
            value=before.content or "Nem volt szöveg.",
            inline=False
        )

        embed.add_field(
            name="Új üzenet",
            value=after.content or "Nem volt szöveg.",
            inline=False
        )

        embed.add_field(
            name="Csatorna",
            value=before.channel.mention,
            inline=False
        )

        await log_channel.send(embed=embed)


@bot.event
async def on_member_update(before, after):
    if before.roles == after.roles:
        return

    log_channel = after.guild.get_channel(1550209636362227833)

    if not log_channel:
        return

    added_roles = [
        role for role in after.roles
        if role not in before.roles and role != after.guild.default_role
    ]

    removed_roles = [
        role for role in before.roles
        if role not in after.roles and role != after.guild.default_role
    ]

    if added_roles:
        roles = ", ".join(role.mention for role in added_roles)

        embed = discord.Embed(
            title="➕ Rang hozzáadva",
            description=f"{after.mention} új rangot kapott."
        )

        embed.add_field(
            name="Rang",
            value=roles,
            inline=False
        )

        await log_channel.send(embed=embed)

    if removed_roles:
        roles = ", ".join(role.name for role in removed_roles)

        embed = discord.Embed(
            title="➖ Rang eltávolítva",
            description=f"{after.mention} rangja eltávolításra került."
        )

        embed.add_field(
            name="Rang",
            value=roles,
            inline=False
        )

        await log_channel.send(embed=embed)
    
@bot.tree.command(name="ping", description="Ellenőrzi, hogy működik-e Csizi-Bot.")
@discord.app_commands.guilds(discord.Object(id=1449737996436766802))
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🏓 **Csizi-Bot jelentkezik!**\n"
        "A szerver működik. Én dolgozom. Fizetést továbbra sem láttam. 🥲"
    )
@bot.tree.command(name="serverinfo", description="Információkat mutat a szerverről.")
@discord.app_commands.guilds(discord.Object(id=1449737996436766802))
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild

    embed = discord.Embed(
        title=f"📊 {guild.name} – Szerverinfó",
        description="Minden fontos infó egy helyen."
    )

    embed.add_field(
        name="👥 Tagok",
        value=str(guild.member_count),
        inline=True
    )

    embed.add_field(
        name="💬 Csatornák",
        value=str(len(guild.channels)),
        inline=True
    )

    embed.add_field(
        name="🎭 Rangok",
        value=str(len(guild.roles) - 1),
        inline=True
    )

    embed.add_field(
        name="👑 Tulajdonos",
        value=guild.owner.mention if guild.owner else "Ismeretlen",
        inline=False
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    await interaction.response.send_message(embed=embed)
TOKEN = os.getenv("CSIZI_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "Nincs beállítva a CSIZI_BOT_TOKEN."
    )

class OtletGombok(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Elfogadás",
        style=discord.ButtonStyle.success,
        emoji="✅"
    )
    async def elfogadas(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        staff_role = interaction.guild.get_role(1449738506741088306)

        if staff_role not in interaction.user.roles:
            await interaction.response.send_message(
                "❌ Ezt a gombot csak a staff használhatja.",
                ephemeral=True
            )
            return

        embed = interaction.message.embeds[0]

        embed.add_field(
            name="Állapot",
            value=f"✅ Elfogadva – {interaction.user.mention}",
            inline=False
        )

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    @discord.ui.button(
        label="Elutasítás",
        style=discord.ButtonStyle.danger,
        emoji="❌"
    )
    async def elutasitas(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        staff_role = interaction.guild.get_role(1449738506741088306)

        if staff_role not in interaction.user.roles:
            await interaction.response.send_message(
                "❌ Ezt a gombot csak a staff használhatja.",
                ephemeral=True
            )
            return

        embed = interaction.message.embeds[0]

        embed.add_field(
            name="Állapot",
            value=f"❌ Elutasítva – {interaction.user.mention}",
            inline=False
        )

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )
@bot.tree.command(name="otlet", description="Küldj be egy ötletet a szerverhez.")
@discord.app_commands.guilds(discord.Object(id=1449737996436766802))
async def otlet(interaction: discord.Interaction, otlet: str):
    channel = interaction.guild.get_channel(1475072110182531163)

    if not channel:
        await interaction.response.send_message(
            "❌ Nem találom az ötletek csatornát.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="💡 Új ötlet",
        description=otlet
    )

    embed.add_field(
        name="Beküldte",
        value=interaction.user.mention,
        inline=False
    )

    message = await channel.send(embed=embed, view=OtletGombok())

    await message.add_reaction("👍")
    await message.add_reaction("👎")

    await interaction.response.send_message(
        "✅ Az ötletedet elküldtem!",
        ephemeral=True
    )
@bot.tree.command(name="inaktiv", description="Inaktivitás bejelentése.")
@discord.app_commands.guilds(discord.Object(id=1449737996436766802))
async def inaktiv(
    interaction: discord.Interaction,
mettol: str,
meddig: str,
indok: str
):
    channel = interaction.guild.get_channel(1491953050779389962)

    if not channel:
        await interaction.response.send_message(
            "❌ Nem találom az inaktivitás csatornát.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="💤 Inaktivitás bejelentés"
    )

    embed.add_field(
        name="👤 Tag",
        value=interaction.user.mention,
        inline=False
    )

    embed.add_field(
    name="📅 Mettől – meddig",
    value=f"{mettol} – {meddig}",
    inline=False
)
    )

    embed.add_field(
        name="📝 Indok",
        value=indok,
        inline=False
    )

    await channel.send(embed=embed)

    await interaction.response.send_message(
        "✅ Az inaktivitásodat elküldtem!",
        ephemeral=True
    )
bot.run(TOKEN)
