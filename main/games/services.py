from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from openai import OpenAI
from pydantic import BaseModel

from main.games.enums import HeatLevel
from main.games.models import Photo
from main.games.prompts import (
    GENERATE_ROAST_IDEAS_SYSTEM_PROMPT,
    GENERATE_ROAST_POEM_SYSTEM_PROMPT,
)


class RoastIdeas(BaseModel):
    roast_ideas: list[str]


def generate_roast_ideas(
    photo: Photo, count: int = 5, language: str = "english"
) -> list[str]:
    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
    )

    system_prompt = GENERATE_ROAST_IDEAS_SYSTEM_PROMPT.format(
        count=count, language=language
    )

    response = client.beta.chat.completions.parse(
        model=settings.OPENAI_VISION_MODEL,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f'{photo.base64_url}'
                        },
                    },
                    {
                        'type': 'text',
                        'text': f"Photo Caption = {photo.caption}" if photo.caption else ""
                    }
                ],
            },
        ],
        response_format=RoastIdeas,
    )
    response_model: RoastIdeas = response.choices[0].message.parsed

    return response_model.roast_ideas


def generate_roast_poem(
    photo: Photo, roast_ideas: list[str], language: str = "english"
) -> str:
    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
    )

    system_prompt = GENERATE_ROAST_POEM_SYSTEM_PROMPT.format(language=language)
    system_prompt += "\nRoast ideas (submitted by players):"
    for idea in roast_ideas:
        system_prompt += f"\n- {idea}"

    # Call Grok API to generate roast
    response = client.chat.completions.create(
        model=settings.OPENAI_VISION_MODEL,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f'{photo.base64_url}'
                        },
                    },
                    {
                        'type': 'text',
                        'text': f"\nPhoto Caption = {photo.caption}" if photo.caption else ""
                    }
                ],
            },
        ],
    )

    return response.choices[0].message.content


def generate_roast_ideas_in_the_background(
    photo: Photo, count: int = 5, language: str = "english",
) -> ThreadPoolExecutor:
    return ThreadPoolExecutor(max_workers=1).submit(
        generate_roast_ideas, photo=photo, count=count, language=language
    )


def generate_roast_poem_in_the_background(
    photo: Photo, roast_ideas: list[str], language: str = "english",
) -> ThreadPoolExecutor:
    return ThreadPoolExecutor(max_workers=1).submit(
        generate_roast_poem, photo=photo, roast_ideas=roast_ideas, language=language
    )
