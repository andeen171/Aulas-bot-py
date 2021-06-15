import discord
import json
from datetime import datetime, time

client = discord.Client()
discord_token = ''
first = time(16, 0, 0)
second = time(16, 50, 0)
third = time(17, 40, 0)
pause = time(18, 35, 0)
forth = time(18, 55, 0)
fifth = time(19, 45, 0)
end = time(20, 35, 0)


def GetRawFile():
    with open('data.json', 'r') as jason:
        return json.load(jason)


def GetActualTime():
    timeNow = time(20, 0, 0)
    weekday = str(datetime.utcnow().weekday() + 1)
    if first < timeNow < second:
        hour = '1'
    elif second < timeNow < third:
        hour = '2'
    elif third < timeNow < pause:
        hour = '3'
    elif pause < timeNow < forth:
        hour = 'Interval'
    elif forth < timeNow < fifth:
        hour = '4'
    elif fifth < timeNow < end:
        hour = '5'
    else:
        hour = 'free'
    return [weekday, hour]


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="!help"))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!agora'):
        data = GetRawFile()
        command = message.content.split()[1]
        timeData = GetActualTime()
        weekDay = timeData[0]
        hour = timeData[1]
        if hour == 'free':
            await message.channel.send('Nenhuma aula agora!')
            return
        if hour == 'interval':
            await message.channel.send('Ta no intervalo!')
            return
        subject = data[command][weekDay][hour]['subject']
        dateEnd = data[command][weekDay][hour]['time'][1]
        await message.channel.send(f'Ta tendo aula de {subject} agora, corre lá! até {dateEnd}')

    if message.content.startswith('!help'):
        embedVar = discord.Embed(title="Class Assistant.py Bot",
                                 description="Lista de todos os comandos do BOT e como utilizá-los",
                                 color=0xfc03f0)
        embedVar.add_field(name="!agora",
                           value="Te informa a aula que ta rolando agora pra turma que você pedir\n Ex: !agora 3c2",
                           inline=False)
        await message.channel.send(embed=embedVar)

client.run(discord_token)
