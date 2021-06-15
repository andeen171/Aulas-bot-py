import discord
import json
from datetime import datetime, time, date, timedelta

client = discord.Client()
discord_token = ''
first = time(16, 0, 0)
second = time(16, 50, 0)
third = time(17, 40, 0)
pause = time(18, 35, 0)
forth = time(18, 55, 0)
fifth = time(19, 45, 0)
end = time(20, 35, 0)
hours = [first, second, third, forth, fifth]
days = ['Domingo', 'Segunda-Feira', 'Terça-Feira', 'Quarta-Feira', 'Quinta-Feira', 'Sexta-Feira', 'Sabado']


def GetRawFile():
    with open('data.json', 'r') as jason:
        return json.load(jason)


def GetActualTime():
    timeNow = datetime.utcnow().time()
    # timeNow = time(20, 0, 0)
    weekday = str(datetime.utcnow().weekday())
    print(weekday)
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
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming,
                                                           name="O sexo nervoso que eu to fazendo com a sua mãe"))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!hoje'):
        if len(message.content.split()) < 2:
            await message.channel.send('Faltou informar o código da turma!')
            return
        command = message.content.split()[1]
        data = GetRawFile()
        timeData = GetActualTime()
        weekDay = timeData[0]
        try:
            dataFiltred = data[command][weekDay]
        except KeyError:
            await message.channel.send('Codigo de turma inválido')
            return
        if dataFiltred == "free":
            embedVar = discord.Embed(title=days[int(weekDay)],
                                     description="Hoje ce ta atoa",
                                     color=0xfc03f0)
            await message.channel.send(embed=embedVar)
            return
        strings = []
        for key, value in dataFiltred.items():
            strings.append(f'{key}° Horário: {value["subject"]} | {value["time"][0]} - {value["time"][1]}')
        embedVar = discord.Embed(title=days[int(weekDay)],
                                 description=f'{strings[0]}\n '
                                             f'{strings[1]}\n '
                                             f'{strings[2]}\n '
                                             f'{strings[3]}\n '
                                             f'{strings[4]}\n ',
                                 color=0xfc03f0)
        await message.channel.send(embed=embedVar)

    if message.content.startswith('!agora'):
        if len(message.content.split()) < 2:
            await message.channel.send('Faltou informar o código da turma!')
            return
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
        try:
            subject = data[command][weekDay][hour]['subject']
            startEnd = data[command][weekDay][hour]['time']
        except KeyError:
            await message.channel.send('Codigo de turma inválido')
            return
        dia = date(1, 1, 1)
        timeEnd = datetime.combine(dia, datetime.strptime(startEnd[1], '%H:%M').time())
        timeNow = datetime.combine(dia, datetime.utcnow().time())
        timeLeft = round(timedelta.total_seconds(timeEnd - timeNow) / 60)
        embedVar = discord.Embed(title=f'Ta tendo aula de {subject} agora, corre lá!',
                                 description=f'Começou {startEnd[0]} e vai terminar {startEnd[1]}\n '
                                             f'falta {timeLeft} minutos para acabar!',
                                 color=0xfc03f0)
        await message.channel.send(embed=embedVar)

    if message.content.startswith('!help'):
        embedVar = discord.Embed(title="Class Assistant.py Bot",
                                 description="Lista de todos os comandos do BOT e como utilizá-los",
                                 color=0xfc03f0)
        embedVar.add_field(name="!agora",
                           value="Te informa a aula que ta rolando agora pra turma que você pedir\n Ex: !agora 3c2",
                           inline=False)
        await message.channel.send(embed=embedVar)


client.run(discord_token)
