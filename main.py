import discord
import json
from datetime import datetime, time, date, timedelta

client = discord.Client()
with open('config.json', 'r') as token:
    discord_token = json.load(token)['token']
first = time(16, 0, 0)
second = time(16, 50, 0)
third = time(17, 40, 0)
pause = time(18, 35, 0)
forth = time(18, 55, 0)
fifth = time(19, 45, 0)
end = time(20, 35, 0)
hours = [first, second, third, forth, fifth]
days = ['Domingo', 'Segunda-Feira', 'Terça-Feira', 'Quarta-Feira', 'Quinta-Feira', 'Sexta-Feira', 'Sabado']
roleId = {'3c2': '853795487513706537', '3a2': '853795394676850728'}


def ExceptionHandling(message, data):
    if len(message.content.split()) < 2:
        return 'Faltou informar o código da turma!'
    command = message.content.split()[1]
    try:
        dataFiltred = data[command]
    except KeyError:
        return 'Codigo de turma inválido'
    if dataFiltred == "free":
        return "Nenhuma aula hoje"
    return


def CreateEmbed(data, x, command):
    strings = []
    for key, value in data[str(x)].items():
        strings.append(f'{key}° Horário: {value["subject"]} | {value["time"][0]} - {value["time"][1]}')
    return discord.Embed(title=days[int(x)],
                         description=f'@{command.upper()}\n '
                                     f'{strings[0]}\n '
                                     f'{strings[1]}\n '
                                     f'{strings[2]}\n '
                                     f'{strings[3]}\n '
                                     f'{strings[4]}\n ',
                         color=0xfc03f0)


def GetRawFile():
    with open('data.json', 'r') as jason:
        return json.load(jason)


def GetActualTime():
    timeNow = datetime.utcnow().time()
    # timeNow = time(20, 0, 0)
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
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming,
                                                           name="O sexo nervoso que eu to fazendo com a sua mãe"))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!horario'):
        data = GetRawFile()
        exception = ExceptionHandling(message, data)
        if exception:
            await message.channel.send(exception)
            return
        command = message.content.split()[1]
        dataFiltred = data[command]
        for x in range(1, 6):
            embedVar = CreateEmbed(dataFiltred, x, command)
            await message.channel.send(embed=embedVar)

    if message.content.startswith('!hoje'):
        data = GetRawFile()
        exception = ExceptionHandling(message, data)
        if exception:
            await message.channel.send(exception)
            return
        command = message.content.split()[1]
        dataFiltred = data[command]
        timeData = GetActualTime()
        weekDay = timeData[0]
        embedVar = CreateEmbed(dataFiltred, weekDay, command)
        await message.channel.send(embed=embedVar)

    if message.content.startswith('!agora'):
        data = GetRawFile()
        exception = ExceptionHandling(message, data)
        if exception:
            await message.channel.send(exception)
            return
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
        startEnd = data[command][weekDay][hour]['time']
        dia = date(1, 1, 1)
        timeEnd = datetime.combine(dia, hours[int(hour) - 1])
        timeNow = datetime.combine(dia, datetime.utcnow().time())
        timeLeft = round(timedelta.total_seconds(timeNow - timeEnd) / 60, 1)
        embedVar = discord.Embed(title=f'Ta tendo aula de {subject} agora, corre lá!',
                                 description=f'Começou {startEnd[0]} e vai terminar {startEnd[1]}\n '
                                             f'falta {timeLeft} minutos para acabar!\n'
                                             f'<@&{roleId[command]}>',
                                 color=0xfc03f0)
        await message.channel.send(embed=embedVar)

    if message.content.startswith('!help'):
        embedVar = discord.Embed(title="Class Assistant.py Bot",
                                 description="Lista de todos os comandos do BOT e como utilizá-los",
                                 color=0xfc03f0)
        embedVar.add_field(name="!agora",
                           value="Te informa a aula que ta rolando agora pra turma que pedir\n Ex: !agora 3c2",
                           inline=False)
        embedVar.add_field(name="!hoje",
                           value="Te informa o horario de hoje para a turma que pedir\n Ex: !hoje 3c2",
                           inline=False)
        embedVar.add_field(name="!horario",
                           value="Te informa o horario completo para a turma que pedir\n Ex: !horario 3c2",
                           inline=False)
        await message.channel.send(embed=embedVar)


client.run(discord_token)
