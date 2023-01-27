import discord
from discord.ext import commands
from discord import app_commands
import requests
from bs4 import BeautifulSoup


channel_id = 808495138686369832
client = commands.Bot(command_prefix= "bor ", intents=discord.Intents.all())

token = "token"

#urls 
URL_PL = "https://kur.doviz.com/serbest-piyasa/polonya-zlotisi"
URL_EUR = "https://kur.doviz.com/serbest-piyasa/euro"
URL_USD = "https://www.bloomberght.com/doviz/dolar"

url_genel = "https://www.x-rates.com/calculator/?from=A&to=B&amount=1"

#emojis

down = "<:dcdown:824159108533714984>"
up = "<:dcup:824158961904517122>"
emoji_usd = "<:dcdollar:823611563167973437>"
emoji_eu = "<:dcavro:823595392527761499>"

@client.event
async def on_ready():
    synced = await client.tree.sync()
    await client.change_presence(status=discord.Status.online, activity=discord.Game("stonks"))
    print("BORsa is ready to go")
    print(f"Commands synced: {len(synced)} " )

#currency exchanger
@client.command(description="number + from + to -- need to use uppercase for currencies")
async def change(ctx,*,text):
    embed = discord.Embed(
        colour = discord.Colour.green()
    )
   
    text = text.split(" ")
    number = float(text[0])
    ffrom = text[1]
    to = text[2]

    modified_url = url_genel.replace('A', ffrom)
    modified_url = modified_url.replace('B' , to)
    page = requests.get(modified_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    change_eq = soup.find('div', {'class' : 'ccOutputBx'} ).text.replace("\n", " ")
    change_eq_split = change_eq.split(" ")
    change_rate = change_eq_split[4]
    
    result = number * float(change_rate)

    embed.add_field(name=f"from {ffrom} to {to}: ",value= change_eq + "\n" + f"{result:.2f}" + " " + to)
    await ctx.channel.send(embed=embed)
    

@client.tree.command(name="borsa", description="Genel kurları gösterir")
async def borsa(interaction: discord.Interaction):
    # channel = client.get_channel(749685025628356769)
    total_embed = discord.Embed(
        title = "Genel Değerler",
        description = "Kurlar ufak farklılıklar gösterebilir",
        colour = discord.Colour.dark_green()
    )

    page = requests.get(URL_USD)
    soup = BeautifulSoup(page.content, 'html.parser')
    part1 = soup.find(id = "dolar").get_text(strip="True")
    change_usd = soup.find("li", {"class" : "up live-dolar"})
    
    dolar_kur = part1[7:-7]

    if change_usd != "None":
        total_embed.add_field(name = "Dolar Kuru " + emoji_usd, value = dolar_kur + " " + up,inline = False)   
    else:
        total_embed.add_field(name = "Dolar Kuru " + emoji_usd, value = dolar_kur + " " + down,inline = False) 

    page = requests.get(URL_PL)
    soup = BeautifulSoup(page.content, "html.parser")   
    zlot_kuru = soup.find(class_="text-xl font-semibold text-white").get_text()
    change_pl = soup.find( "span", {"data-socket-key" : "PLN"}).prettify()

    
    if "change up" in change_pl:
        total_embed.add_field(name = "Zloty Kuru " + "🇵🇱", value = zlot_kuru + " " + up ,inline = False)
    else:
        total_embed.add_field(name = "Zloty Kuru " + "🇵🇱", value = zlot_kuru + " " + down ,inline = False)

    page = requests.get(URL_EUR)
    soup = BeautifulSoup(page.content, "html.parser")
    avro_kuru = soup.find(class_="text-xl font-semibold text-white").get_text()
    change = soup.find( "span", {"data-socket-key" : "EUR", "data-socket-attr":"c"}).prettify()
    

    if "change up" in change:
        total_embed.add_field(name = "Euro Kuru " + emoji_eu, value = avro_kuru + " " + up ,inline = False)
    else:
        total_embed.add_field(name = "Euro Kuru " + emoji_eu, value = avro_kuru + " " + down ,inline = False)
    
    imgURL = "https://global-uploads.webflow.com/5f1f2fa30a2ea56d717cc952/601845cebde6203ac22aa936_stonks.jpg"
    total_embed.set_thumbnail(url=imgURL)

    URL = "https://www.doviz.com/kripto-paralar/bitcoin"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    btc_kur = soup.find(class_="text-xl font-semibold text-white").get_text()
    change_btc = soup.find( "div", {"data-socket-key" : "bitcoin", "data-socket-attr":"c"}).prettify()
    btc_try = soup.find("div",{"class":"text-md font-semibold text-white mt-4"}).get_text()

    if "up" in change_btc:
        total_embed.add_field(name = "Bitcoin Kuru 🛰️" , value = btc_kur + " " + up + "\n" + btc_try + " " + up ,inline = False)
        
    else:
        total_embed.add_field(name = "Bitcoin Kuru 🛰️" , value = btc_kur + " " + down + "\n" + btc_try + " " + down,inline = False)

    URL = "https://altin.doviz.com/gram-altin"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    gold_kur = soup.find("div", {"data-socket-key" : "gram-altin", "data-socket-attr":"s"}).get_text().strip()
    change_gold = soup.find("div", {"data-socket-key" : "gram-altin", "data-socket-attr":"c"}).prettify()
    
    if "up" in change_gold:
        total_embed.add_field(name = "Gram Altın 💰" , value = gold_kur + " " + up, inline = False)
        
    else:
        total_embed.add_field(name = "Gram Altın 💰" , value = gold_kur + " " + down, inline = False)

    await interaction.response.send_message(embed= total_embed)
# """""


@client.tree.command(name = "dt",description="dolardan tl'ye dönüşüm. /dt <amount>")
async def dt(interaction: discord.Interaction,text:str):
   
    embed_up = discord.Embed(
        colour = discord.Colour.green()
    )

    embed_down = discord.Embed(
        colour = discord.Colour.red()
    )

    URL_usd = "https://www.bloomberght.com/doviz/dolar"
    page = requests.get(URL_usd)
    soup = BeautifulSoup(page.content, 'html.parser')
    part1 = soup.find(id = "dolar").get_text(strip="True")
    change = soup.find("li", {"class" : "up live-dolar"})
    dolar_kur = part1[7:-7]
    dolar_kur = dolar_kur.replace(",",".")
    tl_çeviri = float(dolar_kur) * int(text)
    
    if change != "None":
        embed_up.add_field(name = "DOLAR --> TL " + emoji_eu, value = f"{text} DOLAR = {tl_çeviri} TL",inline = False)
        await interaction.response.send_message(embed=embed_up)
    else:
        embed_down.add_field(name = "DOLAR --> TL " + emoji_eu, value = f"{text} DOLAR = {tl_çeviri} TL" ,inline = False)
        await interaction.response.send_message(embed=embed_down)



@client.tree.command(name= "et", description="Currency changer from euro to tl. /et <amount>")
async def et(interaction: discord.Interaction,text:str):
    embed_up = discord.Embed(
        colour = discord.Colour.green()
    )

    embed_down = discord.Embed(
        colour = discord.Colour.red()
    )

    page = requests.get(URL_EUR)
    soup = BeautifulSoup(page.content, "html.parser")
    avro_kuru = soup.find(class_="text-xl font-semibold text-white").get_text()
    avro_kuru = avro_kuru.replace(",",".")
    change = soup.find( "span", {"data-socket-key" : "EUR", "data-socket-attr":"c"}).prettify()
    tl_çeviri = float(avro_kuru) * float(text)

    if "change up" in change:
        embed_up.add_field(name = "EURO --> TL " + emoji_eu, value = f"{text} EURO = {tl_çeviri} TL",inline = False)
        await interaction.response.send_message(embed=embed_up)
    else:
        embed_down.add_field(name = "EURO --> TL " + emoji_eu, value = f"{text} EURO = {tl_çeviri} TL" ,inline = False)
        await interaction.response.send_message(embed=embed_down)

    
    

@client.tree.command(name= "zt", description="Currency changer from Zloty to tl. /zt <amount>")
async def zt(interaction: discord.Interaction,text:str):
    embed_up = discord.Embed(
        colour = discord.Colour.green()
    )

    embed_down = discord.Embed(
        colour = discord.Colour.red()
    )
    page = requests.get(URL_PL)
    soup = BeautifulSoup(page.content, "html.parser")   
    zlot_kuru = soup.find(class_="text-xl font-semibold text-white").get_text()
    zlot_kuru = zlot_kuru.replace(",",".")
    tl_çeviri = float(zlot_kuru) * int(text)

    change_pl = soup.find( "span", {"data-socket-key" : "PLN"}).prettify()
    if "change up" in change_pl:
        embed_up.add_field(name = "Zloty --> TL: " + "🇵🇱", value = zlot_kuru + " " ,inline = False)
        await interaction.response.send_message(embed=embed_up)
    else:
        embed_down.add_field(name = "Zloty --> TL: " + "🇵🇱", value = f"{text} Zlot = {tl_çeviri} TL" ,inline = False)
        await interaction.response.send_message(embed=embed_down)
    


# """""

client.run(token)



