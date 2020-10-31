import discord
from discord.ext import commands
from datetime import datetime
import requests
import pytz
from tzwhere import tzwhere
import string
import random


bot = commands.Bot(command_prefix='!')
@bot.event
async def on_ready():
    print(f"""{bot.user} has connected at {datetime.now().strftime("%a, %m/%d/%Y, %I:%M:%S %p")}""")
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game("!hunterbot for commands"))

@bot.command()
async def ping(ctx):
    await ctx.send(f"ping {round(bot.latency * 1000)}ms")

@bot.command()
async def clear(ctx, amount=1):
    await ctx.channel.purge(limit=amount+1)

@bot.event
async def on_message(message):
    if message.content.startswith('!'):
        await bot.process_commands(message)
        return
    
# @bot.command(name='Hunter ||', description='Help for Commands of This bot')
@bot.command()
async def hunterbot(ctx):
    "!hunterbot for help with commands"
    embed = discord.Embed(
        title='This Bot Was Created To Make Your Life Easier, If You Have Any Idea Or Problem, Do Not Hesitate To Express It',
        description="Commands", color=0xCC0066)
    embed.set_author(name="Created By Hunter Mol")
    embed.add_field(name="**`!ig`**", value="Provides info on instgram profile", inline=False)
    embed.add_field(name="**`!info`**", value="Provides the time, and weather for any city", inline=False)
    embed.add_field(name="**`!m`**", value="Returns input in spongebob text", inline=False)

    embed.add_field(name="**`!pwd`**", value="Generates a random password based on your inputted length", inline=False)
    embed.add_field(name="**`!hunterbot`**", value="Shows The Commamds", inline=True)

    await ctx.send(embed=embed)


@bot.command()
async def ig(ctx,*, ig_name):
    account_name = ig_name.lstrip("!ig")
    account_name.strip()
    full_name = ''.join(ig_name)
    print(full_name)
    url = "https://www.instagram.com/{}/?__a=1".format(account_name)
    r = requests.get(url)
    stcode = r.status_code
    if stcode == 200:
        res = r.json()
        followers = ("Followers: {}".format(res['graphql']['user']['edge_followed_by']['count']))
        following = ("Following: {}".format(res['graphql']['user']['edge_follow']['count']))
        posts = ("Posts: {}".format(len(res["graphql"]['user']["edge_owner_to_timeline_media"]['edges'])))
        likes = sum([res["graphql"]['user']["edge_owner_to_timeline_media"]['edges'][i]["node"]["edge_liked_by"]['count'] for i in range(len(res["graphql"]['user']["edge_owner_to_timeline_media"]['edges']))])
        total_likes = "Total Likes: {}".format(likes)
        posts_number = posts.strip('Posts:')
        with open("instgram.txt", "a") as f:
            f.write(f"""{full_name} was looked up on {datetime.now().strftime("%a, %m/%d/%Y, %I:%M:%S %p")}""")
            f.write("\n")

        if int(posts_number) > 0 and likes == 0:
            await ctx.send(f"""Profile Status for {account_name}. {followers} |  {following} | {posts} | {total_likes} | Private account: True. """)
        elif int(posts_number) == 0 and likes == 0:
            ig_embed = discord.Embed(tile=f"{account_name}", description=f"Data for {account_name}", color=0xCC0066)
            ig_embed.add_field(name="Followers", value=f"{followers}")
            ig_embed.add_field(name="Following", value=f"{following}")
            ig_embed.add_field(name="Number of posts", value=f"{posts}")
            ig_embed.add_field(name="Private Account", value=f"N/A")
            await ctx.send(embed=ig_embed)
        else:
            ig_embed = discord.Embed(tile=f"{account_name}", description=f"Data for {account_name}", color=0xCC0066)
            ig_embed.add_field(name="Followers", value=f"{followers}")
            ig_embed.add_field(name="Following", value=f"{following}")
            ig_embed.add_field(name="Number of posts", value=f"{posts}")
            ig_embed.add_field(name="Total likes", value=f"{total_likes}")
            ig_embed.add_field(name="Public Account", value=f"True")
            await ctx.send(embed=ig_embed)
    else:
        await ctx.send("Incorrect Ig Name.")

with open('colors.txt', encoding='utf-8') as file:
    color = file.read().split('\n')
list_color = [x.replace('#', '0x') for x in color]  

@bot.command()
async def info(ctx, city):
        city.lstrip("!info")
        edited_town = city.strip()
        if edited_town == "abu dhabi":
            await ctx.send("Error. Improper input detected. We Don't Waste Our Data On irrelevancy. Warning num: 1")
        else:
            await ctx.send("Requesting Data....")
            try:
                def kelvin_to_celcius(temp: float) -> int:
                    k = float(temp)
                    c = k - 273.15
                    return int(c)

                def timezone(lt, lng):
                    w = tzwhere.tzwhere()
                    return datetime.now(pytz.timezone(w.tzNameAt(lt, lng))).strftime('%a %I:%M %p')

                def api_weather(edited_town):
                    resp = requests.get(
                        f'https://openweathermap.org/data/2.5/find?q={edited_town}&appid=439d4b804bc8187953eb36d2a8c26a02&units=metric')
                    data = resp.json()
                    resp.raise_for_status()
                    main_data = data ['list'] [0] ['main']
                    weather = data ['list'] [0] ['weather'] [0]

                    coord = data ['list'] [0] ['coord']
                    lat = coord ['lat']
                    lon = coord ['lon']
                    time = timezone(lat, lon)
                    feels_like = kelvin_to_celcius(main_data ['feels_like'])
                    humidity = main_data ['humidity']
                    temp = kelvin_to_celcius(main_data ['temp'])
                    name = data ['list'] [0] ['name']
                    description = weather ['description']
                    wind = data ['list'] [0] ['wind'] ['speed']
                    return time, feels_like, humidity, temp, description, wind, name

                time, feels_like, humidity, temp, description, wind, name = api_weather(edited_town)


                weather_embed = discord.Embed(tile=f"{name}", description=f"Live Data for {name}", color=0xCC0066)
                weather_embed.add_field(name="Time", value=f"{time}")
                weather_embed.add_field(name="Temperture", value=f"{temp}°C")
                weather_embed.add_field(name="Feels Like", value=f"{feels_like}°C")
                weather_embed.add_field(name="Weather", value=f"{description}")

                await ctx.channel.purge(limit=1)
                await ctx.send(embed=weather_embed)

            except:
                exception_embed = discord.Embed(title="Error", description="An error has occurrd, check the name of the city or the spelling.", color=0xFF9E00)
                await ctx.channel.purge(limit=1)
                await ctx.send(embed=exception_embed)

@bot.command()
async def pwd(ctx, password_length):
    password_length.lstrip("!pwd")
    print(password_length)
    pad_length = password_length.strip()
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits + '!@#$%^&*()+_'
    try:
        generated_pwd = ''.join(random.choice(chars) for i in range(int(pad_length)))
        await ctx.send(f"Pwd: `{generated_pwd}`")
    except:
        await ctx.send(f"Unable to generate password. Must be 2000 or fewer in lenth.")

@bot.command()
async def m(ctx,*, text):
    input = ''.join(text)
    words = []
    for i in range(len(input)):
        x = input[i]
        if random.randint(1,2) == 1:
            words.append(x.upper())
        else:
            words.append(x.lower())
    final_sentence = ''.join(words)
    await ctx.channel.purge(limit=1)
    await ctx.send(final_sentence)




bot.run(token)

