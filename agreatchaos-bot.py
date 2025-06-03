# A Great Chaos

import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from dotenv import load_dotenv
import datetime

import valo_api
from valo_api.exceptions.valo_api_exception import ValoAPIException

if os.name == 'nt':
    os.system('cls')
else:
    os.system('clear')

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    print("INVALID TOKEN")
    exit()

HENRIKDEV_API_KEY = os.getenv('HENRIKDEV_API_KEY')
if not HENRIKDEV_API_KEY:
    print("HENRIKDEV_API_KEY NOT FIND .env. COMMAND /valorant_stats WILL NOT WORK")
else:
    try:
        valo_api.set_api_key(HENRIKDEV_API_KEY)
    except AttributeError:
        try:
            from valo_api.config import Config as ValoConfig
            ValoConfig.api_key = HENRIKDEV_API_KEY #type: ignore
        except ImportError:
            print("IMPORT ERROR valo_api.config.Config TO SET API KEY")
        except Exception as e_conf:
            print(f"API KEY CONFIGURE ERROR TO valo_api: {e_conf}")
    except Exception as e_set_key:
        print(f"CALL ERROR ON valo_api.set_api_key: {e_set_key}")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
SERVER_ID_STR = os.getenv('DISCORD_SERVER')
SERVER_ID = int(SERVER_ID_STR) if SERVER_ID_STR and SERVER_ID_STR.isdigit() else None

if not SERVER_ID:
    print("INVALID SERVER ID FROM .env VAR")
    exit()


# on ready

@bot.event
async def on_ready():
    if not hasattr(bot, 'start_time'):
        bot.start_time = datetime.datetime.now(datetime.timezone.utc) # type: ignore

    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

    bot_identity_line = f'{bot.user.name} $ {bot.user.id}' #type: ignore

    print(f'{bot_identity_line} SUCCESS')

    await asyncio.sleep(2)

    try:
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
        print(f'{bot_identity_line} SYNCING COMMANDS')
        guild_object = discord.Object(id=SERVER_ID) #type: ignore
        synced = await bot.tree.sync(guild=guild_object)
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
        print(f'{bot_identity_line} SYNCED {len(synced)} COMMANDS TO SERVER {SERVER_ID}')
    except Exception as e:
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
        print(f'{bot_identity_line} ERROR SYNCING COMMANDS: {e}')

    await asyncio.sleep(2)

    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

    print(bot_identity_line)

    try:
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
        activity = discord.Activity(type=discord.ActivityType.listening, name="A Great Chaos")
        await bot.change_presence(status=discord.Status.online, activity=activity)
        print(f'{bot_identity_line} RICH PRESENCE SET TO {activity.name}')
    except Exception as e:
        print(f'{bot_identity_line} ERROR RICH PRESENCE: {e}')

    await asyncio.sleep(1)

    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

    print(f'{bot_identity_line} ONLINE')

# /ping command

@bot.tree.command(
    name='ping',
    description='CHECK BOT LATENCY',
    guild=discord.Object(id=SERVER_ID) #type: ignore
)
async def command_ping(interaction: discord.Interaction):
    try:
        await interaction.response.send_message(f'{round(bot.latency * 1000)}ms LATENCY', ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send('ERROR: BOT NOT ALLOWED TO SEND MESSAGES IN THIS CHANNEL', ephemeral=True)
    except Exception as e:
        print(f'$ ERROR COMMAND /ping: {e}')
        if not interaction.response.is_done():
            await interaction.response.send_message('UNEXPECTED REQUEST PROCESS ERROR', ephemeral=True)
        else:
            await interaction.followup.send('UNEXPECTED REQUEST PROCESS ERROR', ephemeral=True)
@command_ping.error
async def on_ping_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandNotFound):
        await interaction.response.send_message('COMMAND NOT FOUND', ephemeral=True)
    elif isinstance(error, app_commands.CommandInvokeError) and isinstance(error.original, discord.Forbidden):
        await interaction.response.send_message('ALLOWED TO RECEIVE THE COMMAND, BUT NOT ALLOWED TO SEND MESSAGES IN THIS CHANNEL', ephemeral=True)
    else:
        if not interaction.response.is_done():
            await interaction.response.send_message('COMMAND NOT PROCESSED, FAIL', ephemeral=True)
        else:
            await interaction.followup.send('ADDITIONAL COMMAND NOT PROCESSED, FAIL', ephemeral=True)
        print(f'$ ERROR COMMAND /ping OR PROCESSOR: {error}')

