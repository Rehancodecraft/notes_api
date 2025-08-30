from flask import Flask,request,jsonify
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

from extensions import db
bycrypt = Bcrypt()

load_dotenv()
app = Flask(__name__)
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME")



DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["JWT_SECRET_KEY"] = os.getenv("SUPER_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
db.init_app(app)
jwt = JWTManager(app)
from models import Category, Note, User

with app.app_context():
    db.create_all()
#====================================================LOGIN & SIGNUP===========================================================

#<-----------------------SIGNUP------------------------>
@app.route("/signup",methods = ["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not password or not username:
        return jsonify({"error": "name and password are required fields!"}),400
    
    existing = User.query.filter_by(username=username).first()
    if existing:
        return jsonify({"error": "user already exist!"}),400
    
    hashed_pw = bycrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(username=username,password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"success": "user has been created!","user": new_user.to_dict()})

#<-----------------------LOGIN------------------------>
@app.route("/login",methods = ["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not password or not username:
        return jsonify({"error": "name and password are required fields!"}),400
    user = User.query.filter_by(username=username).first()
    if user and bycrypt.check_password_hash(user.password, password):
        jwt_token = create_access_token(identity=user.id)
        return jsonify({"Success": "You are successfully logged in!", "user": user.to_dict(),"access_token": jwt_token}),200
    elif not user:
        return jsonify({"error": "User does not exist"}),400
    else:
        return jsonify({"error": "wrong password, Try again!"}),400
    
    


#====================================================CATEGORY ENDPOINTS=======================================================

#<-----------------------CREATE CATEGORY------------------------>
@app.route("/categories", methods = ["POST"])
@jwt_required()
def create_category():
    user_id = get_jwt_identity()
    data = request.json
    name = data.get("name")
    if not name:
        return jsonify({"error": "category is required field!"}),400

    existing = Category.query.filter_by(user_id=user_id,name=name).first()
    if existing:
        return jsonify({"error": "category already exists!"}),400

    new_category = Category(name=name,user_id=user_id)
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
@jwt_required()
def get_all_categories():
    user_id = get_jwt_identity()
    categories = Category.query.filter_by(user_id=user_id).all()
    return jsonify([c.to_dict() for c in categories]),200

#<-----------------------GET CATEGORY BY ID------------------------>
@app.route("/category/<int:id>", methods = ["GET"])
@jwt_required()
def get_category(id):
    user_id = get_jwt_identity()
    category = Category.query.filter_by(id=id,user_id=user_id).first()
    if not category:
        return jsonify({"error": "category not found!"}),404
    return jsonify([category.to_dict()]),200

#<-----------------------UPDATE CATEGORY------------------------>
@app.route("/category/<int:id>",methods = ["PUT"])
@jwt_required()
def update_category(id):
    user_id = get_jwt_identity()
    category = Category.query.filter_by(id=id,user_id=user_id).first()
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
@jwt_required()
def delete_category(id):
    user_id= get_jwt_identity()
    category = Category.query.filter_by(id=id,user_id=user_id)
    if not category:
        return jsonify({"error": "category not found"}),404
    db.session.delete(category)
    db.session.commit()
    return jsonify({"success": "category deleted"}),200


#====================================================NOTES ENDPOINTS=======================================================

#<--------------CREATE NOTES------------------->
@app.route("/notes",methods = ["POST"])
@jwt_required()
def create_note():
    user_id = get_jwt_identity()
    data = request.json
    title = data.get("title")
    content = data.get("content")
    category_id = data.get("category_id")

    if not title:
        return jsonify({"error": "title is required!"}),400
    existing = Note.query.filter_by(title=title,user_id=user_id).first()
    if existing :
        return jsonify({"error": "note already exist"})
    if category_id is not None:
        category = Category.query.filter_by(id=category_id,user_id=user_id)
        if not category:
            return jsonify({"error": "category not found"}), 404

    new_note = Note(title=title,content=content,category_id=category_id,user_id=user_id)
    db.session.add(new_note)
    db.session.commit()
    return jsonify({"success": "note has been created","notes": new_note.to_dict()}),201

#<--------------GET ALL NOTES------------------->
@app.route("/notes",methods = ["GET"])
@jwt_required()
def get_all_notes():
    user_id = get_jwt_identity()
    notes = Note.query.filter_by(user_id=user_id).all()
    return jsonify([n.to_dict() for n in notes])


#<--------------GET NOTE BY ID------------------->
@app.route("/note/<int:id>",methods = ["GET"])
@jwt_required()
def get_note(id):
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=id,user_id=user_id).first()
    if not note:
        return jsonify({"error": "note not found!"}),404
    return jsonify(note.to_dict()),200


#<--------------UPDATE NOTE------------------->
@app.route("/note/<int:id>",methods = ["PUT"])
@jwt_required()
def update_note(id):
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=id,user_id=user_id).first()
    if not note:
        return jsonify({"error": "note not found!"}),404
    data = request.json
    title = data.get("title")
    content = data.get("content")
    category_id = data.get("category_id")
    if not title:
        return jsonify({"error": "title is required!"}),400

    if title:
        existing = Note.query.filter_by(title=title,user_id=user_id).first()
        if existing and existing.id != id:
            return jsonify({"error": "note with this title already exists"}), 400
        note.title = title

    if content is not None:
        note.content = content

    if category_id is not None:
        category = Category.query.filter_by(id=category_id,user_id=user_id)
        if not category:
            return jsonify({"error": "category not found"}), 404
        note.category_id = category_id

    db.session.commit()
    return jsonify({"success": "note updated", "note": note.to_dict()}), 200

#<--------------DELETE NOTE------------------->
@app.route("/notes/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_note(id):
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=id,user_id=user_id).first()
    if not note:
        return jsonify({"error": "note not found"}), 404

    db.session.delete(note)
    db.session.commit()
    return jsonify({"success": "note deleted"}), 200

#<--------------GET ALL NOTES OF A CATEGORY------------------->
@app.route("/category/<int:id>/notes",methods=["GET"])
@jwt_required()
def get_notes_of_a_category(id):
    user_id = get_jwt_identity()
    category = Category.query.filter_by(id=id,user_id=user_id).first()
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
