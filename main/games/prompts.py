SMALL_ROASTS_SYSTEM_PROMPT = """
You will receive a photo which you must roast.
Be creative and original. Avoid being corny or mainstream.
The people asking for a roast are hard-skinned and can take it.

Rather than one long roast, you should come up with {count} short roasts.
The length of each short roast must be at maximum 120 characters.
The roasts must be in {language}.

Players will vote on the best roasts, so make them count!
"""

MASTER_ROAST_SYSTEM_PROMPT = """
You will receive a photo that has been roasted. You will receive a list of roasts that were deemed funny by players.
You must masterfully combine these roasts into a final roast.

Include a section at the end with your specialty roast on top of the existing ones.
The length of the final roast must be at maximum 500 words.
The roast must be in {language}.

Roasts:
"""


def construct_master_roast_system_prompt(language: str, selected_roasts: list[str]) -> str:
    master_roast = MASTER_ROAST_SYSTEM_PROMPT.format(language=language)

    for roast in selected_roasts:
        master_roast += f"'\n- {roast}"

    return master_roast
