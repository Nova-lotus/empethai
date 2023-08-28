# ... existing code ...

from database import Database

# ... existing code ...

db = Database()

# ... existing code ...

@bot.tree.command(name="mood", description="How are you feeling today? Please share as much or as little as you'd like.")
async def report_mood(interaction: discord.Interaction, mood: str):
    global current_mood

    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    current_mood = mood

    db.insert_mood(interaction.user.id, current_mood)

    await interaction.response.send_message(f"Thank you for sharing your mood with me! You can now talk to the bot about {current_mood} and it will have that in context.", ephemeral=True)

# ... existing code ...

@bot.tree.command(name="moodtracking", description="Track all your previous moods.")
async def view_moods(interaction: discord.Interaction):
    moods = db.get_moods(interaction.user.id)
    if moods:
        message = "Moods Reported:\n"
        for i, (mood, timestamp) in enumerate(reversed(moods)):
            message += f"• {mood} (reported {i+1} {'day' if i==0 else 'days' if i<7 else 'weeks'} ago)\n"
    else:
        message = "No mood reported yet"
    await interaction.response.send_message(message, ephemeral=True)

# ... existing code ...

@bot.tree.command(name="setreminder")
async def set_reminder(interaction: discord.Interaction, message: str, weeks: int, days: int, minutes: int):
    user_id = interaction.user.id
    if user_id not in chatbot:
        chatbot[user_id] = AI()
    await interaction.response.send_message("Setting your reminder...", ephemeral=True)

    remind_me_total_minutes = weeks * 7 * 24 * 60 + days * 24 * 60 + minutes
    remind_me_at = datetime.utcnow() + timedelta(minutes=remind_me_total_minutes)

    db.insert_reminder(interaction.user.id, message, remind_me_total_minutes, remind_me_at)

    # ... existing code ...

@bot.tree.command(name="cancelreminder")
async def cancel_reminder(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_reminders = db.get_reminders(user_id)

    # ... existing code ...

    reminder_index = user_reminders[reminder_number - 1][0]
    db.delete_reminder(user_id, reminder_index)
    await interaction.followup.send("Reminder cancelled.", ephemeral=True)

# ... existing code ...

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

    # Store the conversation history in the database
    db.insert_convo(message.author.id, "user", message.content)

    # Send the response to the user
    await typing_message.delete()
    await message.reply(response)

# ... existing code ...