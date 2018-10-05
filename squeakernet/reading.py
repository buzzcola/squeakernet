import json

class Reading():
    def __init__(self, date, reading):
        self.date = date
        self.reading = reading
    
    def to_json(this):
        result = {
            'date': str(this.date),
            'reading': this.reading
        }
        return json.dumps(result)
