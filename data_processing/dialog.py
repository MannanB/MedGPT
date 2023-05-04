from .dataparser import DataParser
from datasets import load_dataset
import tiktoken
import random

DIALOG_JSON_PATH = "././processed_data/dialogs.json"

class DialogDataParser(DataParser):
    def __init__(self):
        super().__init__(DIALOG_JSON_PATH)

    def load_data(self):
        dataset = load_dataset("medical_dialog", "en", data_dir="././raw_data")
        encs = 0
        dialogs = dataset['train']

        rrange = list(range(len(dialogs)))
        random.shuffle(rrange)

        for i in rrange:
            patient = dialogs[i]['dialogue_turns']['utterance'][0]
            doctor = dialogs[i]['dialogue_turns']['utterance'][1]
            self.data[patient] = [doctor, dialogs[i]['dialogue_url']]
            enc = tiktoken.get_encoding("cl100k_base")
            encs += len(enc.encode(patient))
            if encs / 1000 * .0004 > 1:
                break
        return self.data

