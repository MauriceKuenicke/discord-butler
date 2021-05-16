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
    df = google_doc.request_GoogleDocRecords(week="next")
    embed = utils.embeds.createTimeTable(df)
    await ctx.send(f"Aktuell eingetragene Zeiten für die Raidwoche ({df['Datum'].min():%d.%m.%Y}-{df['Datum'].max():%d.%m.%Y})\n")
    await ctx.send(embed=embed)


@ tasks.loop(hours=168.0)  # 168 hours = 1 week
async def send_reminder():
    print("Start reminder.")
    df = google_doc.request_GoogleDocRecords(week="next")
    playerL = google_doc.get_slacking_player(df)
    if len(playerL) > 0:
        print("List of slacking player: ", playerL)
        # Calculate poossible days without missing player
        available_days, single_block = google_doc.calculate_available_days(
            df.drop([player for player in playerL], axis=1))

        # Message player
        message_string = ""
        for index, data in available_days.iterrows():
            message_string += f'{data["Wochentag"]}({data["Datum"]:%d.%m.%Y}) von {int(data["start_time"])}Uhr bis {int(data["end_time"])}Uhr\n'
        for player in playerL:
            user_id = utils.get_userID_by_name(player)
            username = str(client.get_user(user_id)).split("#")[0]
            await client.get_user(user_id).send(f"Guten Tag {username}! Auf meinem wöchentlichen Rundgang musste ich feststellen, dass Sie für die kommende Raidwoche weniger als 2 mögliche Tage in den Kalender eingetragen haben. " +
                                                "Falls dies beabsichtigt gewesen ist, betrachten Sie diese Nachricht als gegenstandslos. Falls nicht, möchte ich Sie höflichst darum bitten, die Eintragungen auf einen aktuellen Stand zu bringen.")

            if available_days.shape[0] > 1:
                await client.get_user(user_id).send("Aktuell wären folgende Termine mit Ihnen möglich: \n" +
                                                    message_string)
    else:
        print("No slacking player found...")
        pass


@ tasks.loop(hours=168.0)  # 168 hours = 1 week
async def send_weekly_report():
    print("Start weekly report.")
    df = google_doc.request_GoogleDocRecords(week="next")
    available_days, single_block = google_doc.calculate_available_days(df)

    if available_days.shape[0] < 2:
        player_single_block = single_block.columns[single_block.isin(
            ['-']).any()].tolist()
        # Message player
        print("Message player for possible days: ", player_single_block)
        for player in player_single_block:
            message_string = ""
            for date in single_block[single_block[player] == "-"]["Datum"].values:
                indx = single_block.index[single_block['Datum'] == date].tolist()[
                    0]
                wday = single_block["Wochentag"][indx]
                message_string += f'**- {wday}({date:%d.%m.%Y})**\n'

            user_id = utils.get_userID_by_name(player)
            username = str(client.get_user(user_id)).split("#")[0]
            user = client.get_user(user_id)
            await user.send(f"Guten Abend {username}! Leider muss ich Ihnen mitteilen, dass es sehr schlecht aussieht, was die Raidtage nächste Woche betrifft. Allerdings musste ich feststellen, dass Sie zu folgenden Terminen als einzige Person keine Zeit haben:\n\n" +
                            message_string + "\nVielleicht können Sie uns doch an einem dieser Tage mit Ihrer Anwesenheit beglücken. Falls das der Fall sein sollte, würde ich Sie bitten dies in Form einer Zeitangabe im Kalender bis spätestens 20Uhr am heutigen Tag zu vermerken.")

    # Create and send message
    embed = utils.embeds.createTimeTable(df)
    message_string = ""
    for index, data in available_days.iterrows():
        message_string += f'**- {data["Wochentag"]}({data["Datum"]:%d.%m.%Y}) von {int(data["start_time"])}Uhr bis {int(data["end_time"])}Uhr**\n'
    for user_id in [utils.get_userID_by_name("Dimi"), utils.get_userID_by_name("Mira")]:
        username = str(client.get_user(user_id)).split("#")[0]
        user = client.get_user(user_id)
        await user.send(f"Guten Abend {username}! Hier finden Sie die aktuelle Übersicht der eingetragenen Zeiten für die kommende Woche:")
        await user.send(embed=embed)
        await user.send("Ich habe mir die Freiheit genommen und Ihnen bereits die möglichen Raidtage herausgesucht. Aktuell stehen folgende Optionen zur Verfügung:\n\n" +
                        message_string)
        if available_days.shape[0] < 2:
            message_string_player_informed = ""
            for player in player_single_block:
                message_string_player_informed += "**- " + player+"**\n"
            await user.send("\n\nWie Sie sehen können, sieht es mit verfügbaren Tagen sehr schlecht aus. Ich habe allerdings schon folgende Spieler über mögliche Termine benachrichtigt, da an diesen nur jeweils ein Spieler fehlt:\n\n" +
                            message_string_player_informed +
                            "\nDie weitere Planung überlasse ich Ihnen und verabschiede mich nun in den Feierabend für diese Woche!")
    print("Report summary sent.")


@ send_weekly_report.before_loop
async def before_weekly():
    await client.wait_until_ready()
    # Sunday 18:00 -> (6, 16, 0) 2h delay
    delta = utils.calculate_timedelta(6, 10, 0)
    print(f"Starting weekly report cycle in {delta} seconds.")
    await asyncio.sleep(delta)
    print("Starting weekly report cycle.")


@ send_reminder.before_loop
async def before_reminder():
    await client.wait_until_ready()
    delta = utils.calculate_timedelta(5, 10, 0)
    print(f"Starting reminder cycle in {delta} seconds.")
    await asyncio.sleep(delta)
    print("Starting reminder cycle.")

send_reminder.start()
send_weekly_report.start()
client.run(token)
