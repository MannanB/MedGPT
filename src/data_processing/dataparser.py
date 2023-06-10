import os
import json

class DataParser:
    def __init__(self, source):
        self.source = source
        self.data = {}
        self.credits = {}
        self.embedding_text = []
        self.documents = []

    def load_data(self):
        """Returns the data in the source file. If the source file does not exist, it will be created and populated.

        Arguments:
            None

        Returns:
            dict: The data in the source file
        """
        if os.path.exists(self.source):
            with open(self.source, 'r') as f:
                self.data = json.load(f)
        else:
            input(f"Source {self.source} has not been parsed. Press enter to parse")
            self.parse_data()
            with open(self.source, "w") as f:
                f.write(json.dumps(self.data, indent=4))

        self.prepare_embedding()
        self.create_credits()
    
    def prepare_embedding(self):
        """Prepares data for embedding."""
        return
    
    def create_credits(self):
        """Creates credits for the data."""
        return

    def parse_data(self):
        """Load data from source"""
        return []

    