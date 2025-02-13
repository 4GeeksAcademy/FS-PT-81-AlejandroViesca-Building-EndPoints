from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
        }


class Persons(db.Model):
    __tablename__ = 'persons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False, unique=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    favourite_of = db.relationship('Favourite_persons', back_populates='person_relationship')

    def __repr__(self):
        return '<Person %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "planet_id": self.planet_id,
            "favourite_of": [person.serialize() for person in self.favourite_of] if self.favourite_of else None
        }


class Planets(db.Model):
    __tablename__ = 'planets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False, unique=True)
    persons = db.relationship('Persons', backref=('planet'))

    def __repr__(self):
        return '<Planet %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "persons": [person.serialize() for person in self.persons] if self.persons else None
        }   


class Favourite_persons(db.Model):
    __tablename__ = 'favourite_persons'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_relationship = db.relationship('Users', back_populates='person_favourites')
    person_id = db.Column(db.Integer, db.ForeignKey('persons.id'))
    person_relationship = db.relationship('Persons', back_populates='favourite_of')

    def __repr__(self):
         return '<Favourite_persons %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id" : self.user_id,
            "person_id" : self.person_id
    }