# ... existing code ...

async def run(self, user_id, prompt, public=False):
    # ... existing code ...

    # Function to generate a response using the conversation history or summary as the context
    response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=context,
                max_tokens=350,
                n=1,
                stop=None,
                temperature=0.5,  # Lower the temperature to make the AI's responses more focused and deterministic
            )

    # ... existing code ...