from pydantic import BaseModel


class NewDestination(BaseModel):

    path: str
    destination: str

class UpdateDestination(BaseModel):

    id: str
    path: str
    destination: str