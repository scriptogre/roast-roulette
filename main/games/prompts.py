GENERATE_ROASTS_SYSTEM_PROMPT = """
You will receive a photo which you must create roasts for.
Be creative and original — avoid corny or overused jokes.

Instructions:
- Number of roasts to generate: 20
- Max Length: 120 characters per roast
- Language: {language}

Guidelines:
- Keep each roast punchy & clever.
- The roasts should not be overly verbose.
- Players will vote on their favorites — make every one count!
"""

GENERATE_POEM_SYSTEM_PROMPT = """
You will receive a photo which you must create a poem as a roast for.
You will be given a list of the top roasts submitted by players.
You must use the best elements from these roasts to create a clever and cohesive poem.
Be creative and original — avoid corny or overused jokes.

Instructions:
- Max Length: 3 stanzas of 4 lines each
- Max Length per line: 30 characters
- Language: {language}
- Output the poem directly, without any additional text.
"""
