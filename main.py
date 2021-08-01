import discord
import pytz
import json
from discord.utils import get
from datetime import datetime, date, timedelta

client = discord.Client()
with open('config.json', 'r') as token:
    discord_token = json.load(token)['token']
valid_commands = ["!help", "!horario", "!agora", "!hoje"]
days = ['Segunda-Feira', 'Terça-Feira', 'Quarta-Feira', 'Quinta-Feira', 'Sexta-Feira', 'Sábado', 'Domingo']


class Session:

    def __init__(self, command):
        with open('data.json', 'r') as jason:
            self.data = json.load(jason)
        self.now = datetime.now(pytz.timezone('America/Sao_Paulo'))
        self.week_day = str(self.now.weekday())
        self.command = command
        self.days = ['Segunda-Feira', 'Terça-Feira', 'Quarta-Feira', 'Quinta-Feira', 'Sexta-Feira', 'Sábado', 'Domingo']
        self.data_filtered = self.data[command][self.week_day]
        hours = []
        for time_stamp in self.data[command]['time']:
            hours.append(datetime.strptime(time_stamp, '%H:%M').time())
        self.hours = hours
        self.final = {'1': hours[1], '2': hours[2], '3': hours[3], '4': hours[5], '5': hours[6]}

    def schedule(self):
        now = self.now.time()
        if self.hours[0] < now < self.hours[1]:
            return '1'
        if self.hours[1] < now < self.hours[2]:
            return '2'
        if self.hours[2] < now < self.hours[3]:
            return '3'
        if self.hours[3] < now < self.hours[4]:
            return 'interval'
        if self.hours[4] < now < self.hours[5]:
            return '4'
        if self.hours[5] < now < self.hours[6]:
            return '5'
        return 'free'

    def time_until(self):
        dia = date(1, 1, 1)
        time_stamp = self.schedule()
        if time_stamp == "interval":
            time_end = datetime.combine(dia, self.hours[4])
        elif time_stamp == "free":
            if self.week_day == '4' and self.now.time() > self.hours[6]:
                time_end = datetime.combine(date(1, 1, 3), self.hours[0])
            elif self.week_day == '6':
                time_end = datetime.combine(date(1, 1, 2), self.hours[0])
            else:
                time_end = datetime.combine(dia, self.hours[0])
        else:
            time_end = datetime.combine(dia, self.final[self.schedule()])
        time_now = datetime.combine(dia, self.now.time())
        if '-' in str(time_end - time_now):
            return round(timedelta.total_seconds(time_now - time_end) / 60, 1)
        return round(timedelta.total_seconds(time_end - time_now) / 60, 1)

    def create_embed(self, x):
        data = self.data_filtered
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

    def next_subject(self):
        timestamp = self.schedule()
        if timestamp == "interval":
            return self.data[self.command][self.week_day]["4"]
        if self.week_day == '5' or self.week_day == '6' or (self.week_day == '4' and self.now.time() > self.hours[6]):
            print('foi')
            return self.data[self.command]['0']['1']
        if self.now.time() > self.hours[6]:
            return self.data[self.command][str(int(self.week_day) + 1)]['1']
        return self.data[self.command][self.week_day]['1']

    def class_now(self, role):
        hour = self.schedule()
        try:
            role.mention
        except AttributeError:
            mention = ''
        else:
            mention = role.mention
        if hour == 'free':
            time_left = self.time_until()
            if time_left > 60:
                time_left = str(round(time_left / 60, 1)) + ' horas'
            else:
                time_left = str(time_left) + ' minutos'
            subject = self.next_subject()
            return discord.Embed(title='Nenhuma aula no momento!',
                                 description=f'Falta {time_left} para a aula de {subject}!\n'
                                             f'{mention}',
                                 color=0xffd343)

        if hour == 'interval':
            time_left = self.time_until()
            subject = self.next_subject()
            return discord.Embed(title='Ta no intervalo',
                                 description=f'Falta {time_left} minutos para a aula de {subject}!\n'
                                             f'{mention}',
                                 color=0xffd343)

        subject = self.data_filtered[hour]
        time_left = self.time_until()
        return discord.Embed(title=f'Ta tendo aula de {subject} agora, corre lá!',
                             description=f'falta {time_left} minutos para acabar!\n'
                                         f'{mention}',
                             color=0xffd343)

    @staticmethod
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


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,
                                                           name="!help"))


@client.event
async def on_message(message):
    if message.author == client.user or message.content.split()[0] not in valid_commands:
        return
    command = message.content.split()[1].upper()
    session = Session(command)
    if message.content.startswith('!help'):
        embed_var = session.help_embed()
        await message.channel.send(embed=embed_var)
        return

    if message.content.startswith('!horario'):
        for x in range(1, 6):
            embed_var = session.create_embed(x)
            await message.channel.send(embed=embed_var)
        return

    if message.content.startswith('!hoje'):
        if session.data_filtered[session.week_day] == 'free':
            await message.channel.send('Nenhuma aula hoje!')
            return
        embed_var = session.create_embed(session.week_day)
        await message.channel.send(embed=embed_var)
        return

    if message.content.startswith('!agora'):
        role = get(message.guild.roles, name=command)
        embed_var = session.class_now(role)
        await message.channel.send(embed=embed_var)


client.run(discord_token)
