class Currency:
    identifier = None
    iso_code = None

    def __init__(self, identifier, iso_code):
        self.identifier = identifier
        self.iso_code = iso_code

    def __str__(self):
        return self.iso_code

