class UppercaseGameCodeConverter:
    """
    Custom converter for game codes that ensures they are always uppercase.
    """

    regex = '[A-Za-z]{4}'  # Matches 4 letters (assuming game codes are 4 characters)

    def to_python(self, value):
        return value.upper()  # Convert to uppercase before passing to view

    def to_url(self, value):
        return value.upper()  # Ensure the URL generated is uppercase
