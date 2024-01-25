from fastapi import Depends
from sqlalchemy.schema import Column 
from core.database import Base, get_db


async def hmm(db=Depends(get_db)):
    pass
