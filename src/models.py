from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from typing import List


db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    favorites: Mapped[List["Favorite"]] = db.relationship(back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }


class People(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    height: Mapped[str] = mapped_column(String(10))
    mass: Mapped[str] = mapped_column(String(10))
    gender: Mapped[str] = mapped_column(String(20))
    birth_year: Mapped[str] = mapped_column(String(20))

    favorites: Mapped[List["Favorite"]] = db.relationship(back_populates="people")


    def serialize(self):
        return {
            "id": self.id
        }


class Planet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    climate: Mapped[str] = mapped_column(String(50))
    population: Mapped[str] = mapped_column(String(20))
    terrain: Mapped[str] = mapped_column(String(50))

    favorites: Mapped[List["Favorite"]] = db.relationship(back_populates="planet")


    def serialize(self):
        return{
            "id": self.id
        }


class Favorite(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(db.ForeignKey('user.id'), nullable=False)    
    people_id: Mapped[int | None] = mapped_column(db.ForeignKey('people.id'), nullable=True)
    planet_id: Mapped[int | None] = mapped_column(db.ForeignKey('planet.id'), nullable=True)

    user: Mapped["User"] = db.relationship(back_populates="favorites")
    people: Mapped["People | None"] = db.relationship(back_populates="favorites")
    planet: Mapped["Planet | None"] = db.relationship(back_populates="favorites")

    def serialize(self):
        pass