from pydantic import BaseModel

class ToggleHidden(BaseModel):
    hidden: bool
