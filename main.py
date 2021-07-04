import discord
import pytz
import json
from discord.utils import get
from datetime import datetime, time, date, timedelta

# ==================== Globals ==========================
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
now = time(0, 0, 0)
hours = {}
days = ['Segunda-Feira', 'Terça-Feira', 'Quarta-Feira', 'Quinta-Feira', 'Sexta-Feira', 'Sábado', 'Domingo']


# ============================ functions ============================
def set_globals(data, command, week_day):
    global first, second, third, pause, forth, fifth, end, hours, now
    data_filtered = data[command][week_day]
    if data_filtered == 'free':
        data_filtered = data[command]['1']
    now = datetime.now(pytz.timezone('America/Sao_Paulo')).time()
    first = datetime.strptime(data_filtered['1']['time'][0], '%H:%M').time()
    second = datetime.strptime(data_filtered['1']['time'][1], '%H:%M').time()
    third = datetime.strptime(data_filtered['2']['time'][1], '%H:%M').time()
    pause = datetime.strptime(data_filtered['3']['time'][1], '%H:%M').time()
    forth = datetime.strptime(data_filtered['4']['time'][0], '%H:%M').time()
    fifth = datetime.strptime(data_filtered['4']['time'][1], '%H:%M').time()
    end = datetime.strptime(data_filtered['5']['time'][1], '%H:%M').time()
    hours = {'1': second, '2': third, '3': pause, '4': fifth, '5': end}


def next_subject(week_day, data_filtred, interval=False):
    if interval:
        return data_filtred[week_day]["4"]['subject']
    if week_day == '5' or week_day == '6' or (week_day == '4' and now > end):
        print('foi')
        return data_filtred['0']['1']['subject']
    if now > end:
        return data_filtred[str(int(week_day) + 1)]['1']['subject']
    return data_filtred[week_day]['1']['subject']


def time_until(hour, interval=False, free=False, week_day=None):
    dia = date(1, 1, 1)
    if interval:
        time_end = datetime.combine(dia, forth)
    elif free:
        if week_day == '4' and now > end:
            time_end = datetime.combine(date(1, 1, 3), first)
        elif week_day == '6':
            time_end = datetime.combine(date(1, 1, 2), first)
        else:
            time_end = datetime.combine(dia, first)
    else:
        time_end = datetime.combine(dia, hours[hour])
    time_now = datetime.combine(dia, now)
    if '-' in str(time_end - time_now):
        return round(timedelta.total_seconds(time_now - time_end) / 60, 1)
    return round(timedelta.total_seconds(time_end - time_now) / 60, 1)


def exception_handling(message, data):
    if len(message.content.split()) < 2:
        return 'Faltou informar o código da turma!'
    command = message.content.split()[1].upper()
    try:
        data[command]
    except KeyError:
        return 'Codigo de turma inválido'


def create_embed(data, x):
    strings = []
    for key, value in data[str(x)].items():
        strings.append(f'{key}° Horário: {value["subject"]} | {value["time"][0]} - {value["time"][1]}')
    return discord.Embed(title=days[int(x)],
                         description=f'{strings[0]}\n '
                                     f'{strings[1]}\n '
                                     f'{strings[2]}\n '
                                     f'{strings[3]}\n '
                                     f'{strings[4]}\n ',
                         color=0xffd343)


def raw_file():
    with open('data.json', 'r') as jason:
        return json.load(jason)


def actual_time():
    if first < now < second:
        return '1'
    if second < now < third:
        return '2'
    if third < now < pause:
        return '3'
    if pause < now < forth:
        return 'interval'
    if forth < now < fifth:
        return '4'
    if fifth < now < end:
        return '5'
    return 'free'


def help_embed():
    embed_var = discord.Embed(title="Class Assistant.py Bot",
                              description="Lista de todos os comandos do BOT e como utilizá-los",
                              color=0xffd343)
    embed_var.add_field(name="!agora",
                        value="Te informa a aula que ta rolando agora pra turma que pedir\n"
                              "Ex: !agora 3c2\n"
                              "Obs: Crie um cargo com o mesmo nome da turma para que eu mencione-o",
                        inline=False)
    embed_var.add_field(name="!hoje",
                        value="Te informa o horario de hoje para a turma que pedir\n"
                              "Ex: !hoje 3c2\n"
                              "Obs: Crie um cargo com o mesmo nome da turma para que eu mencione-o",
                        inline=False)
    embed_var.add_field(name="!horario",
                        value="Te informa o horario completo para a turma que pedir\n"
                              "Ex: !horario 3c2\n"
                              "Obs: Crie um cargo com o mesmo nome da turma para que eu mencione-o",
                        inline=False)
    return embed_var


def class_now(week_day, data_filtred, role):
    hour = actual_time()
    try:
        role.mention
    except AttributeError:
        mention = ''
    else:
        mention = role.mention
    if hour == 'free':
        time_left = time_until(hour, free=True, week_day=week_day)
        if time_left > 60:
            time_left = str(round(time_left / 60, 1)) + ' horas'
        else:
            time_left = str(time_left) + ' minutos'
        subject = next_subject(week_day, data_filtred)
        return discord.Embed(title='Nenhuma aula no momento!',
                             description=f'Falta {time_left} para a aula de {subject}!\n'
                                         f'{mention}',
                             color=0xffd343)

    if hour == 'interval':
        time_left = time_until(hour, interval=True)
        subject = next_subject(week_day, data_filtred, interval=True)
        return discord.Embed(title='Ta no intervalo',
                             description=f'Falta {time_left} minutos para a aula de {subject}!\n'
                                         f'{mention}',
                             color=0xffd343)

    subject = data_filtred[week_day][hour]['subject']
    start_end = data_filtred[week_day][hour]['time']
    time_left = time_until(hour)
    return discord.Embed(title=f'Ta tendo aula de {subject} agora, corre lá!',
                         description=f'Começou {start_end[0]} e vai terminar {start_end[1]}\n '
                                     f'falta {time_left} minutos para acabar!\n'
                                     f'{mention}',
                         color=0xffd343)


# =============================== Client run ==================================================
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,
                                                           name="!help"))


@client.event
async def on_message(message):
    if message.author == client.user or not message.content.startswith('!'):
        return
    if message.content.startswith('!help'):
        embed_var = help_embed()
        await message.channel.send(embed=embed_var)
        return

    data = raw_file()
    week_day = str(datetime.now(pytz.timezone('America/Sao_Paulo')).weekday())
    exception = exception_handling(message, data)
    if exception:
        await message.channel.send(exception)
        return
    command = message.content.split()[1].upper()
    data_filtred = data[command]

    if message.content.startswith('!horario'):
        for x in range(1, 6):
            embed_var = create_embed(data_filtred, x)
            await message.channel.send(embed=embed_var)
        return

    set_globals(data, command, week_day)

    if message.content.startswith('!hoje'):
        if data_filtred[week_day] == 'free':
            await message.channel.send('Nenhuma aula hoje!')
            return
        embed_var = create_embed(data_filtred, week_day)
        await message.channel.send(embed=embed_var)
        return

    if message.content.startswith('!agora'):
        role = get(message.guild.roles, name=command)
        embed_var = class_now(week_day, data_filtred, role)
        await message.channel.send(embed=embed_var)


client.run(discord_token)
