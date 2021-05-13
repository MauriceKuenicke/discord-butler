import discord


def createTimeTable(df):
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
    return embed
