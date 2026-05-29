from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import datetime

from database import engine, Base, get_db
from models import User, Reservation
from auth import hash_password, verify_password

# Tworzenie tabel w bazie przy starcie aplikacji (jeśli nie istnieją)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cloud Desk API", version="1.0")


# Schematy Pydantic (Walidacja danych)
class UserCreate(BaseModel):
    username: str
    password: str


class ReservationCreate(BaseModel):
    desk_number: str
    user_id: int


class ReservationResponse(BaseModel):
    id: int
    desk_number: str
    reservation_date: datetime.datetime
    user_id: int

    class Config:
        from_attributes = True


#  Rejestracja użytkownika oraz szyfrowanie haseł
@app.post("/users/register", status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Użytkownik już istnieje")

    # Szyfrowanie hasła
    secured_password = hash_password(user_data.password)

    new_user = User(username=user_data.username, hashed_password=secured_password)
    db.add(new_user)
    db.commit()
    return {"message": "Użytkownik zarejestrowany pomyślnie"}


# --- CRUD ---

# 1. CREATE (Tworzenie rezerwacji)
@app.post("/reservations", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
    # Sprawdzenie czy użytkownik istnieje
    user = db.query(User).filter(User.id == reservation.user_id).first()
    if not user:
        raise HTTPException(status_code=44, detail="Nie znaleziono użytkownika")

    new_res = Reservation(desk_number=reservation.desk_number, user_id=reservation.user_id)
    db.add(new_res)
    db.commit()
    db.refresh(new_res)
    return new_res


# 2. READ (Odczyt wszystkich rezerwacji)
@app.get("/reservations", response_model=List[ReservationResponse])
def read_all_reservations(db: Session = Depends(get_db)):
    return db.query(Reservation).all()


# 3. UPDATE (Aktualizacja numeru biurka)
@app.put("/reservations/{res_id}", response_model=ReservationResponse)
def update_reservation(res_id: int, updated_desk: str, db: Session = Depends(get_db)):
    db_res = db.query(Reservation).filter(Reservation.id == res_id).first()
    if not db_res:
        raise HTTPException(status_code=404, detail="Nie znaleziono rezerwacji")

    db_res.desk_number = updated_desk
    db.commit()
    db.refresh(db_res)
    return db_res


# 4. DELETE (Usunięcie/Anulowanie rezerwacji)
@app.delete("/reservations/{res_id}", status_code=status.HTTP_200_OK)
def delete_reservation(res_id: int, db: Session = Depends(get_db)):
    db_res = db.query(Reservation).filter(Reservation.id == res_id).first()
    if not db_res:
        raise HTTPException(status_code=404, detail="Nie znaleziono rezerwacji")

    db.delete(db_res)
    db.commit()
    return {"message": f"Anulowano rezerwację o ID {res_id}"}