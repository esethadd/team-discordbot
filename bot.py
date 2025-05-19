import discord
from discord.ext import commands
from discord import Embed
from collections import defaultdict, Counter
import aiohttp

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# store user filters by user ID
user_filters = {}

API_URL = //insert API URL here

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

def reset_filters(user_id):
    user_filters[user_id] = {
        "salary": None,
        "remote": None
    }

def get_filter_summary(user_id):
    filters = user_filters.get(user_id, {})
    salary = filters.get("salary")
    remote = filters.get("remote")

    summary = []
    if salary:
        summary.append(f"💰 Salary: ${salary[0]} - ${salary[1]}")
    if remote is not None:
        summary.append(f"🏠 Remote: {'On' if remote else 'Off'}")

    return "\n".join(summary) if summary else "No filters applied."

@bot.command()
async def filter(ctx):
    user_id = ctx.author.id
    if user_id not in user_filters:
        reset_filters(user_id)

    embed = Embed(
        title="🧰 Job Filter Options",
        description="Use these commands to narrow or reset your job search filters.",
        color=0x3498db
    )

    embed.add_field(
        name="💰 Salary Range Filter",
        value=(
            "`/filter_salary [min_amount] [max_amount]`\n"
            "🔸 Example: `/filter_salary 30000 70000`\n"
            "Shows jobs between $30,000 and $70,000."
        ),
        inline=False
    )

    embed.add_field(
        name="🏠 Remote Work Filter",
        value=(
            "`/filter_remote [on/off]`\n"
            "🔸 Example: `/filter_remote on`\n"
            "Only includes remote-friendly jobs."
        ),
        inline=False
    )

    embed.add_field(
        name="♻️ Reset Filters",
        value=(
            "`/filter_clear`\n"
            "🔸 Resets all applied filters so future searches return full results."
        ),
        inline=False
    )

    embed.add_field(
        name="📋 Current Filters",
        value=get_filter_summary(user_id),
        inline=False
    )

    embed.set_footer(text="Filters remain active until updated or cleared.")
    await ctx.send(embed=embed)

@bot.command()
async def filter_remote(ctx, toggle: str):
    user_id = ctx.author.id
    if user_id not in user_filters:
        reset_filters(user_id)

    if toggle.lower() not in ["on", "off"]:
        await ctx.send("❌ Invalid input. Use `/filter remote on` or `/filter remote off`.")
        return

    user_filters[user_id]["remote"] = toggle.lower() == "on"
    status = "enabled" if toggle.lower() == "on" else "disabled"
    await ctx.send(f"🏠 Remote job filter {status}.")

@bot.command()
async def filter_clear(ctx):
    user_id = ctx.author.id
    reset_filters(user_id)
    await ctx.send("♻️ All filters have been cleared.")

bot_stats = {
    "total_jobs_found": 0,
    "keyword_counter": Counter(),
    "industry_counter": Counter(),
    "active_subscriptions": defaultdict(list)  # user_id -> list of keywords/locations
}

@bot.command()
async def stats(ctx):
    total = bot_stats["total_jobs_found"]
    top_keywords = bot_stats["keyword_counter"].most_common(3)
    top_industries = bot_stats["industry_counter"].most_common(3)
    subs = len(bot_stats["active_subscriptions"])

    embed = Embed(
        title="📊 Job Search Stats",
        description="Here's what the community has been looking for!",
        color=0x4CAF50
    )

    embed.add_field(name="🧾 Total Jobs Found", value=str(total), inline=False)

    embed.add_field(
        name="🔍 Top Keywords",
        value="\n".join(f"{kw} ({count})" for kw, count in top_keywords) or "None",
        inline=False
    )

    embed.add_field(
        name="🏭 Top Industries",
        value="\n".join(f"{ind} ({count})" for ind, count in top_industries) or "None",
        inline=False
    )

    embed.add_field(name="📬 Active Subscriptions", value=str(subs), inline=False)

    await ctx.send(embed=embed)

async def search_jobs(keywords, location=None, user_id=None):
    query = {
        "keywords": keywords
    }

    if location:
        query["location"] = location

    # Apply filters from the user's session
    filters = user_filters.get(user_id, {})
    if filters.get("remote") is not None:
        query["remote"] = filters["remote"]
    if filters.get("salary"):
        query["salary_min"], query["salary_max"] = filters["salary"]

    headers = {
        "Authorization": "Bearer YOUR_API_KEY"  # Replace with your actual auth method
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL, params=query, headers=headers) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            return data.get("jobs", [])  # Adapt to your API structure

@bot.command()
async def find(ctx, *, args):
    user_id = ctx.author.id
    if user_id not in user_filters:
        reset_filters(user_id)

    parts = args.split()
    if len(parts) < 2:
        await ctx.send("❌ Please use the format `/find [keywords] [location]`.")
        return

    keywords = " ".join(parts[:-1])
    location = parts[-1]

    jobs = await search_jobs(keywords, location, user_id)
    if not jobs:
        await ctx.send("🔍 No jobs found for your search.")
        return

    embed = Embed(title=f"🔎 Results for '{keywords}' in {location}", color=0x1abc9c)
    for job in jobs[:5]:  # limit to 5 results
        embed.add_field(
            name=job["title"],
            value=f"**Company:** {job['company']}\n**Location:** {job['location']}\n[Apply]({job['link']})",
            inline=False
        )
        bot_stats["total_jobs_found"] += 1
        bot_stats["keyword_counter"][keywords] += 1
        bot_stats["industry_counter"][job.get("industry", "Unknown")] += 1

    await ctx.send(embed=embed)

@bot.command()
async def latest(ctx, industry: str):
    user_id = ctx.author.id
    if user_id not in user_filters:
        reset_filters(user_id)

    jobs = await search_jobs(industry, user_id=user_id)
    if not jobs:
        await ctx.send("🆕 No new job postings found in that industry.")
        return

    embed = Embed(title=f"🆕 Latest jobs in {industry}", color=0xff9800)
    for job in jobs[:5]:
        embed.add_field(
            name=job["title"],
            value=f"**Company:** {job['company']}\n**Location:** {job['location']}\n[Apply]({job['link']})",
            inline=False
        )
        bot_stats["total_jobs_found"] += 1
        bot_stats["industry_counter"][industry] += 1

    await ctx.send(embed=embed)

@bot.command()
async def company(ctx, *, company_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/company", params={"name": company_name}) as resp:
            if resp.status != 200:
                await ctx.send("❌ Couldn't fetch data for that company.")
                return
            data = await resp.json()

    embed = Embed(title=f"🏢 {company_name}", color=0x9b59b6)
    for job in data.get("jobs", [])[:3]:
        embed.add_field(
            name=job["title"],
            value=f"{job['location']}\n[Apply]({job['link']})",
            inline=False
        )
    await ctx.send(embed=embed)


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
    embed.add_field(name="👨‍💻 Database Designer", value="Brenden Toussant", inline=True)
    embed.set_footer(text="Type /help to view available commands.")
    await ctx.send(embed=embed)

bot.run("YOUR_BOT_TOKEN")