# Let's calculate the number of tokens used in the current conversation.
import tst_openai

# Assuming we can access the context history
conversation = [
    {"role": "system", "content": "You are ChatGPT."},
    {"role": "user", "content": "...."},  # Include full conversation history up to now.
]

# Calculate tokens for a request
response = openai.Completion.create(
    model="gpt-4",
    messages=conversation,
    max_tokens=0  # Do not generate a response, just count tokens
)

tokens_used = response["usage"]["total_tokens"]
tokens_used