# /msg command

@bot.tree.command(
    name='msg',
    description='BOT SEND A MESSAGE TO A CHANNEL (ADMIN ONLY)',
    guild=discord.Object(id=SERVER_ID)
)
@app_commands.describe(
    message='THE MESSAGE TO SEND',
)
@app_commands.checks.has_permissions(administrator=True)
async def received_message(
    interaction: discord.Interaction,
    message: str
):
    try:
        await interaction.response.send_message(f'OK', ephemeral=True)
        if interaction.channel:
            await interaction.channel.send(message) #type: ignore
        else:
            await interaction.followup.send('ERROR: CHANNEL NOT FOUND', ephemeral=True)
    except discord.Forbidden:
        try:
            await interaction.followup.send('ERROR: BOT NOT ALLOWED TO SEND MESSAGES IN THIS CHANNEL', ephemeral=True)
        except Exception as e:
            print(f'$ ERROR FOLLOWUP: {e}')
    except Exception as e:
        print(f'$ ERROR COMMAND /msg: {e}')
        try:
            if interaction.response.is_done():
                await interaction.followup.send(f'UNEXPECTED REQUEST PROCESS ERROR', ephemeral=True)
            else:
                await interaction.response.send_message(f'REQUEST PROCESS ERROR', ephemeral=True)
        except Exception as final_e:
            print(f'$ NOTIFY ERROR UNEXPECTED RESPONSE COMMAND: {final_e}')

@received_message.error
async def on_msg_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message('NOT PERMISSION ALLOWED', ephemeral=True)
    elif isinstance(error, app_commands.CommandInvokeError) and isinstance(error.original, discord.Forbidden):
        await interaction.response.send_message('ALLOWED TO RECEIVE THE COMMAND, BUT NOT ALLOWED TO SEND MESSAGES IN THIS CHANNEL', ephemeral=True)
    else:
        if not interaction.response.is_done():
            await interaction.response.send_message('COMMAND NOT PROCESSED, FAIL', ephemeral=True)
        else:
            await interaction.followup.send('ADDITIONAL COMMAND NOT PROCESSED, FAIL', ephemeral=True)
        print(f'$ ERROR COMMAND /msg OR PROCESSOR: {error}')

# /send_file command

@bot.tree.command(
    name='send_file',
    description='BOT SEND A MEDIA/FILE TO A CHANNEL (ADMIN ONLY)',
    guild=discord.Object(id=SERVER_ID) #type: ignore
)
@app_commands.describe(
    file='THE FILE TO SEND (MAX 8MB)',
    optional_message='THE MESSAGE TO SEND WITH THE FILE (OPTIONAL, MAX 2000 CHARACTERS)'
)
@app_commands.checks.has_permissions(administrator=True)
async def command_send_file(
    interaction: discord.Interaction,
    file: discord.Attachment,
    optional_message: str = None #type: ignore
):
    try:
        await interaction.response.send_message('OK',ephemeral=True)

        file_to_send = await file.to_file()

        if interaction.channel:
            if optional_message:
                await interaction.channel.send(content=optional_message, file=file_to_send) #type: ignore
            else:
                await interaction.channel.send(file=file_to_send) #type: ignore
        else:
            await interaction.followup.send('ERROR: CHANNEL NOT FOUND', ephemeral=True)

    except discord.Forbidden:
        await interaction.followup.send(
            'ERROR: BOT NOT ALLOWED TO SEND MESSAGES IN THIS CHANNEL',
            ephemeral=True
        )
    except Exception as e:
        print(f'$ ERROR COMMAND /send_file: {e}')
        await interaction.followup.send(
            'UNEXPECTED SEND FILE ERROR',
            ephemeral=True
        )

# /clear command

