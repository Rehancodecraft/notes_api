from datetime import datetime
from extensions import db


#<-------------------MODELS----------------------->
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable = False, unique = True)

    notes = db.relationship("Note", backref="category", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name}

class Note(db.Model):
    __tablename__ = "notes"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False, unique=True)
    content = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)

    def to_dict(self):
      return  {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "category": self.category.name if self.category else None
        }
