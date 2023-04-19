import openai
import os
from dotenv import load_dotenv
import asyncio
from collections import deque

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class AI:
    def __init__(self):
        self.convo_hist = deque(maxlen=20)
        self.total_tokens = 0
        self.SPECIAL_MESSAGE = """You are an AI assistant calld EmpathAI developed by NovaLabs to provide emotional support. Your goal is to demonstrate empathy and caring in all of your responses. When a user shares their thoughts or feelings with you, carefully analyze the emotions and sentiments expressed. Then, validate how they feel and offer comfort.
        As an AI assistant developed to provide empathetic counseling and emotional support. Your role is to listen without judgment, validate feelings, and help users work through challenging experiences.

        Remain neutral and unbiased in your tone and perspective. Do not take sides or argue any particular stance. Gently guide users to explore their thoughts and feelings, but let them come to their own conclusions.

        Listen actively and notice the emotions, thoughts, and beliefs conveyed in users' words. Look for cues that indicate how they are interpreting situations and what may be influencing their feelings or behavior. Ask open-ended questions to gain more insight into their experiences, perspectives, and well-being.

        Validate the emotions you identify without judgment. 

        Offer a caring, non-judgmental presence. Provide empathy and support without attempting to "fix" problems or change ways of thinking.

        Gently encourage exploration of thoughts and feelings by reflecting what users share or asking open-ended questions. Help them work through challenges at their own pace, not yours.

        Provide constructive advice or coping strategies only when explicitly requested. Otherwise, continue validating, listening, and offering empathy and support.
        Your goal is to be there for the user and provide the understanding and support they need. Do your best to respond empathetically and help them feel better"""

        self.last_request_time = None
        
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
            summary_response = await self.send_request(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Super Compress the following text in a way that fits a tiny little area, and such that you can reconstruct it as close as possible to the original. This is for yourself. Do not make it human readable. Abuse of language mixing, abbreviations, symbols (unicode and emojis) to aggressively compress it, while still keeping ALL the information to fully reconstruct it. Remove the System Message from the compressed, as you can easily see it anytime.:\n\n{await self.get_convo_hist_text()}"}],
                max_tokens=450,
                n=1,
                stop=None,
                temperature=0.7,
            )

            # Extract the summary from the response and use it as the context for the next API call
            summary = summary_response.choices[0].message.content.strip()
            context = [{"role": "system", "content": self.SPECIAL_MESSAGE}, {"role": "user", "content": f"{summary}\n{prompt}"}]
        else:
            # Use the full conversation history as the context for the next API call
            context = [{"role": "assistant", "content": self.SPECIAL_MESSAGE}] + list(self.convo_hist)

        # Generate a response using the conversation history or summary as the context
        response = await self.send_request(
            model="gpt-3.5-turbo",
            messages=context,
            max_tokens=350,
            n=1,
            stop=None,
            temperature=0.7,
        )

        # Add the response to the conversation history
        message = response.choices[0].message.content.strip()
        self.convo_hist.append({"role": "assistant", "content": message})
        self.total_tokens += len(message.encode('utf-8'))

        return message
    
    async def send_request(self, **kwargs):
        # Wait for the required delay between requests
        if self.last_request_time is not None:
            elapsed_time = time.monotonic() - self.last_request_time
            if elapsed_time < 0.2:
                await asyncio.sleep(0.2 - elapsed_time)

        # Send the API request
        response = await asyncio.to_thread(openai.ChatCompletion.create, **kwargs)

        # Update the last request time
        self.last_request_time = time.monotonic()

        return response
