from dataclasses import dataclass


@dataclass
class SubjectIdentifier:
    subject_class: str
    subject_id: str
