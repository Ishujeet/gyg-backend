from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.models.base import get_db
from src.models.gym_slot import Slot, Gym
from src.models.vendors import GymOwner
from datetime import datetime
from src.vendor.login import get_current_user
from enum import Enum
from pydantic import BaseModel
from src.utils import generate_id

gym_router = APIRouter(
    prefix="/gym",
    tags=["gym"],
    dependencies=[Depends(get_current_user)],
    responses={403: {"description": "Forbidden"}},
)

class Status(str, Enum):
    Added: 'Added'
    Paused: 'Paused'
    Stopped: 'Stopped'
    

class GymDetails(BaseModel):
    name: str
    address: str
    capacity: int

@gym_router.post("/add_gym/")
def add_gym(gym: GymDetails, db: Session = Depends(get_db)):
    existing_gym = db.query(Gym).filter(Gym.name == gym.name).first()
    if existing_gym:
        raise HTTPException(status_code=400, detail="Gym with this name already exists")
    
    gym = Gym(**gym.model_dump(), gym_id=generate_id())
    gym.status = "Added"

    db.add(gym)
    db.commit()
    db.refresh(gym)
    
    return gym

@gym_router.put("/remove_gym/{gym_id}")
def remove_gym(gym_id: str, db: Session = Depends(get_db), current_user: GymOwner = Depends(get_current_user)):
    gym = db.query(Gym).get(gym_id)
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")
    if gym.owner_id != current_user.owner_id:
        raise HTTPException(status_code=403, detail="You don't have permission to update this slot")
    
    gym.status = "Stopped"
    db.commit()
    return {"message": "Gym removed successfully"}

@gym_router.put("/pause_gym/{gym_id}")
def remove_gym(gym_id: str, db: Session = Depends(get_db), current_user: GymOwner = Depends(get_current_user)):
    gym = db.query(Gym).get(gym_id)
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")
    if gym.owner_id != current_user.owner_id:
        raise HTTPException(status_code=403, detail="You don't have permission to update this slot")
    
    gym.status = "Stopped"
    db.commit()
    return {"message": "Gym removed successfully"}


@gym_router.put("/slots/{slot_id}")
def update_slot(slot_id: int, new_start_time: datetime, new_end_time: datetime, 
                db: Session = Depends(get_db), current_user: GymOwner = Depends(get_current_user)):
    slot = db.query(Slot).get(slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    associated_gym = slot.gym
    if not associated_gym and associated_gym.owner != current_user:
        raise HTTPException(status_code=403, detail="You don't have permission to update this slot")
    
    # Update the slot details here
    slot.start_time = new_start_time
    slot.end_time = new_end_time
    slot.slot_id = generate_id()
    db.commit()
    
    return {"message": "Slot updated successfully"}
