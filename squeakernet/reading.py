import json

class Reading():
    def __init__(self, date, reading):
        self.date = date
        self.reading = reading
    
    def to_json(self):
        result = {
            'date': str(self.date),
            'reading': self.reading
        }
        return json.dumps(result)
