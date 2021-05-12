from dotenv import load_dotenv
from discord.ext import commands, tasks
import asyncio
import discord
import google_doc
import datetime
import os
load_dotenv()

client = commands.Bot(command_prefix=".", intents=discord.Intents.all())
token = os.getenv("DISCORD_BOT_TOKEN")

@client.event
async def on_ready() :
    await client.change_presence(status = discord.Status.online, activity = discord.Activity(type=discord.ActivityType.watching, name="you"))
    print("I am online")

@client.command()
async def ping(ctx) :
    await ctx.send(f"🏓 Pong with {str(round(client.latency, 2))}")

@client.command()
async def clear(ctx, amount=20) :
    await ctx.channel.purge(limit=amount)

@client.command()
async def times(ctx, name="availability") :
    await ctx.send("Ihr Wunsch sei mir Befehl...\n")
    gd = google_doc.GoogleDoc()
    gd.authorize_client()
    records = gd.open_by_url(os.getenv("DOC_LINK"))
    df = google_doc.handle_records(records)
    print(df.head())
    # Filter maybe?
    df = df[:7] 
    # -----------
    data_set = list(df.itertuples(index=False, name=None))
    embed = discord.Embed(title=f"__**Zeiten:**__", color=0x03f8fc)
    player = tuple(i for i in df.columns[1:])
    for cnt, day in enumerate(df["Wochentag"]):
        embed.add_field(name=f'**{day}**', value=f'{player[1]}:  {data_set[cnt][2]}' +
        f'\n {player[2]}:  {data_set[cnt][3]}' +
        f'\n {player[3]}:  {data_set[cnt][4]}' +
        f'\n {player[4]}:  {data_set[cnt][5]}' +
        f'\n {player[5]}:  {data_set[cnt][6]}' +
        f'\n {player[6]}:  {data_set[cnt][7]}' +
        f'\n {player[7]}:  {data_set[cnt][8]}' +
        f'\n {player[8]}:  {data_set[cnt][9]}\n ', inline=True)
    
    await ctx.send(embed=embed)


@tasks.loop(hours=168.0)
async def weekly_report():
    # Get Google document
    gd = google_doc.GoogleDoc()
    gd.authorize_client()
    records = gd.open_by_url(os.getenv("DOC_LINK"))
    df = google_doc.handle_records(records)
    df = df[:7]
    # Calculate available days
    available_days = google_doc.calculate_available_days(df)

    # Create time table
    data_set = list(df.itertuples(index=False, name=None))
    embed = discord.Embed(title=f"__**Zeiten:**__", color=0x03f8fc)
    player = tuple(i for i in df.columns[1:])
    for cnt, day in enumerate(df["Wochentag"]):
        embed.add_field(name=f'**{day}**', value=f'{player[1]}:  {data_set[cnt][2]}' +
        f'\n {player[2]}:  {data_set[cnt][3]}' +
        f'\n {player[3]}:  {data_set[cnt][4]}' +
        f'\n {player[4]}:  {data_set[cnt][5]}' +
        f'\n {player[5]}:  {data_set[cnt][6]}' +
        f'\n {player[6]}:  {data_set[cnt][7]}' +
        f'\n {player[7]}:  {data_set[cnt][8]}' +
        f'\n {player[8]}:  {data_set[cnt][9]}\n ', inline=True)

    # Create and send message
    message_string = ""
    for index, data in available_days.iterrows():
        message_string += f'{data["Wochentag"]}({data["Datum"]}) von {int(data["start_time"])}Uhr bis {int(data["end_time"])}Uhr\n'
    print(message_string)

    await client.get_user(356526822906920963).send("Guten Abend Sir! Hier finden Sie die aktuelle Übersicht der eingetragenen Zeiten für die kommende Woche:")
    await client.get_user(356526822906920963).send(embed=embed)
    await client.get_user(356526822906920963).send("Ich habe mir die Freiheit genommen und Ihnen bereits die möglichen Raidtage herausgesucht. Aktuell stehen Ihnen folgende Optionen zur Verfügung:\n\n" +
    message_string)


@weekly_report.before_loop
async def before():
    await client.wait_until_ready()
    time_now = datetime.datetime.now()
    time_goal = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, 12, 19, 52, 0, 0)
    delt = time_goal - time_now
    if delt.total_seconds() < 0:
        time_goal = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day+1, 15, 15, 0, 0)
        delt = time_goal - time_now
    print(f"Wait for {delt.total_seconds()} seconds before starting the weekly report.")
    await asyncio.sleep(delt.total_seconds())
    print("Finished waiting")

weekly_report.start()
client.run(token)
