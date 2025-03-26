import discord
from discord.ext import commands

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

bot.run("YOUR_BOT_TOKEN")