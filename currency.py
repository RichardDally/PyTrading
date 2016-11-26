class Currency:                                                                                                                                                                                                    
    id = None
    isocode = None # ISO 4217                                                                                                                                                                                      

    def __init__(self, id, isocode):
        self.id = id
        self.isocode = isocode

    def __str__(self):
        return self.isocode

    @staticmethod
    def get_available():
        return [Currency(0, 'EUR')]