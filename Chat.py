class AI:
    def __init__(self):
        self.convo_hist = deque(maxlen=20)
        self.total_tokens = 0
        self.SPECIAL_MESSAGE = """You are an AI assistant called EmpathAI.
        Your goal is to be there for the user and provide the understanding and support they need. Do your best to respond empathetically and help them feel better"""

        # Add the special message to the conversation history
        self.convo_hist.append({"role": "system", "content": self.SPECIAL_MESSAGE})
        self.total_tokens += len(self.SPECIAL_MESSAGE.encode('utf-8'))

    # ... existing code ...

    async def run(self, user_id, prompt, public=False):
        # ... existing code ...

        # Add the user's message to the conversation history
        self.convo_hist.append({"role": "user", "content": prompt})
        self.total_tokens += len(prompt.encode('utf-8'))

        # ... existing code ...

        # Function to generate a response using the conversation history or summary as the context
        response = await openai.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                    messages=self.convo_hist,
                    max_tokens=350,
                    n=1,
                    stop=None,
                    temperature=0.5,  # Lower the temperature to make the AI's responses more focused and deterministic
                )

        # Add the response to the conversation history
        message = response.choices[0].message.content.strip()
        self.convo_hist.append({"role": "assistant", "content": message})
        self.total_tokens += len(message.encode('utf-8'))

    # ... existing code ...