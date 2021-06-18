import discord
import pytz
import json
from datetime import datetime, time, date, timedelta

client = discord.Client()
with open('config.json', 'r') as token:
    discord_token = json.load(token)['token']
first = time(0, 0, 0)
second = time(0, 0, 0)
third = time(0, 0, 0)
pause = time(0, 0, 0)
forth = time(0, 0, 0)
fifth = time(0, 0, 0)
end = time(0, 0, 0)
hours = []
now = time(0, 0, 0)
timeZone = pytz.timezone('America/Sao_Paulo')
days = ['Domingo', 'Segunda-Feira', 'Terça-Feira', 'Quarta-Feira', 'Quinta-Feira', 'Sexta-Feira', 'Sabado']
roleId = {'3c2': '853795487513706537', '3a2': '853795394676850728'}


def CreateGlobals(data, command, weekDay):
    global first, second, third, pause, forth, fifth, end, hours, now, timeZone
    dataFiltered = data[command][weekDay]
    now = datetime.now(timeZone).time()
    first = datetime.strptime(dataFiltered['1']['time'][0], '%H:%M').time()
    second = datetime.strptime(dataFiltered['1']['time'][1], '%H:%M').time()
    third = datetime.strptime(dataFiltered['2']['time'][1], '%H:%M').time()
    pause = datetime.strptime(dataFiltered['3']['time'][1], '%H:%M').time()
    forth = datetime.strptime(dataFiltered['4']['time'][0], '%H:%M').time()
    fifth = datetime.strptime(dataFiltered['4']['time'][1], '%H:%M').time()
    end = datetime.strptime(dataFiltered['5']['time'][1], '%H:%M').time()
    hours = [first, second, third, forth, fifth]


def NextSubject(weekDay, data, command, interval=False):
    dataFiltred = data[command]
    if interval:
        return dataFiltred[weekDay]["4"]['subject']
    if int(weekDay) < 1 or int(weekDay) >= 5:
        return dataFiltred['1']['1']['subject']
    nextDay = int(weekDay) + 1
    return dataFiltred[str(nextDay)]['1']['subject']


def TimeUntil(hour, interval=False, free=False, weekDay=None):
    dia = date(1, 1, 1)
    if interval:
        timeEnd = datetime.combine(dia, forth)
    elif free:
        if weekDay == '5':
            timeEnd = datetime.combine(date(1, 1, 4), first)
        elif weekDay == '6':
            timeEnd = datetime.combine(date(1, 1, 3), first)
        else:
            timeEnd = datetime.combine(date(1, 1, 2), first)
    else:
        timeEnd = datetime.combine(dia, hours[int(hour) - 1])
    timeNow = datetime.combine(dia, now)
    if '-' in str(timeEnd - timeNow):
        return round(timedelta.total_seconds(timeNow - timeEnd) / 60, 1)
    return round(timedelta.total_seconds(timeEnd - timeNow) / 60, 1)


def ExceptionHandling(message, data):
    if len(message.content.split()) < 2:
        return 'Faltou informar o código da turma!'
    command = message.content.split()[1].upper()
    try:
        dataFiltred = data[command]
    except KeyError:
        return 'Codigo de turma inválido'
    return


def CreateEmbed(data, x):
    strings = []
    for key, value in data[str(x)].items():
        strings.append(f'{key}° Horário: {value["subject"]} | {value["time"][0]} - {value["time"][1]}')
    return discord.Embed(title=days[int(x)],
                         description=f'{strings[0]}\n '
                                     f'{strings[1]}\n '
                                     f'{strings[2]}\n '
                                     f'{strings[3]}\n '
                                     f'{strings[4]}\n ',
                         color=0xfc03f0)


def GetRawFile():
    with open('data.json', 'r') as jason:
        return json.load(jason)


def GetActualTime():
    # timeNow = time(20, 0, 0)
    if first < now < second:
        hour = '1'
    elif second < now < third:
        hour = '2'
    elif third < now < pause:
        hour = '3'
    elif pause < now < forth:
        hour = 'interval'
    elif forth < now < fifth:
        hour = '4'
    elif fifth < now < end:
        hour = '5'
    else:
        hour = 'free'
    return hour


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming,
                                                           name="O sexo nervoso que eu to fazendo com a sua mãe"))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    data = GetRawFile()
    weekDay = str(datetime.now(timeZone).weekday() + 1)

    if message.content.startswith('!horario'):
        exception = ExceptionHandling(message, data)
        if exception:
            await message.channel.send(exception)
            return
        command = message.content.split()[1].upper()
        CreateGlobals(data, command, weekDay)
        dataFiltred = data[command]
        for x in range(1, 6):
            embedVar = CreateEmbed(dataFiltred, x)
            await message.channel.send(embed=embedVar)

    if message.content.startswith('!hoje'):
        exception = ExceptionHandling(message, data)
        if exception:
            await message.channel.send(exception)
            return
        command = message.content.split()[1].upper()
        CreateGlobals(data, command, weekDay)
        dataFiltred = data[command]
        embedVar = CreateEmbed(dataFiltred, weekDay)
        await message.channel.send(embed=embedVar)

    if message.content.startswith('!agora'):
        exception = ExceptionHandling(message, data)
        if exception:
            await message.channel.send(exception)
            return
        command = message.content.split()[1].upper()
        CreateGlobals(data, command, weekDay)
        hour = GetActualTime()
        if hour == 'free':
            timeLeft = TimeUntil(hour, free=True, weekDay=weekDay)
            if timeLeft > 60:
                timeLeft = str(round(timeLeft / 60, 1)) + ' horas'
            else:
                timeLeft = str(timeLeft) + ' minutos'
            nextSubject = NextSubject(weekDay, data, command)
            if nextSubject == "Livre":
                nextSubject = "vaga antes de RAC"
            else:
                nextSubject = f'de {nextSubject}'
            embedVar = discord.Embed(title='Nenhuma aula hoje!',
                                     description=f'Falta {timeLeft} para a aula {nextSubject} amanhã!',
                                     color=0xfc03f0)
            await message.channel.send(embed=embedVar)
            return
        if hour == 'interval':
            timeLeft = TimeUntil(hour, interval=True)
            nextSubject = NextSubject(weekDay, data, command, interval=True)
            embedVar = discord.Embed(title='Ta no intervalo',
                                     description=f'Falta {timeLeft} minutos para a aula de {nextSubject} ainda!',
                                     color=0xfc03f0)
            await message.channel.send(embed=embedVar)
            return
        subject = data[command][weekDay][hour]['subject']
        startEnd = data[command][weekDay][hour]['time']
        timeLeft = TimeUntil(hour)
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