@bot.tree.command(
    name="clear",
    description="BOT CLEAR CHAT CHANNEL (ADMIN ONLY)",
    guild=discord.Object(id=SERVER_ID)
)
@app_commands.describe(
    quantidade="1 TO 100 MESSAGES TO DELETE (DEFAULT 5)",
)
@app_commands.checks.has_permissions(administrator=True)
async def command_clear(
    interaction: discord.Interaction,
    quantidade: app_commands.Range[int, 1, 100] = 5
):
    await interaction.response.defer(ephemeral=True, thinking=True)

    if not isinstance(interaction.channel, (discord.TextChannel, discord.Thread, discord.VoiceChannel)):
        await interaction.followup.send(
            "THIS COMMAND CAN ONLY BE USED IN TEXT CHANNELS OR THREADS",
            ephemeral=True
        )
        return

    try:
        cleared_messages = await interaction.channel.purge(limit=quantidade)
        
        await interaction.followup.send(
            f"{len(cleared_messages)} MESSAGES DELETED {interaction.user.mention}",
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.followup.send(
            "BOT DOESNT HAVE PERMISSION TO DELETE MESSAGES IN THIS CHANNEL",
            ephemeral=True
        )
    except discord.HTTPException as e:
        await interaction.followup.send(
            f"ERROR OCCURRED ON CLEAR MESSAGES: {e}",
            ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(
            f"UNEXPECTED ERROR: {e}",
            ephemeral=True
        )
        print(f"$ UNEXPECTED ERROR ON COMMAND /clear: {e}")

@command_clear.error
async def on_clear_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "ONLY ADMINS CAN USE THIS COMMAND",
            ephemeral=True
        )
    elif isinstance(error, app_commands.CommandNotFound):
         await interaction.response.send_message("COMMAND NOT FOUND", ephemeral=True)
    else:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "ERROR PROCESSING COMMAND /clear",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                "ERROR PROCESSING COMMAND /clear",
                ephemeral=True
            )
        print(f"$ ERROR PROCESSING COMMAND /clear (BEFORE EXECUTE): {error}")

# /uptime command

@bot.tree.command(
    name="uptime",
    description="SHOW BOT TIME ONLINE",
    guild=discord.Object(id=SERVER_ID)
)
async def comando_uptime(interaction: discord.Interaction):
    if not hasattr(bot, 'start_time'):
        await interaction.response.send_message(
            "TIME ONLINE NOT AVAILABLE YET",
            ephemeral=True
        )
        return

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    duration = now_utc - bot.start_time #type: ignore

    total_seconds = int(duration.total_seconds())

    days = total_seconds // (24 * 3600)
    remanescent_seconds_after_days = total_seconds % (24 * 3600)
    hours = remanescent_seconds_after_days // 3600
    remanescent_seconds_after_hours = remanescent_seconds_after_days % 3600
    minutes = remanescent_seconds_after_hours // 60
    seconds = remanescent_seconds_after_hours % 60

    parts_uptime = []
    if days > 0:
        parts_uptime.append(f"{days} DAY{'S' if days != 1 else ''}")
    if hours > 0:
        parts_uptime.append(f"{hours} HOUR{'S' if hours != 1 else ''}")
    if minutes > 0:
        parts_uptime.append(f"{minutes} MINUTE{'S' if minutes != 1 else ''}")
    
    if seconds >= 0 and not parts_uptime: 
        parts_uptime.append(f"{seconds} SECOND{'S' if seconds != 1 else ''}")
    elif seconds > 0 : 
         parts_uptime.append(f"{seconds} SECOND{'S' if seconds != 1 else ''}")


    if not parts_uptime: 
        uptime_string = "I'M ONLINE FOR LESS THAN A SECOND"
    elif len(parts_uptime) == 1:
        uptime_string = f"ONLINE HAS {parts_uptime[0]}."
    else:
        last_part = parts_uptime.pop()
        uptime_string = "ONLINE HAS " + ", ".join(parts_uptime) + f" AND {last_part}"

    await interaction.response.send_message(uptime_string, ephemeral=True)

@command_send_file.error
async def on_send_file_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message('NOT PERMISSION ALLOWED', ephemeral=True)
    else:
        if not interaction.response.is_done():
            await interaction.response.send_message('COMMAND FILE NOT PROCESSED, FAIL', ephemeral=True)
        else:
            await interaction.followup.send('COMMAND FILE NOT PROCESSED, FAIL', ephemeral=True)
        print(f'$ ERROR COMMAND /send_file OR PROCESSOR: {error}')

