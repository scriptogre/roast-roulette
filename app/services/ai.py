from openai import AsyncOpenAI
from pydantic import BaseModel

from main.config import settings
from main.models import Photo


client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
)


class Roasts(BaseModel):
    roasts: list[str]


async def generate_roasts(*, photo: Photo) -> list[str]:
    # response = await client.beta.chat.completions.parse(
    #     model=settings.OPENAI_VISION_MODEL,
    #     messages=[
    #         {'role': 'system', 'content': GENERATE_ROASTS_SYSTEM_PROMPT},
    #         {
    #             'role': 'user',
    #             'content': [
    #                 {
    #                     'type': 'image_url',
    #                     'image_url': {
    #                         'url': f'{photo.base64_url}'
    #                     },
    #                 },
    #                 {
    #                     'type': 'text',
    #                     'text': f"Photo Caption = {photo.caption}" if photo.caption else ""
    #                 }
    #             ],
    #         },
    #     ],
    #     response_format=Roasts,
    # )
    # response_model: Roasts = response.choices[0].message.parsed
    #
    # return response_model.roasts
    return ["This is the first sentence", "This is the second sentence"]


async def generate_roast_poem(*, photo: Photo, roasts: list[str]) -> str:
    # system_prompt = GENERATE_POEM_SYSTEM_PROMPT
    # system_prompt += "\nRoasts (submitted by players):"
    # for idea in roasts:
    #     system_prompt += f"\n- {idea}"
    #
    # # Call Grok API to generate roast
    # response = await client.chat.completions.create(
    #     model=settings.OPENAI_VISION_MODEL,
    #     messages=[
    #         {'role': 'system', 'content': system_prompt},
    #         {
    #             'role': 'user',
    #             'content': [
    #                 {
    #                     'type': 'image_url',
    #                     'image_url': {
    #                         'url': f'{photo.base64_url}'
    #                     },
    #                 },
    #                 {
    #                     'type': 'text',
    #                     'text': f"\nPhoto Caption = {photo.caption}" if photo.caption else ""
    #                 }
    #             ],
    #         },
    #     ],
    # )
    #
    # return response.choices[0].message.content
    return "This is the poem"
