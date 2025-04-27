import shortuuid


def generate_unique_game_code():
    """
    Generates a short, unique 4-character code using uppercase letters and numbers.
    """
    return shortuuid.ShortUUID(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ').random(length=4)
