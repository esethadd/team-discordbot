import discord
from discord.ext import commands
from discord import Embed

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

API_URL = //insert API URL here

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def beginposting(ctx):
    await ctx.send("The bot has received the '!beginposting' command and will start posting jobs.")

@bot.command()
async def help(ctx):
    await ctx.send("The bot has received the '!help' command and will display a help message.")

@bot.command()
async def stopposting(ctx):
    await ctx.send("The bot has received the '!stopposting' command and will stop posting jobs.")

@bot.command()
async def changejobtype(ctx, category: str):
    await ctx.send(f"The bot has received the '!changejobtype' command and will now post jobs in the {category} category.")

@bot.command()
async def jobs(ctx, category: str):
    response = requests.get(f"{API_URL}/jobs/{category}")
    if response.status_code == 200:
        await ctx.send("Failed to fetch job listings. Try again later.")
        return
    
    jobs = response.json()[1:6]
    job_results = []

    for job in jobs:
        if category.lower() in job.get("tags", []):
            job_results.append(f"**{job['position']}** at {job['company']} - [Apply Here]({job['url']})")

    if job_results:
        await ctx.send("\n".join(job_results))
    else:
        await ctx.send("No jobs found in that category.")

@bot.command()
async def help_command(ctx, name="help"):
    help_text = """
**📘 Available Commands:**

`/company [company_name]`  
🔹 Shows recent job openings and reviews for the specified company.

`/find [keywords] [location]`  
🔹 Searches for jobs based on the given role and location.  
🔸 Example: `/find software_developer Georgia`

`/latest [industry]`  
🔹 Finds the latest and most popular job postings in the given industry.  
🔸 Example: `/latest tech`

`/subscribe [keywords] [location]`  
🔹 Get notified (DM or @mention) when new jobs match your query.  
🔸 Example: `/subscribe data analyst remote`

`/unsubscribe [keywords] [location]`  
🔹 Stops job alerts for the specified criteria.  
🔸 Example: `/unsubscribe data analyst remote`

`/filter salary [min] [max]`  
🔹 Filters job results by salary range.  
🔸 Example: `/filter salary 30000 70000`

`/filter remote [on/off]`  
🔹 Toggles remote job filtering.  
🔸 Example: `/filter remote on`

`/stats`  
🔹 Shows total jobs found, top keywords, and leading industries.

`/about`  
🔹 Learn about the bot's purpose and developer info.

`/help`  
🔹 Displays this help message.
"""
    await ctx.send(help_text)

@bot.command()
async def about(ctx):
    embed = Embed(
        title="🤖 About This Bot",
        description="Your personalized assistant for job searching!",
        color=0x00b0f4
    )
    embed.add_field(
        name="📌 Features",
        value=(
            "• Search jobs by company, keyword, or industry\n"
            "• Filter results by salary and remote options\n"
            "• Subscribe for alerts when matching jobs appear\n"
            "• View stats on top industries and keywords"
        ),
        inline=False
    )
    embed.add_field(name="👨‍💻 Bot Creator", value="Lauren Rousell", inline=True)
    embed.set_footer(text="Type /help to view available commands.")
    await ctx.send(embed=embed)

bot.run("YOUR_BOT_TOKEN")