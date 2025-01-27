from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, Integer, String, Float
from typing import List

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    password: Mapped[str] = mapped_column(String(80), nullable=False)
    favourites_users: Mapped[List["Favourites"]] = relationship(back_populates="users_favourites")

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "favourites": [favourite.serialize() for favourite in self.favourites_users]
            # do not serialize the password, its a security breach
        }
    
    def favourites_serialize(self):
        return {
            "id": self.id,
            "email": self.email
        }

class Favourites(db.Model):
    __tablename__= "favourites"
    id: Mapped[int] = mapped_column(primary_key=True)
    # relación con usuarios
    users_favourites_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    users_favourites: Mapped["User"] = relationship(back_populates="favourites_users")
    # relación con people
    people_favourites_id: Mapped[int] = mapped_column(ForeignKey("people.id"), nullable=True)
    people_favourites: Mapped["People"] = relationship()
    # relación con planets
    planet_favourites_id: Mapped[int] = mapped_column(ForeignKey("planets.id"), nullable=True)
    planet_favourites: Mapped["Planets"] = relationship()

    def serialize(self):
        return {
            "id": self.id,
            "user": self.users_favourites.favourites_serialize(),
            "people": self.people_favourites.serialize() if self.people_favourites else None,
            "planets": self.planet_favourites.serialize() if self.planet_favourites else None
        }
    

class People(db.Model):
    __tablename__= "people"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    birth_year: Mapped[int] = mapped_column(Integer, nullable=True)
    eye_color: Mapped[str] = mapped_column(String(50), nullable=True)
    gender: Mapped[str] = mapped_column(String(50), nullable=True)
    hair_color: Mapped[str] = mapped_column(String(50), nullable=True)
    height: Mapped[str] = mapped_column(String(50), nullable=True)
    weight: Mapped[str] = mapped_column(String(50), nullable=True)
    skin_color: Mapped[str] = mapped_column(String(50), nullable=True)
    species: Mapped[str] = mapped_column(String(50), nullable=True)
    starships: Mapped[str] = mapped_column(String(250), nullable=True)
    vehicles: Mapped[str] = mapped_column(String(250), nullable=True)
    master: Mapped[str] = mapped_column(String(250), nullable=True)
    disciple: Mapped[str] = mapped_column(String(250), nullable=True)
    image: Mapped[str] = mapped_column(String, nullable=True)
    films: Mapped[str] = mapped_column(String, nullable=True)
    # relación con planets
    homeworld_id: Mapped[int] = mapped_column(ForeignKey("planets.id"), nullable=True)
    homeworld: Mapped["Planets"] = relationship(back_populates="residents")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "eye_color": self.eye_color,
            "gender": self.gender,
            "hair_color": self.hair_color,
            "height": self.height,
            "weight": self.weight,
            "skin_color": self.skin_color,
            "species": self.species,
            "starships": self.starships,
            "vehicles": self.vehicles,
            "master": self.master,
            "disciple": self.disciple,
            "image": self.image,
            "films": self.films,
            "homeworld": self.homeworld.residents_serialize() if self.homeworld else None
        }
    
    def homeworld_serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }

class Planets(db.Model):
    __tablename__= "planets"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    diameter: Mapped[str] = mapped_column(String(50), nullable=True)
    rotation_period: Mapped[str] = mapped_column(String(50), nullable=True)
    orbital_period: Mapped[str] = mapped_column(String(50), nullable=True)
    gravity: Mapped[float] = mapped_column(Float, nullable=True)
    population: Mapped[int] = mapped_column(nullable=True)
    climate: Mapped[str] = mapped_column(String(50), nullable=True)
    terrain: Mapped[str] = mapped_column(String(50), nullable=True)
    surface_water: Mapped[str] = mapped_column(String(50), nullable=True)
    image: Mapped[str] = mapped_column(String, nullable=True)
    species: Mapped[str] = mapped_column(String(100), nullable=True)
    films: Mapped[str] = mapped_column(String(500), nullable=True)
    # relación con people
    residents: Mapped[List["People"]] = relationship(back_populates="homeworld")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "diameter": self.diameter,
            "rotation_period": self.rotation_period,
            "orbital_period": self.orbital_period,
            "gravity": self.gravity,
            "population": self.population,
            "climate": self.climate,
            "terrain": self.terrain,
            "surface_water": self.surface_water,
            "image": self.image,
            "species": self.species,
            "films": self.films,
            "residents": [person.homeworld_serialize() for person in self.residents] if self.residents else None
        }
    
    def residents_serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }

# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(80), unique=False, nullable=False)
#     is_active = db.Column(db.Boolean(), unique=False, nullable=False)

#     def __repr__(self):
#         return '<User %r>' % self.username

#     def serialize(self):
#         return {
#             "id": self.id,
#             "email": self.email,
#             # do not serialize the password, its a security breach
#         }