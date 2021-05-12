from dotenv import load_dotenv
from discord.ext import commands
import discord
import google_doc
import os
load_dotenv()

client = commands.Bot(command_prefix=".")
token = os.getenv("DISCORD_BOT_TOKEN")

@client.event
async def on_ready() :
    await client.change_presence(status = discord.Status.online, activity = discord.Activity(type=discord.ActivityType.watching, name="you"))
    print("I am online")

@client.command()
async def ping(ctx) :
    await ctx.send(f"🏓 Pong with {str(round(client.latency, 2))}")

@client.command(name="whoami")
async def whoami(ctx) :
    await ctx.send(f"You are {ctx.message.author.name}")

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
    # Filter maybe?
    df = df[:7] 
    # -----------
    data_set = list(df.itertuples(index=False, name=None))

    # Create embeded message for data
    embed = discord.Embed(title=f"__**Zeiten:**__", color=0x03f8fc)
    player = tuple(i for i in df.columns[1:])
    for cnt, day in enumerate(df["Wochentag"]):
        embed.add_field(name=f'**{day}**', value=f'{player[0]}:  {data_set[cnt][1]}' +
        f'\n {player[1]}:  {data_set[cnt][2]}' +
        f'\n {player[2]}:  {data_set[cnt][3]}' +
        f'\n {player[3]}:  {data_set[cnt][4]}' +
        f'\n {player[4]}:  {data_set[cnt][5]}' +
        f'\n {player[5]}:  {data_set[cnt][6]}\n ', inline=True)
    
    await ctx.send(embed=embed)
    await ctx.send("\nMich dünkt, es haben einige vergessen ihre Zeiten einzutragen.")



client.run(token)
