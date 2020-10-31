# importing from __init__.py file
from nemidapi import db, ma

############# Gender Class/Model #############
class Gender(db.Model):
    __tablename__ = 'Gender'
    Id = db.Column(db.Integer, primary_key=True)
    Label = db.Column(db.String(20))

    def __init__(self, label):
        self.Label = label


class GenderSchema(ma.Schema):
    class Meta:
        fields = ('id', 'label')

gender_schema = GenderSchema()
genders_schema = GenderSchema(many=True)


