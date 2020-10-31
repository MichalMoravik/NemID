# importing from __init__.py file
from nemidapi import db, ma

############# User Class/Model #############
class User(db.Model):
    __tablename__ = 'User'
    Id = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(255))
    NemId = db.Column(db.String(20))
    CPR = db.Column(db.String(20))
    CreatedAt = db.Column(db.String(255))
    ModifiedAt = db.Column(db.String(255))
        
    # one-to-many relationship
    GenderId = db.Column(db.Integer, db.ForeignKey('Gender.Id'))
    Gender = db.relationship('Gender', backref=db.backref('User', lazy=True))
    
    def __init__(self, email, nem_id, cpr, created_at, modified_at, gender_id, gender):
        self.Email = email,
        self.NemId = nem_id,
        self.CPR = cpr,
        self.CreatedAt = created_at,
        self.ModifiedAt = modified_at,
        self.GenderId = gender_id,
        self.Gender = gender


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'email', 'nem_id', 'cpr', 'created_at', 'modified_at', 'gender_id')

user_schema = UserSchema()
users_schema = UserSchema(many=True)


