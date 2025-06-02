# A Great Chaos

import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from dotenv import load_dotenv
import datetime

if os.name == 'nt':
    os.system('cls')
else:
    os.system('clear')

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    print("INVALID TOKEN")
    exit()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
SERVER_ID_STR = os.getenv('DISCORD_SERVER')
SERVER_ID = int(SERVER_ID_STR) if SERVER_ID_STR and SERVER_ID_STR.isdigit() else None

if not SERVER_ID:
    print("INVALID SERVER ID FROM ENV VAR")
    exit()


# ON READY EVENT

@bot.event
async def on_ready():
    if not hasattr(bot, 'start_time'):
        bot.start_time = datetime.datetime.now(datetime.timezone.utc) # type: ignore

    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

    bot_identity_line = f'{bot.user.name} $ {bot.user.id}' #type: ignore

    print(bot_identity_line)
    print()
    print('SUCCESS')

    await asyncio.sleep(2)

    try:
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
        print(bot_identity_line)
        print()
        print('SYNCING COMMANDS')
        guild_object = discord.Object(id=SERVER_ID) #type: ignore
        synced = await bot.tree.sync(guild=guild_object)
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
        print(bot_identity_line)
        print()
        print(f'SYNCED {len(synced)} COMMANDS TO GUILD {SERVER_ID}')
    except Exception as e:
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
        print(bot_identity_line)
        print()
        print(f'ERROR SYNCING COMMANDS: {e}')

    await asyncio.sleep(2)

    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

    print(f'{bot_identity_line} ONLINE')

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

bot.run(TOKEN)