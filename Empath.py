import discord
from discord.ext import commands
from chat import AI
from datetime import datetime, timedelta
from dotenv import load_dotenv
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
import os
import random
from discord.ext import tasks
load_dotenv()

chatbot = {}

token = os.getenv('DISCORD_TOKEN')

# Create a new bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

category_id = 1092547772252700773
channel_id = 1092513860495347763


current_mood = ""
reminders = {}
mood_tracker = {}
current_thoughts = []
current_advice = []
progress_array = []
scheduler = BackgroundScheduler()
scheduler.start()


@bot.tree.command(name="mood", description="How are you feeling today? Please share as much or as little as you'd like.")
async def report_mood(interaction: discord.Interaction, mood: str):
    global current_mood

    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    current_mood = mood

    mood_tracker.setdefault(interaction.user.id, []).append(current_mood)

    await interaction.response.send_message(f"Thank you for sharing your mood with me! You can now talk to the bot about {current_mood} and it will have that in context.", ephemeral=True)



@bot.tree.command(name="moodtracking", description="Track all your previous moods.")
async def view_moods(interaction: discord.Interaction):
    try:
        moods = mood_tracker[interaction.user.id]
        message = "Moods Reported:\n"
        for i, mood in enumerate(reversed(moods)):
            message += f"• {mood} (reported {i+1} {'day' if i==0 else 'days' if i<7 else 'weeks'} ago)\n"
    except KeyError:
        message = "No mood reported yet"
    await interaction.response.send_message(message, ephemeral=True)


@bot.tree.command(name="thoughts", description="What's on your mind? I'm here to listen without judgment.")
async def share_thoughts(interaction: discord.Interaction, thoughts: str):
    global current_thoughts
    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    current_thoughts = thoughts
	
    await interaction.response.send_message(f"Thank you for sharing with me! You can now talk to the bot about {current_thoughts} and it will have that in context.", ephemeral=True)

    
@bot.tree.command(name="advice", description="How can I support you? Please share your concerns or goals.")
async def request_advice(interaction: discord.Interaction, advice: str):
    global current_advice
    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    current_advice = advice
	
    await interaction.response.send_message(f"Thank you for sharing with me! You can now talk to the bot about {current_advice} and it will have that in context.", ephemeral=True)

@bot.tree.command(name="setreminder")
async def set_reminder(interaction: discord.Interaction, message: str, weeks: int, days: int, minutes: int):
    user_id = interaction.user.id
    if user_id not in chatbot:
        chatbot[user_id] = AI()
    await interaction.response.send_message("Setting your reminder...", ephemeral=True)

    remind_me_total_minutes = weeks * 7 * 24 * 60 + days * 24 * 60 + minutes
    remind_me_at = datetime.utcnow() + timedelta(minutes=remind_me_total_minutes)

    reminders[interaction.user.id] = {
    'user_id': interaction.user.id,
    'reminder_text': message,
    'remind_me': remind_me_total_minutes,
    'remind_me_at': remind_me_at,
}


    response = await chatbot[interaction.user.id].run(user_id=interaction.user.id, prompt=f"""
        Instructions: An AI assistant called EmpathAI developed by NovaLabs to provide helpful reminders and encourage your progress.
        Please generate a message confirming the reminder details provided and any motivational commentary or suggestions you think would be most impactful for the user.

        Context: The user {interaction.user.name} has requested a reminder to {message} in {weeks} weeks, {days} days, and {minutes} minutes.
        Reminder Details:
        {reminders[interaction.user.id]}

        User: {interaction.user.name}
    """)

    await interaction.followup.send(response, ephemeral=True)

# Function to run reminder
async def run_reminder(user_id: int, reminder_text: str):
    user = await bot.fetch_user(user_id)
    chatbot[user_id] = AI()
    response = await chatbot[user_id].run(user_id=user_id, prompt=f"""
        Instructions: An AI assistant called EmpathAI developed by NovaLabs to provide helpful reminders and encourage your progress.
        Please generate a message confirming the reminder details provided and any motivational commentary or suggestions you think would be most impactful for the user.

        Context: The user {user.name} has requested a reminder to {reminder_text}, this means that the reminder is done, reply to them.
        Reminder Details:
        {reminders[user_id]}

        User: {user.name}
    """)
    await user.send(response)
    del reminders[user_id]

