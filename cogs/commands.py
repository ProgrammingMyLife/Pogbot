import os
import platform
import re

import discord
import requests
import requests_cache
import json
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from discord.ext import commands
from utils.pogfunctions import send_embed
from utils.pogesquelle import get_prefix, get_db_item, check_snipes, decodebase64

session = requests_cache.CachedSession('covid_cache', expire_after=timedelta(hours=6))


class Commands(commands.Cog, name="Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='prefix', brief='Responds with the prefix.',
                      description="Responds with Pogbot's command prefix.")
    async def prefix(self, ctx):
        justprefix = await get_prefix(self.bot, ctx.message)
        await send_embed(ctx.message.channel, send_option=0, description=f"**The current prefix is {justprefix[2]}**",
                         color=0x08d5f7)

    @commands.command(name='ping', aliases=['latency'], brief='Responds with latency.',
                      description="Responds with Pogbot's latency.")
    # Look for a command called ping.
    async def ping(self, ctx):
        # Responds with the bots latency in a embed.
        embedping = discord.Embed(
            description=f"<:Check:845178458426179605> **Pogbot's latency is {round(self.bot.latency * 100)}ms**",
            color=0x08d5f7)
        # Edit the original message
        await ctx.send(embed=embedping)

    @commands.command(name='github', brief="Responds with github link.",
                      description="Responds with the link to Pogbot's github.")
    # Look for a command called github.
    async def github(self, ctx):
        # Sends the link to the bot github page when the github command is used.
        await ctx.send("https://github.com/projectopengroup/Pogbot")

    @commands.command(name='codeck', aliases=['deck'], brief='Responds with codeck link.',
                      description="Responds with the link to Pogbot's codeck.")
    # Look for a command called codeck.
    async def codeck(self, ctx):
        # Sends the link to the bot codeck page when the codeck command is used.
        await ctx.send("https://open.codecks.io/pog")

    @commands.command(name='echo', brief='Responds with the text provided.',
                      description="Replies with the same text argument that's provided by the user.")
    # Look for a command called echo
    async def echo(self, ctx, *, text_to_echo):
        # Send an echo of the keyword-only argument.
        await ctx.send(text_to_echo)

    @commands.command(name='icon', brief="Responds with Pogbot's avatar.", description="Responds with Pogbot's avatar.")
    # Look for a command called icon.
    async def icon(self, ctx):
        # Send pogbot icon
        await ctx.send(self.bot.user.avatar_url)

    @commands.command(name='avatar', aliases=['av', 'pfp'], brief='Responds with an avatar.',
                      description="Responds with the avatar of a user provided, if none provided, responds with the "
                                  "avatar of the user that called the command.")
    # Look for a command called avatar and collects optional user parameter, so if no user given, user = None.
    async def avatar(self, ctx, user: discord.Member = None):
        # Checks if user parameter is given. If user = none, that means no user was given so user variable is set to the
        # command author.
        if user is None:
            user = ctx.author
        # Defining pfp from user's avatar_url.
        pfp = user.avatar_url
        # Creating an embed response using an f string to insert the author long name by using our variable 'user',
        # setting the description to '**Avatar**', the color to match the bot, and the image to the specified user's
        # pfp.
        await send_embed(ctx, title=f'**{user}**', description='**Avatar**', color=0x08d5f7, image=pfp)

    @commands.command(name='userid', aliases=['id', 'uid'], brief='Responds with a users ID.',
                      description="Responds with the ID of a user provided, if none provided, responds with the"
                                  " ID of the user that called the command.")
    # Look for a command called userid and collects optional user parameter, so if no user given, user = None.
    async def userid(self, ctx, user: discord.Member = None):
        # Checks if user parameter is given. If user = none, that means no user was given so user variable is set to the
        # command author.
        if user is None:
            user = ctx.author
        # Creates a discord embed with the elements: title (Which gets the user's tag),
        # description (Which gets the user's id), and color (which is the bot's color).
        await send_embed(ctx, author=f"{user}'s ID", author_pfp=user.avatar_url, description=f'**{user.id}**',
                         color=0x08d5f7)

    @commands.command(name='botinfo', aliases=['binfo'], brief='Responds with information about the bot.',
                      description="Responds with information about the bot and it's hosting environment.")
    async def botinfo(self, ctx):
        await send_embed(ctx, title=f"**Pogbot's Info**", thumbnail=self.bot.user.avatar_url,
                         fields=[(f'**Python Version:**', platform.python_version(), True),
                                 (f'**Operating System:**', platform.system(), True),
                                 (f'**OS Version:**', platform.release(), True),
                                 (f'**OS Details:**', platform.platform(), True),
                                 (f'**Created by:**',
                                  "[Project Open Group, a community project.](https://github.com/projectopengroup)",
                                  True),
                                 (f'**Pogbot is:**',
                                  "[Open Source](https://github.com/projectopengroup/pogbot)", True)],
                         color=0x08d5f7)

    @commands.command(name='serverinfo', aliases=['sinfo'], brief='Responds with information about the discord server.',
                      description="Responds with information about the discord server it's ran in.")
    async def serverinfo(self, ctx):
        server = ctx.message.guild
        time = str(server.created_at)
        time = time.split(" ")
        time = time[0]

        list_of_bots = [bot.mention for bot in server.members if bot.bot]

        await send_embed(ctx, title=f"**{server} Info**", thumbnail=server.icon_url,
                         fields=[(f'**Server Owner**', f"{server.owner}", True),
                                 (f'**Owner ID:**', server.owner.id, True),
                                 (f'**Server ID:**', server.id, True),
                                 (f'**Highest Role:**', server.roles[-2], True),
                                 (f'**Member Count:**', server.member_count, True),
                                 (f'**Channel Count:**', len(server.channels), True),
                                 (f'**Role Count**', len(server.roles), True),
                                 (f'**Bots**',
                                  str(list_of_bots).replace("'", "").replace(']', '').replace('[', ''), True),
                                 (f'**Region**', len(server.region), True),
                                 (f'**Verification Level**', len(server.verification_level), True),
                                 (f'**Bot Count**', len(list_of_bots), True),
                                 (f'**Created:**', time, True)],
                         color=0x08d5f7)

    @commands.command(name='whois', aliases=['userinfo', 'uinfo'], brief='Responds with information on a user.',
                      description="Responds with the information of a user provided, if none provided, responds "
                                  "with the information of the user that called the command.")
    # Look for a command called whois and collects optional user parameter, so if no user given, user = None.
    async def whois(self, ctx, user: discord.Member = None):
        # Checks if user parameter is given. If user = none, that means no user was given so user variable is set to the
        # command author.
        if user is None:
            user = ctx.author

        # Checks if the user is a bot and stores it in a variable
        isBot = "No"
        if user.bot:
            isBot = "Yes"

        # Checks if the user has a nickname set by taking the username, removing the # and numbers, and comparing it
        # with the display name.
        usernameFull = str(user)
        username, usertag = usernameFull.split("#")
        nickname = user.display_name
        if username == nickname:
            nickname = "None"

        # Get's user's status
        userStatus = str(user.status).title()
        if userStatus == "Dnd":
            userStatus = "Do not disturb"

        # Gets user's roles, excludes the @everyone role, and puts it in a string
        foundRoles = []
        for role in user.roles:
            if role.name != "@everyone":
                foundRoles.append(role.mention)

        foundRoles.reverse()
        userRoles = " ".join(foundRoles)

        # Creates and sends an embed with various user info by adding them as fields. When getting dates, the format
        # as to be converted so that it is easier to read.
        await send_embed(ctx, author=f"{username}", author_pfp=user.avatar_url, thumbnail=user.avatar_url,
                         fields=[(f'**Username:**', usernameFull, True), (f'**Nickname:**', nickname, True),
                                 (f'**User ID:**', str(user.id), True),
                                 (f'**Registered:**', str(user.created_at.strftime("%b %d, %Y")), True),
                                 (f'**Joined Server:**', str(user.joined_at.strftime("%b %d, %Y")), True),
                                 (f'**Is Bot:**', isBot, True),
                                 (f'**Status:**', userStatus, True),
                                 (f'**Roles:**', userRoles, True)],
                         color=0x08d5f7)

    @commands.command(name='qr', brief='Responds with a QR code.',
                      description="Responds with a QR code of the data provided.")
    async def qr(self, ctx, *, text_or_url):
        # Send an echo of the keyword-only argument.
        request = requests.get(url=f'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={text_or_url}')
        await ctx.send(request.url)

    @commands.command(name='contributors', aliases=['contrib', 'contribs'],
                      brief='Responds with a list of contributors.',
                      description="Responds with a full list of project contributors.")
    async def contributors(self, ctx):
        contribs = "__**Leads**: Mag#7777, h3resjonny#0741, TheOneCheetah#3764, and Stu__\n \n" \
                   "**TG#5287** -> Graphics contributions. POG logo, Pogbot logo, welcome graphic. \n " \
                   "**Mag#7777** -> Developer. Foundational code contributions. \n **TheOneCheetah#3764** -> " \
                   "Developer. Foundational code contributions. \n **DJ DeHao#4627** -> Coder. Code contributions. (" \
                   "avatar command). \n **Panda Gummies#2155** -> Coder. Code contributions. (echo command). \n " \
                   "**ravenig#8429** -> Coder. Code contributions. (main check and run.sh). \n **Jaycon#4073** -> " \
                   "Coder. Code contributions. (icon command). "
        await send_embed(ctx, title="**Pogbot's Contributors**", description=contribs, color=0x08d5f7)

    @commands.command(name='covid', aliases=['coviddata', 'covid19', 'coronavirus', 'covid19data'],
                      brief='Responds with covid data.',
                      decription='Responds with covid data based on specified country.')
    async def covid(self, ctx, *, country=None):
        possible_us = ["us", "usa", "u.s", "u.s.", "u.s.a", "u.s.a.", "united states", "unitedstates", "united-states",
                       "united states of america", "unitedstatesofamerica", "united-states-of-america"]
        possible_uk = ["uk", "u.k", "u.k.", "united kingdom", "unitedkingdom", "united-kingdom"]
        possible_skorea = ["s. korea", "s.korea", "south korea", "southkorea"]

        if country is None:
            country = "World"
        elif country.lower() in possible_us:
            country = "usa"
        elif country.lower() in possible_uk:
            country = "uk"
        elif country.lower() in possible_skorea:
            country = "s. korea"

        request1 = session.get(url=f'https://www.worldometers.info/coronavirus/#main_table')
        request2 = session.get(url=f'https://www.worldometers.info/coronavirus/weekly-trends/#weekly_table')
        soup1 = BeautifulSoup(request1.text, 'html.parser')
        soup2 = BeautifulSoup(request2.text, 'html.parser')

        covid_data = soup1.find_all(id="main_table_countries_today")
        covid_change = soup2.find_all(id="main_table_countries_today")

        selected_country = None
        iter = 0
        for countries in covid_data[0].find_all('tr'):
            iter += 1
            if iter >= 9:
                data = countries.find_all('td')
                for value in range(0, len(data)):
                    data[value] = data[value].get_text()
                    if data[value] == '':
                        data[value] = 'N/A'
                if country.lower() == data[1].lower():
                    selected_country = {'Country': data[1], 'Total Cases': data[2], 'New Cases': data[3],
                                        'Total Deaths': data[4],
                                        'New Deaths': data[5], 'Total Recovered': data[6], 'Active Cases': data[8],
                                        'Critical Cases': data[9]}
                    break
        if selected_country is not None:
            iter = 0
            for countries in covid_change[0].find_all('tr'):
                iter += 1
                if iter >= 9:
                    data = countries.find_all('td')
                    if data[1].get_text() == selected_country['Country']:
                        selected_country['Case Change'] = data[4].get_text()
                        selected_country['Death Change'] = data[8].get_text()
            await send_embed(ctx, title=f"{selected_country['Country']} Covid-19 Statistics", color=0x08d5f7,
                             fields=[(f"**Total Cases:**", selected_country["Total Cases"], True),
                                     (f"**New Cases:**", selected_country["New Cases"], True),
                                     (f"**Weekly Change:**", selected_country["Case Change"], True),
                                     (f"**Total Recovered:**", selected_country["Total Recovered"], True),
                                     (f"**Active Cases:**", selected_country["Active Cases"], True),
                                     (f"**Critical Cases:**", selected_country["Critical Cases"], True),
                                     (f"**Total Deaths:**", selected_country["Total Deaths"], True),
                                     (f"**New Deaths:**", selected_country["New Deaths"], True),
                                     (f"**Weekly Change:**", selected_country["Death Change"], True)],
                             footer="Data via worldometers.info", thumbnail="https://i.imgur.com/kYANkld.jpg")
        else:
            await send_embed(ctx, description="<:Pogbot_X:850089728018874368> **Country Not Found**", color=0x08d5f7)

    @commands.command(name="snipe")
    async def snipe(self, ctx):
        check_snipes(ctx.author.guild.id)
        Message = get_db_item(ctx.author.guild.id, "snipes", "Message")
        MessageID = get_db_item(ctx.author.guild.id, "snipes", "MessageID")
        Author = get_db_item(ctx.author.guild.id, "snipes", "Author")
        AuthorAvatar = get_db_item(ctx.author.guild.id, "snipes", "AuthorAvatar")
        TimeStamp = get_db_item(ctx.author.guild.id, "snipes", "Timestamp")

        Author = decodebase64(Author)
        Message = decodebase64(Message)

        if Message != "None":
            await send_embed(ctx, author=f"{Author}", author_pfp=AuthorAvatar,
                             description=Message,
                             color=0x08d5f7,
                             timestamp=datetime.strptime(TimeStamp, '%Y-%m-%d %H:%M:%S.%f'),
                             footer=f"Message ID: {MessageID}\nDeleted")


def setup(bot):
    bot.add_cog(Commands(bot))
