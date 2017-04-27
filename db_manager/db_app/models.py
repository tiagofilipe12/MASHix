## the actual file that does the structure to be imported in the database

from . import db
from sqlalchemy.dialects.postgresql import JSON

class Plasmid(db.Model):
    __tablename__ = "plasmids"
    plasmid_id = db.Column(db.String, primary_key=True)
    json_entry = db.Column(JSON, index=True, unique=True)

    def __repr__(self):
        return '<Plasmid %r>' % (self.json_entry)

## in order to add an entry to the database one should use something like the example below

# models.Plasmid(plasmid_id='1345', json=json.dumps({"names":"buh", "distances":{"gi_1":"21388213", "gi_2":"398393"}}))
# db.session.add(row)
# db.session.commit()

class Card(db.Model):
    __tablename__ = "card"
    plasmid_id = db.Column(db.String, primary_key=True)
    json_entry = db.Column(JSON, index=True, unique=True)

    def __repr__(self):
        return '<Card %r>' % (self.json_entry)