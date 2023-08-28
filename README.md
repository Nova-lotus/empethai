# EmpathAI

EmpathAI is a Discord bot developed by NovaLabs. It is designed to provide ethical and compassionate support to users. It can set reminders, track moods, listen to thoughts, provide advice, and create private channels for users.

## Table of Contents
1. [How to Run](#how-to-run)
2. [Features](#features)
3. [Code Structure](#code-structure)
4. [Future Improvements](#future-improvements)

## How to Run
1. Clone the repository.
2. Install the necessary libraries by running `pip install -r requirements.txt`.
3. Set up a `.env` file in the root directory with your Discord token and OpenAI API key.
4. Run the bot by executing `python Empath.py`.

## Features
- **Mood Tracking**: Users can report their mood and the bot will track it. This allows the bot to understand the user's emotional state and provide appropriate responses.
- **Reminders**: Users can set reminders and the bot will notify them at the specified time. This can be useful for remembering important tasks or events.
- **Thoughts Sharing**: Users can share their thoughts and the bot will listen without judgment. This provides a safe space for users to express their feelings and thoughts.
- **Advice**: Users can request advice and the bot will provide support. The bot is designed to provide compassionate and ethical advice to help users navigate their concerns or goals.
- **Private Channels**: Users can create private channels for them and the bot. This allows for private conversations between the user and the bot.

## Code Structure

The codebase is divided into two main files: `Empath.py` and `chat.py`.

- `Empath.py` handles the Discord bot functionality. It includes commands for mood tracking, setting reminders, sharing thoughts, requesting advice, and creating private channels. It also handles events such as messages and bot readiness.

- `chat.py` handles the AI interactions. It uses OpenAI's GPT-3 model to generate responses to user messages. The AI keeps track of the conversation history and uses it to generate contextually appropriate responses.

## Future Improvements
- Implement a database to persistently store user data such as moods, reminders, and conversation history.
- Add more commands for user interaction.
- Improve the AI's response generation to provide more accurate and helpful responses.