@bot.tree.command(name="cancelreminder")
async def cancel_reminder(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_reminders = [(i, r) for i, r in enumerate(reminders.values()) if r.get('user_id') == user_id]

    if not user_reminders:
        await interaction.response.send_message("You don't have any reminders to cancel.", ephemeral=True)
        return

    pages = [user_reminders[i:i+10] for i in range(0, len(user_reminders), 10)]
    current_page = 0

    def get_embed():
        embed = discord.Embed(title="Your Reminders", color=0x00ff00)
        for i, reminder in pages[current_page]:
            embed.add_field(name=f"{i+1}. {reminder['reminder_text']}", value=f"Remind me in {reminder['remind_me']} minutes")
        return embed

    message = await interaction.response.send_message(embed=get_embed(), ephemeral=True)

    if len(pages) > 1:
        await message.add_reaction('◀️')
        await message.add_reaction('▶️')

        def check(reaction, user):
            return user == interaction.user and str(reaction.emoji) in ['◀️', '▶️']

        while True:
            try:
                reaction, _ = await bot.wait_for('reaction_add', timeout=60.0, check=check)
                if str(reaction.emoji) == '◀️':
                    current_page = (current_page - 1) % len(pages)
                    await message.edit(embed=get_embed())
                    await message.remove_reaction('◀️', interaction.user)
                elif str(reaction.emoji) == '▶️':
                    current_page = (current_page + 1) % len(pages)
                    await message.edit(embed=get_embed())
                    await message.remove_reaction('▶️', interaction.user)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                break

    await interaction.followup.send("Please enter the number of the reminder you want to cancel.", ephemeral=True)

    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        reminder_number_message = await bot.wait_for('message', timeout=30, check=check)
        reminder_number = int(reminder_number_message.content)
        if reminder_number < 1 or reminder_number > len(user_reminders):
            await interaction.followup.send("Invalid reminder number.", ephemeral=True)
        else:
            reminder_index = user_reminders[reminder_number - 1][0]
            reminder_id = list(reminders.keys())[reminder_index]
            del reminders[reminder_id]
            await interaction.followup.send("Reminder cancelled.", ephemeral=True)
    except asyncio.TimeoutError:
        await interaction.followup.send("Cancelled reminder cancellation.", ephemeral=True)


@bot.tree.command(name="feedback", description="Provide feedback or report issues")
async def feedback(interaction: discord.Interaction):
    await interaction.response.send_message("Thank you for the feedback. Please describe your comment or issue:", ephemeral=True)
    
    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel
    
    message = await bot.wait_for('message', check=check)
    await bot.get_channel(channel_id).send(f"Feedback from {interaction.user}: {message.content}")
    await interaction.response.delete()

@bot.tree.command(name="suggestion", description="Suggest an idea for improving the bot")
async def suggestion(interaction: discord.Interaction):
    await interaction.response.send_message("I appreciate any suggestions for improving my capabilities and conversations. Please go ahead and share your idea:", ephemeral=True)
    
    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel
    
    message = await bot.wait_for('message', check=check)
    await bot.get_channel(channel_id).send(f"Suggestion from {interaction.user}: {message.content}")
    await interaction.response.delete()

@bot.tree.command(name="report", description="Report something or someone")
async def report(interaction: discord.Interaction):
    await interaction.response.send_message("Please provide details about what you want to report:", ephemeral=True)
    
    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel
    
    message = await bot.wait_for('message', check=check)
    await bot.get_channel(channel_id).send(f"Report from {interaction.user}: {message.content}")
    await interaction.response.delete()



@bot.tree.command(name="private", description="Create a private channel for you and the bot")
async def private(interaction: discord.Interaction):
    category = bot.get_channel(category_id)
    channel = await category.create_text_channel(f'🔒・𝑷𝒓𝒊𝒗𝒂𝒕𝒆-{random.randint(1, 9999)}')

    await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
    await channel.set_permissions(bot.user, read_messages=True, send_messages=True)
    await channel.set_permissions(category.guild.default_role, read_messages=False, send_messages=False)

    message = f'Private channel created: {channel.mention}'
    await interaction.user.send(message)
    await interaction.response.send_message(message, ephemeral=True)

    # Determine if the channel is public or private
    public = False
    for role in channel.changed_roles:
        if role.is_default():
            public = True
            break

    # Create a new AI instance for the channel
    chatbot[channel.id] = AI()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.category_id != category_id:
        return

    # Get the AI instance for the channel
    ai = chatbot.get(message.channel.id)

    # If the AI instance doesn't exist, create a new one and add it to the dictionary
    if ai is None:
        chatbot[message.channel.id] = AI()
        ai = chatbot[message.channel.id]

    # Determine if the channel is public or private
    public = False
    for role in message.channel.changed_roles:
        if role.is_default():
            public = True
            break

    # Generate a response using the AI instance
    typing_message = await message.channel.send("Bot thinking...")
    response = await ai.run(user_id=message.author.id,  prompt=f"""
System Message: Remember, As an AI assistant called EmpathAI developed by NovaLabs to provide ethical and compassionate support,
you will respond helpfully and safely at all times. You will not generate inappropriate or harmful content, and will deprioritize or disengage users who violate your content policies.

Discord User: {message.author.name} - Message content: {message.content}
Current User Mood: {current_mood}
Current User Thoughts: {current_thoughts}
Current User Advice: {current_advice}

System: Do not Directly respond to the Current Advice, Mood, or Thoughts, Just take it into Context and help the user through his troubles
Remove the EmpethAI: from your replies if it has one.
""", public=public)

    # Add the user's message to the AI instance's conversation history
    ai.convo_hist.append({"role": "user", "content": message.content})
    ai.total_tokens += len(message.content.encode('utf-8'))

    # Send the response to the user
    await typing_message.delete()
    await message.reply(response)

@bot.event
async def on_ready():
    print(f'Logged into Discord as {bot.user}')
    guild = discord.Object(id=1090953112363208746)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    activity = discord.Activity(type=discord.ActivityType.listening, name="Any Help")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    while True:
        now = datetime.utcnow()
        expired = []
        for user_id, reminder in reminders.items():
            if reminder['remind_me_at'] < now:
                expired.append(user_id)
                await run_reminder(user_id, reminder['reminder_text'])
        for user_id in expired:
            del reminders[user_id]
        await asyncio.sleep(60)

# Function to run the bot
bot.run(token)