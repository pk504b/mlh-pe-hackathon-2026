from peewee import CharField, IntegerField
from app.database import BaseModel

class Song(BaseModel):
    title = CharField()
    artist = CharField()
    genre = CharField()
    duration = IntegerField() 

    