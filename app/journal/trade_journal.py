from dataclasses import dataclass
from datetime import datetime


@dataclass
class JournalEntry:
    timestamp: datetime
    event: str
    message: str


class TradeJournal:

    def __init__(self):
        self.entries = []

    def log(self, event: str, message: str):

        self.entries.append(
            JournalEntry(
                timestamp=datetime.now(),
                event=event,
                message=message,
            )
        )

    def count(self):

        return len(self.entries)

    def latest(self):

        if not self.entries:
            return None

        return self.entries[-1]