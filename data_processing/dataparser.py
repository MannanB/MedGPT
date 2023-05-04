import os
import json

class DataParser:
    def __init__(self, source):
        self.source = source
        self.data = {}

    def create_data(self):
        if os.path.exists(self.source):
            with open(self.source, 'r') as f:
                self.data = json.load(f)
        else:
            input(f"Source {self.source} has not been parsed. Press enter to parse")
            self.load_data()
            with open(self.source, "w") as f:
                f.write(json.dumps(self.data, indent=4))
        return self.data

    def load_data(self):
        pass

    