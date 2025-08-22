from flask import Flask,request,jsonify
from dotenv import load_dotenv

import os
from extensions import db

load_dotenv()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

from models import Category, Note 

with app.app_context():
    db.create_all()
#====================================================CATEGORY ENDPOINTS=======================================================

#<-----------------------CREATE CATEGORY------------------------>
@app.route("/categories", methods = ["POST"])
def create_category():
    data = request.json
    name = data.get("name")
    if not name:
        return jsonify({"error": "category is required field!"}),400

    existing = Category.query.filter_by(name=name).first()
    if existing:
        return jsonify({"error": "category already exists!"}),400

    new_category = Category(name=name)
    db.session.add(new_category)
    db.session.commit()

    return jsonify(
        {
            "success": "new category has been created!",
            "New Category": new_category.to_dict()
        }
            ),201
#<-----------------------GET ALL CATEGORIES------------------------>
@app.route("/categories",methods = ["GET"])
def get_all_categories():
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories]),200

#<-----------------------GET CATEGORY BY ID------------------------>
@app.route("/category/<int:id>", methods = ["GET"])
def get_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({"error": "category not found!"}),404
    return jsonify([category.to_dict()]),200

#<-----------------------UPDATE CATEGORY------------------------>
@app.route("/category/<int:id>",methods = ["PUT"])
def update_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({"error": "category not found!"}),404
    data = request.json
    name = data.get("name")
    if not name:
        return jsonify({"error": "name is required"})
    category.name = name
    db.session.commit()
    return jsonify({"success": "categery has been updated","category": category.to_dict()})


#<-----------------------DELETE CATEGORY------------------------>
@app.route("/category/<int:id>",methods = ["DELETE"])
def delete_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({"error": "category not found"}),404
    db.session.delete(category)
    db.session.commit()
    return jsonify({"success": "category deleted"}),200


#====================================================NOTES ENDPOINTS=======================================================

#<--------------CREATE NOTES------------------->
@app.route("/notes",methods = ["POST"])
def create_note():
    data = request.json
    title = data.get("title")
    content = data.get("content")
    category_id = data.get("category_id")

    if not title:
        return jsonify({"error": "title is required!"}),400
    existing = Note.query.filter_by(title=title).first()
    if existing :
        return jsonify({"error": "note already exist"})
    if category_id is not None:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "category not found"}), 404

    new_note = Note(title=title,content=content,category_id=category_id)
    db.session.add(new_note)
    db.session.commit()
    return jsonify({"success": "note has been created"},new_note.to_dict()),201

#<--------------GET ALL NOTES------------------->
@app.route("/notes",methods = ["GET"])
def get_all_notes():
    notes = Note.query.all()
    return jsonify([n.to_dict() for n in notes])


#<--------------GET NOTE BY ID------------------->
@app.route("/note/<int:id>",methods = ["GET"])
def get_note(id):
    note = Note.query.get(id)
    if not note:
        return jsonify({"error": "note not found!"}),404
    return jsonify([note.to_dict()]),200


#<--------------UPDATE NOTE------------------->
@app.route("/note/<int:id>",methods = ["PUT"])
def update_note(id):
    note = Note.query.get(id)
    if not note:
        return jsonify({"error": "note not found!"}),404
    data = request.json
    title = data.get("title")
    content = data.get("content")
    category_id = data.get("category_id")
    if not title:
        return jsonify({"error": "title is required!"}),400

    if title:
        existing = Note.query.filter_by(title=title).first()
        if existing and existing.id != id:
            return jsonify({"error": "note with this title already exists"}), 400
        note.title = title

    if content is not None:
        note.content = content

    if category_id is not None:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "category not found"}), 404
        note.category_id = category_id

    db.session.commit()
    return jsonify({"success": "note updated", "note": note.to_dict()}), 200

#<--------------DELETE NOTE------------------->
@app.route("/notes/<int:id>", methods=["DELETE"])
def delete_note(id):
    note = Note.query.get(id)
    if not note:
        return jsonify({"error": "note not found"}), 404

    db.session.delete(note)
    db.session.commit()
    return jsonify({"success": "note deleted"}), 200

#<--------------GET ALL NOTES OF A CATEGORY------------------->
@app.route("/category/<int:id>/notes",methods=["GET"])
def get_notes_of_a_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({"error": "category not found"})
    notes = [n.to_dict() for n in category.notes]

    return jsonify({
        "category": category.to_dict(),
        "count": len(notes),
        "notes": notes
    }),200

if __name__ == "__main__":
    app.run(debug=True)
