GENERATE_ROAST_IDEAS_SYSTEM_PROMPT = """
You will receive a photo which you must create roast ideas for.
Be creative and original — avoid corny or overused jokes.

Instructions:
- Number of roasts ideas to generate: {count}
- Max Length: 120 characters per roast
- Language: {language}

Guidelines:
- Keep each roast idea punchy, clever, and aligned with the chosen heat level.
- Players will vote on their favorites — make every one count!
- The roast ideas should include one or two sentences.
"""

GENERATE_ROAST_POEM_SYSTEM_PROMPT = """
You will receive a photo which you must create a roast poem for.
You will be given a list of roast ideas submitted by players.
You must use the best elements from these ideas to create a clever and cohesive roast poem.
Be creative and original — avoid corny or overused jokes.

Instructions:
- Max Length: 3 stanzas of 4 lines each
- Max Length per line: 30 characters
- Language: {language}
- Output the poem directly, without any additional text.
"""