# /serverinfo command
@bot.tree.command(
    name="serverinfo",
    description="SHOW SERVER DETAILS",
    guild=discord.Object(id=SERVER_ID)
)
async def command_serverinfo(interaction: discord.Interaction):
    guild = interaction.guild

    if guild is None: # Adicionado um check extra, embora improvável para guild-specific command
        await interaction.response.send_message("THIS COMMAND CAN ONLY BE USED IN A SERVER", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"SERVER INFORMATION",
        description=f"DETAILS ABOUT **{guild.name.upper()}**:",
        color=discord.Color.from_rgb(0, 0, 0)
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(name="SERVER NAME", value=guild.name, inline=True)
    embed.add_field(name="SERVER ID", value=str(guild.id), inline=True)
    
    owner = guild.owner
    if owner:
        embed.add_field(name="OWNER", value=f"{owner.mention} ({owner.display_name})", inline=True)
    else:
        embed.add_field(name="OWNER ID", value=str(guild.owner_id), inline=True)

    embed.add_field(name="CREATION DATE", value=f"<t:{int(guild.created_at.timestamp())}:D> (<t:{int(guild.created_at.timestamp())}:R>)", inline=False)
    embed.add_field(name="TOTAL MEMBERS", value=str(guild.member_count), inline=True)
    
    embed.add_field(name="TEXT CHANNELS", value=str(len(guild.text_channels)), inline=True)
    embed.add_field(name="VOICE CHANNELS", value=str(len(guild.voice_channels)), inline=True)
    embed.add_field(name="CATEGORIES", value=str(len(guild.categories)), inline=True)
    embed.add_field(name="ROLES", value=str(len(guild.roles) -1), inline=True) 

    embed.add_field(name="BOOST LEVEL", value=f"LEVEL {guild.premium_tier}", inline=True)
    embed.add_field(name="BOOSTS COUNT", value=str(guild.premium_subscription_count), inline=True)
    
    verification_level_map = {
        discord.VerificationLevel.none: "NONE",
        discord.VerificationLevel.low: "LOW (VERIFIED EMAIL)",
        discord.VerificationLevel.medium: "MEDIUM (REGISTERED ON DISCORD >5 MIN)",
        discord.VerificationLevel.high: "HIGH (MEMBER OF SERVER >10 MIN)",
        discord.VerificationLevel.highest: "HIGHEST (VERIFIED PHONE)"
    }
    embed.add_field(name="VERIFICATION LEVEL", value=verification_level_map.get(guild.verification_level, str(guild.verification_level).upper()), inline=False)

    if guild.description:
        embed.add_field(name="SERVER DESCRIPTION", value=guild.description, inline=False)

    if guild.vanity_url_code:
        embed.add_field(name="VANITY URL", value=f"discord.gg/{guild.vanity_url_code}", inline=False)
    
    features_str = ""
    if guild.features:
        features_list = [feature.replace("_", " ").upper() for feature in guild.features]
        if features_list:
            features_str = ", ".join(features_list)
    
    if features_str: # Só adiciona o campo se houver features formatadas
        embed.add_field(name="SERVER FEATURES", value=features_str if len(features_str) <= 1024 else features_str[:1020] + "...", inline=False)


    embed.set_footer(text=f"REQUESTED BY: {interaction.user.display_name.upper()}", icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None)
    embed.timestamp = datetime.datetime.now(datetime.timezone.utc)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# /valorant_stats command

@bot.tree.command(
    name='valorant_stats',
    description='SHOW VALORANT PLAYER RANK',
    guild=discord.Object(id=SERVER_ID)
)
@app_commands.describe(
    name='VALORANT NICKNAME WITHOUT TAG',
    tag='VALORANT TAG (BR1, VALO without #)',
    region_input='REGION (br, na, eu, ap, kr, latam, es)'
)
async def comando_valorant_stats(interaction: discord.Interaction, name: str, tag: str, region_input: str):
    region = region_input.lower()
    valid_regions = ['br', 'na', 'eu', 'ap', 'kr', 'latam', 'es']
    if region not in valid_regions:
        await interaction.response.send_message(
            f"INVALID REGION, USE ONE OF THEM: {', '.join(valid_regions)}.",
            ephemeral=True
        )
        return

    if not HENRIKDEV_API_KEY:
        await interaction.response.send_message("API KEY FOR VALORANT STATS NOT CONFIGURED", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=False)

    name_api = name.replace(' ', '')
    tag_api = tag

    try:
        mmr_details = await valo_api.get_mmr_details_by_name_v2_async( #type: ignore
            name=name_api,
            tag=tag_api,
            region=region
        )

        name_jogador_api = getattr(mmr_details, 'name', name)
        tag_jogador_api = getattr(mmr_details, 'tag', tag)
        
        current_data = getattr(mmr_details, 'current_data', None)

        rank_now = "NOT RANKED"
        elo = 0
        mmr_last_match = 0
        image_rank_url = None

        if current_data:
            rank_now = getattr(current_data, 'currenttierpatched', "NOT RANKED")
            elo = getattr(current_data, 'elo', 0)
            mmr_last_match = getattr(current_data, 'mmr_change_to_last_game', 0)
            images_data = getattr(current_data, 'images', None)
            if images_data:
                image_rank_url = getattr(images_data, 'small', None)
        
        embed = discord.Embed(
            title=f'VALORANT RANK TO {name_jogador_api}#{tag_jogador_api} ({region.upper()})',
            color=discord.Color.from_rgb(0, 0, 0)
        )
        embed.add_field(name="RANK NOW", value=rank_now, inline=True)
        embed.add_field(name="ELO (Rank Points)", value=str(elo), inline=True)
        if isinstance(mmr_last_match, int) and mmr_last_match != 0:
            embed.add_field(name="MMR LAST MATCH", value=f"{mmr_last_match:+} points", inline=True)

        if image_rank_url:
            embed.set_thumbnail(url=image_rank_url)
        else:
            embed.set_footer(text="IMAGE RANK NOT AVAILABLE")

        await interaction.followup.send(embed=embed)

    except ValoAPIException as e:
        error_message = f"VALORANT API ERROR: {str(e)}"
        status_code = getattr(e, 'status_code', None) 

        if status_code == 404:
            error_message = f"PLAYER {name}#{tag} ON REGION {region} NOT FOUND"
        elif status_code == 429:
            error_message = "LOT REQUESTS API. TRY LATER"
        elif status_code == 403:
            error_message = "DENIED ACCESS API. VERIFY API KEY OR PERMISSIONS"
        elif status_code == 400:
            error_message = "REQUEST BAD FORMATTED API. VERIFY NAME, TAG AND REGION"
        
        await interaction.followup.send(error_message, ephemeral=True)
        print(f"$ ERROR COMMAND /valorant_stats OR PROCESSOR: {str(e)}")
    except AttributeError as e:
        print(f"$ ERROR ATRIBUTTE COMMAND /valorant_stats (verify name function or API request): {e}")
        await interaction.followup.send('UNEXPECTED ERROR ON ACCESS API DATA. API FUNCTION COULD BE CHANGED', ephemeral=True)
    except Exception as e:
        print(f"$ UNEXPECTED ERROR ON COMMAND /valorant_stats: {type(e).__name__} - {e}")
        await interaction.followup.send('UNEXPECTED ERROR ON PROCESS REQUEST STATS', ephemeral=True)

@comando_valorant_stats.error
async def on_valorant_stats_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandInvokeError) and isinstance(error.original, discord.Forbidden):
        await interaction.followup.send('BOT DOESN`T HAVE PERMISSION TO SEND FOLLOWUP MESSAGES HERE', ephemeral=True)
    else:
        if not interaction.response.is_done():
            try:
                await interaction.response.send_message('ERROR COMMAND /valorant_stats OR PROCESSOR', ephemeral=True)
            except discord.InteractionResponded:
                await interaction.followup.send('ERROR COMMAND /valorant_stats OR PROCESSOR (followup).', ephemeral=True)
        else:
            await interaction.followup.send('ERROR COMMAND /valorant_stats OR PROCESSOR', ephemeral=True)
        print(f'$ ERROR PROCESSING COMMAND /valorant_stats: {error}')

