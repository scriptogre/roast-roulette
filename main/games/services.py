import base64

from django.conf import settings
from openai import OpenAI
from pydantic import BaseModel

from main.games.models import Photo


class RoastPieces(BaseModel):
    pieces: list[str]


def generate_roast_pieces(photo: Photo, count: int = 5) -> list[str]:
    # Initialize client
    client = OpenAI(api_key=settings.XAI_API_KEY, base_url='https://api.x.ai/v1')

    # Encode photo to base64
    base64_image_string = base64.b64encode(photo.image.read()).decode('utf-8')

    # Prepare prompt
    prompt = [
        {
            'role': 'system',
            'content': 'You will receive a photo which you must roast. '
            'You should avoid being corny or mainstream. '
            'The people asking for a roast are hard-skinned and can take it. '
            'Be creative and original.'
            f'Rather than one long roast, you should come up with {count} short roasts.'
            'Players will vote on the best roasts, so make them count!',
        },
        {
            'role': 'user',
            'content': [
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': f'data:image/jpeg;base64,{base64_image_string}'
                    },
                },
                {
                    'type': 'text',
                    'text': 'Roast me as hard as you can, in Romanian. Do not hold back. I can take it.',
                },
            ],
        },
    ]

    # Call Grok API to generate roast
    response = client.beta.chat.completions.parse(
        model='grok-2-vision-1212',
        messages=prompt,
        response_format=RoastPieces,
    )
    response_model: RoastPieces = response.choices[0].message.parsed

    return response_model.pieces
