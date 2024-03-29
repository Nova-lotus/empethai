import openai
import os
from dotenv import load_dotenv
import asyncio
from collections import deque

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Class to handle AI interactions
class AI:
    def __init__(self):
        self.convo_hist = deque(maxlen=20)
        self.total_tokens = 0
        self.SPECIAL_MESSAGE = """You are an AI assistant called EmpathAI.
        Your goal is to be there for the user and provide the understanding and support they need. Do your best to respond empathetically and help them feel better"""

        # Add the special message to the conversation history
        self.convo_hist.append({"role": "system", "content": self.SPECIAL_MESSAGE})
        self.total_tokens += len(self.SPECIAL_MESSAGE.encode('utf-8'))

    async def get_convo_hist_text(self, public=False):
        if public:
            return "\n\n".join([f"{msg['role']}: {msg['content']}" for msg in self.convo_hist])
        else:
            return "\n\n".join([msg['content'] for msg in self.convo_hist if msg['role'] != 'system'])

    async def run(self, user_id, prompt, public=False):
        # Check if the conversation history has exceeded the token limit
        while self.total_tokens >= 3996:
            # If it has, remove the oldest messages until the total token count is below the limit
            oldest_message = self.convo_hist.popleft()
            self.total_tokens -= len(oldest_message["content"].encode('utf-8'))

            # If the oldest message is the special message, don't add it back to the deque
            if oldest_message["content"] == self.SPECIAL_MESSAGE:
                continue
                
        # Add the user's message to the conversation history
        self.convo_hist.append({"role": "user", "content": prompt})
        self.total_tokens += len(prompt.encode('utf-8'))

        # If the conversation history is large enough, summarize it
        if self.total_tokens >= 3900:
            # Remove the special message from the conversation history if it's present
            if self.convo_hist[0]["content"] == self.SPECIAL_MESSAGE:
                self.convo_hist.popleft()
                self.total_tokens -= len(self.SPECIAL_MESSAGE.encode('utf-8'))

            # Create a summary of the conversation history using OpenAI's GPT-3 API
            summary_response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Super Compress the following text in a way that fits a tiny little area, and such that you can reconstruct it as close as possible to the original. This is for yourself. Do not make it human readable. Abuse of language mixing, abbreviations, symbols (unicode and emojis) to aggressively compress it, while still keeping ALL the information to fully reconstruct it.:\n\n{self.get_convo_hist_text()}"}], 
                max_tokens=450,
                n=1,
                stop=None,
                temperature=0.7,
            )

            # Extract the summary from the response and use it as the context for the next API call
            summary = summary_response.choices[0].message.content.strip()
            context = [{"role": "system", "content": self.SPECIAL_MESSAGE}, {"role": "user", "content": f"Summery of current conversation: {summary}\nCurrent prompt: {prompt}"}]
        else:
            # Use the full conversation history as the context for the next API call
            context = [{"role": "assistant", "content": self.SPECIAL_MESSAGE}] + list(self.convo_hist)

        # Function to generate a response using the conversation history or summary as the context
        response = await openai.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                    messages=context,
                    max_tokens=350,
                    n=1,
                    stop=None,
                    temperature=1,
                )

        # Add the response to the conversation history
        message = response.choices[0].message.content.strip()
        self.convo_hist.append({"role": "assistant", "content": message})
        self.total_tokens += len(message.encode('utf-8'))

        return message
