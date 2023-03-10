import discord
from discord.ext import commands
from discord import app_commands
import requests
from bs4 import BeautifulSoup
import pandas as pd


channel_id = 808495138686369832
client = commands.Bot(command_prefix= "bor ", intents=discord.Intents.all())

token = "token"

# urls 
URL_PL = "https://kur.doviz.com/serbest-piyasa/polonya-zlotisi"
URL_EUR = "https://kur.doviz.com/serbest-piyasa/euro"
URL_USD = "https://www.bloomberght.com/doviz/dolar"

url_genel = "https://www.x-rates.com/calculator/?from=A&to=B&amount=1"
url_for_embed = "https://www.x-rates.com/table/?from=A&amount=1"

# emojiler

down = "<:dcdown:824159108533714984>"
up = "<:dcup:824158961904517122>"
emoji_usd = "<:dcdollar:823611563167973437>"
emoji_eu = "<:dcavro:823595392527761499>"

# shows ready status
@client.event
async def on_ready():
    synced = await client.tree.sync()
    await client.change_presence(status=discord.Status.online, activity=discord.Game("stonks"))
    print("BORsa is ready to go")
    print(f"Commands synced: {len(synced)} " )

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

    embed.add_field(name=f"from {ffrom} to {to}: ",value= change_eq + "\n" + f"**{result:.2f}**" + " " + to)
    await ctx.channel.send(embed=embed)
    
# slash commands
@client.tree.command(name="borsa", description="top 11 currency rates for the given currency")
async def borsa(interaction: discord.Interaction, text:str):
    
    total_embed = discord.Embed(
        title = f"Exchange Rates for {text}",
        description = "Rates may vary slightly",
        colour = discord.Colour.dark_green()
    )

    imgURL = "https://global-uploads.webflow.com/5f1f2fa30a2ea56d717cc952/601845cebde6203ac22aa936_stonks.jpg"
    total_embed.set_thumbnail(url=imgURL)

    if (text != 'TRY'):
        #get currency names and respected rates, put them in pandas dataframe
        modified_url = url_for_embed.replace('A',text)
        page = requests.get(modified_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        table = soup.find('table', class_='ratesTable')
        tr_rates = []

        for tr in soup.find_all('tr'):
            if 'Turkish Lira' in tr.text:
                tr_exchange = tr.find_all('td', class_='rtRates')
                for exchange_rate in tr_exchange:
                    tr_rates.append(exchange_rate.text)
        
        df = pd.DataFrame(columns=['Currencies', 'change rate'])
        for row in table.tbody.find_all('tr'):    
        # Find all data for each column
            columns = row.find_all('td')
            if (columns != []):
                currencies = columns[0].text
                change_rate = columns[2].text

                df = df.append({'Currencies': currencies, 'change rate': change_rate}, ignore_index=True)

        
        for i in range(0,10):
            value = (df['Currencies'][i],df['change rate'][i])
            currency = value[0]
            rate = value[1]
            if (i % 2 == 1):
                total_embed.add_field(name=currency, value=rate[:6])
                total_embed.add_field(name='\u200b',value='\u200b')
            else:
                total_embed.add_field(name=currency, value=rate[:6])
            
        total_embed.add_field(name="Turkish Lira", value=tr_rates[1][:-3])
        await interaction.response.send_message(embed=total_embed)

    # for TRY based general rates
    else:

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
            total_embed.add_field(name = "Zloty Kuru " + "????????", value = zlot_kuru + " " + up ,inline = False)
        else:
            total_embed.add_field(name = "Zloty Kuru " + "????????", value = zlot_kuru + " " + down ,inline = False)

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
            total_embed.add_field(name = "Bitcoin Kuru ???????" , value = btc_kur + " " + up + "\n" + btc_try + " " + up ,inline = False)
            
        else:
            total_embed.add_field(name = "Bitcoin Kuru ???????" , value = btc_kur + " " + down + "\n" + btc_try + " " + down,inline = False)

        URL = "https://altin.doviz.com/gram-altin"
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        gold_kur = soup.find("div", {"data-socket-key" : "gram-altin", "data-socket-attr":"s"}).get_text().strip()
        change_gold = soup.find("div", {"data-socket-key" : "gram-altin", "data-socket-attr":"c"}).prettify()
        
        if "up" in change_gold:
            total_embed.add_field(name = "Gram Alt??n ????" , value = gold_kur + " " + up, inline = False)
            
        else:
            total_embed.add_field(name = "Gram Alt??n ????" , value = gold_kur + " " + down, inline = False)

        await interaction.response.send_message(embed= total_embed)


@client.tree.command(name = "dt",description="dolardan tl'ye d??n??????m. /dt <amount>")
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
    tl_??eviri = float(dolar_kur) * int(text)
    
    if change != "None":
        embed_up.add_field(name = "DOLAR --> TL " + emoji_eu, value = f"{text} DOLAR = {tl_??eviri} TL",inline = False)
        await interaction.response.send_message(embed=embed_up)
    else:
        embed_down.add_field(name = "DOLAR --> TL " + emoji_eu, value = f"{text} DOLAR = {tl_??eviri} TL" ,inline = False)
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
    tl_??eviri = float(avro_kuru) * float(text)

    if "change up" in change:
        embed_up.add_field(name = "EURO --> TL " + emoji_eu, value = f"{text} EURO = {tl_??eviri} TL",inline = False)
        await interaction.response.send_message(embed=embed_up)
    else:
        embed_down.add_field(name = "EURO --> TL " + emoji_eu, value = f"{text} EURO = {tl_??eviri} TL" ,inline = False)
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
    tl_??eviri = float(zlot_kuru) * int(text)

    change_pl = soup.find( "span", {"data-socket-key" : "PLN"}).prettify()
    if "change up" in change_pl:
        embed_up.add_field(name = "Zloty --> TL: " + "????????", value = zlot_kuru + " " ,inline = False)
        await interaction.response.send_message(embed=embed_up)
    else:
        embed_down.add_field(name = "Zloty --> TL: " + "????????", value = f"{text} Zlot = {tl_??eviri} TL" ,inline = False)
        await interaction.response.send_message(embed=embed_down)
    
@client.tree.command(name="cs", description="Cheatsheet for currency name codes")
async def cs(interaction: discord.Interaction):
    embed = discord.Embed(
        color = discord.colour.Color.dark_gold(),
        title= "Currency Codes" ,
        url="https://taxsummaries.pwc.com/glossary/currency-codes"
    )

    embed.set_thumbnail(url="https://taxsummaries.pwc.com/-/media/world-wide-tax-summaries/dev/new-pwclogo.ashx?rev=857d31d9188a45cb89c2a139fca9bbc2&revision=857d31d9-188a-45cb-89c2-a139fca9bbc2&hash=185803B13B63A76ED59B9489B23256389302FCC5")
    embed.add_field(name="Euro", value="EUR",inline=False)
    embed.add_field(name="Turkish Lira", value="TRY",inline=False)
    embed.add_field(name="US Dollar", value="USD",inline=False)
    embed.add_field(name="Zloty", value="PLN",inline=False)
    embed.add_field(name="Canadian Dollar", value="CAD",inline=False)
    embed.add_field(name="Pound Sterling", value="GBP",inline=False)
    embed.add_field(name="Japanese Yen", value="JPY",inline=False)
    embed.set_footer(text="For more codes, please click the title")

    await interaction.response.send_message(embed=embed)


client.run(token)
