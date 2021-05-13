from dotenv import load_dotenv
from discord.ext import commands, tasks
import asyncio
import discord
import google_doc
import utils
import os
load_dotenv()

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())
token = os.getenv("DISCORD_BOT_TOKEN")


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="you"))
    print("Listening to commands...")


@client.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong with {str(round(client.latency, 2))}")


@client.command()
async def clear(ctx, amount=20):
    await ctx.channel.purge(limit=amount)


@client.command()
async def times(ctx, name="availability"):
    df = google_doc.request_GoogleDocRecords()
    embed = utils.embeds.createTimeTable(df)
    await ctx.send(f"Aktuell eingetragene Zeiten für die Raidwoche ({df['Datum'].min():%d.%m.%Y}-{df['Datum'].max():%d.%m.%Y})\n")
    await ctx.send(embed=embed)


@tasks.loop(hours=168.0)  # 168 hours = 1 week
async def send_weekly_report():
    df = google_doc.request_GoogleDocRecords()
    available_days = google_doc.calculate_available_days(df)
    embed = utils.embeds.createTimeTable(df)

    # Create and send message
    message_string = ""
    for index, data in available_days.iterrows():
        message_string += f'{data["Wochentag"]}({data["Datum"]:%d.%m.%Y}) von {int(data["start_time"])}Uhr bis {int(data["end_time"])}Uhr\n'

    for user_id in [356526822906920963]:
        username = str(client.get_user(356526822906920963)).split("#")[0]
        await client.get_user(user_id).send(f"Guten Abend {username}! Hier finden Sie die aktuelle Übersicht der eingetragenen Zeiten für die kommende Woche:")
        await client.get_user(user_id).send(embed=embed)
        await client.get_user(user_id).send("Ich habe mir die Freiheit genommen und Ihnen bereits die möglichen Raidtage herausgesucht. Aktuell stehen folgende Optionen zur Verfügung:\n\n" +
                                            message_string)


@send_weekly_report.before_loop
async def before_weekly():
    await client.wait_until_ready()
    delta = utils.calculate_timedelta(6, 18, 0)   # Sunday 18:00 -> (6, 18, 0)
    print(f"Starting weekly report cycle in {delta} seconds.")
    await asyncio.sleep(delta)
    print("Starting weekly report cycle.")

send_weekly_report.start()
client.run(token)