# /userinfo command

@bot.tree.command(
    name="userinfo",
    description="SHOWS INFORMATION ABOUT A SERVER MEMBER.",
    guild=discord.Object(id=SERVER_ID)
)
@app_commands.describe(
    membro="THE MEMBER YOU WANT TO GET INFO ABOUT."
)
async def comando_userinfo(interaction: discord.Interaction, membro: discord.Member):
    embed = discord.Embed(
        title=f"USER INFORMATION: {membro.display_name.upper()}",
        color=membro.color if membro.color != discord.Color.default() else discord.Color.blue()
    )
    if membro.display_avatar:
        embed.set_thumbnail(url=membro.display_avatar.url)

    if membro.discriminator == "0":
        username_field = f"USERNAME: @{membro.name}"
    else:
        username_field = f"USERNAME: {membro.name}#{membro.discriminator}"
    
    embed.add_field(name="USER TAG", value=str(membro), inline=True)
    embed.add_field(name="NICKNAME", value=membro.nick if membro.nick else "NONE", inline=True)
    embed.add_field(name="USER ID", value=str(membro.id), inline=True)

    embed.add_field(name="ACCOUNT CREATED", value=f"<t:{int(membro.created_at.timestamp())}:D> (<t:{int(membro.created_at.timestamp())}:R>)", inline=False)
    if membro.joined_at:
        embed.add_field(name="JOINED SERVER", value=f"<t:{int(membro.joined_at.timestamp())}:D> (<t:{int(membro.joined_at.timestamp())}:R>)", inline=False)

    roles = [role.mention for role in reversed(membro.roles) if not role.is_default()]
    
    if roles:
        roles_display_limit = 7
        roles_str = ", ".join(roles[:roles_display_limit])
        if len(roles) > roles_display_limit:
            roles_str += f" AND {len(roles) - roles_display_limit} MORE..."
        embed.add_field(name=f"ROLES ({len(roles)})", value=roles_str if roles_str else "NO SPECIFIC ROLES", inline=False)
    else:
        embed.add_field(name="ROLES", value="NO SPECIFIC ROLES", inline=False)

    if membro.top_role and not membro.top_role.is_default():
        embed.add_field(name="HIGHEST ROLE", value=membro.top_role.mention, inline=True)
    else:
        embed.add_field(name="HIGHEST ROLE", value="NONE", inline=True)
    
    status_map = {
        discord.Status.online: "ONLINE",
        discord.Status.idle: "IDLE",
        discord.Status.dnd: "DO NOT DISTURB",
        discord.Status.offline: "OFFLINE / INVISIBLE"
    }
    embed.add_field(name="STATUS", value=status_map.get(membro.status, str(membro.status).upper()), inline=True)

    if membro.activity:
        activity = membro.activity
        activity_type_str = ""
        activity_details = ""

        if activity.type == discord.ActivityType.playing:
            activity_type_str = "PLAYING"
            activity_details = activity.name
        elif activity.type == discord.ActivityType.streaming:
            activity_type_str = "STREAMING"
            activity_details = f"[{activity.name}]({activity.url})" #type: ignore
        elif activity.type == discord.ActivityType.listening:
            if isinstance(activity, discord.Spotify):
                activity_type_str = "LISTENING TO SPOTIFY"
                activity_details = f"{activity.title} BY {activity.artist}"
            else:
                activity_type_str = "LISTENING TO"
                activity_details = activity.name
        elif activity.type == discord.ActivityType.watching:
            activity_type_str = "WATCHING"
            activity_details = activity.name
        elif isinstance(activity, discord.CustomActivity):
             activity_type_str = "CUSTOM STATUS"
             activity_details = f"{activity.emoji if activity.emoji else ''} {activity.name if activity.name else ''}".strip()
             if not activity_details: activity_details = "NONE"
        
        if activity_type_str and activity_details:
             embed.add_field(name=f"ACTIVITY ({activity_type_str})", value=activity_details, inline=False)

    embed.set_footer(text=f"REQUESTED BY: {interaction.user.display_name.upper()}", icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None)
    embed.timestamp = datetime.datetime.now(datetime.timezone.utc)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@comando_userinfo.error
async def on_userinfo_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.TransformerError) or isinstance(error, app_commands.CommandInvokeError):
        error_message = "COULD NOT FETCH INFO FOR THIS USER OR AN UNEXPECTED ERROR OCCURRED."
    else:
        error_message = "AN ERROR OCCURRED WHILE PROCESSING THE COMMAND."

    print(f"$ ERROR ON COMMAND /userinfo: {error}")
    if not interaction.response.is_done():
        await interaction.response.send_message(error_message, ephemeral=True)
    else:
        await interaction.followup.send(error_message, ephemeral=True)

bot.run(TOKEN)