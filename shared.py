from dataclasses import dataclass

@dataclass
class EmailInputPayload:
    id: str
    subject: str
    body: str

@dataclass
class EmailOutputPayload:
    id: str
    subject: str
    body: str
    processed: bool 
