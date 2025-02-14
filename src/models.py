from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False, unique=True)
    person_favourites = db.relationship('Favourite_persons', back_populates='user_relationship')
    planet_favourites = db.relationship('Favourite_planets', back_populates='user_relationship')

    def __repr__(self):
        return '<Users %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "person_favourites": [user.serialize() for user in self.person_favourites] if self.person_favourites else None
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
    favourite_of = db.relationship('Favourite_planets', back_populates='planet_relationship')

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


class Favourite_planets(db.Model):
    __tablename__ = 'favourite_planets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_relationship = db.relationship('Users', back_populates='planet_favourites')
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    planet_relationship = db.relationship('Planets', back_populates='favourite_of')

    def __repr__(self):
        return '<Favourite_planets %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id
        }