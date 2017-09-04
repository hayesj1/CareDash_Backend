import json

from flask import Flask, request, jsonify, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Change the assigned string if credentials and/or port are unavailable
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:hayesj3@localhost:5432/Doctors_Reviews'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # Gives a warning if not set
app.secret_key = '\xd0\xf9\x11\xd9\x84}\xb4\xd0J\x9dD\x10\xb9\t\xb6\x10%\xc3\xcbv\x9f\xfd\xbf\xac'
db = SQLAlchemy(app)

# Uncomment on first run to setup the database schema
# A database named "Doctors_Reviews" must be accessible on port 5432 with
# username "postgres" and password "hayesj3" must already exist
# db.create_all()


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))    # non-unique names for simplicity
    reviews = db.relationship('Review', backref=db.backref('Doctor', lazy='joined'), lazy='select')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Name %r>' % self.name


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    description = db.Column(db.String(240))

    def __init__(self, doctor_id, description):
        self.doctor_id = doctor_id
        self.description = description

    def __repr__(self):
        return '<Name %r> %r' % self.doctor_id % self.description


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Doctor):
            reviews = list(iter(obj.reviews))
            return {
                "id": obj.id,
                "name": obj.name,
                "reviews": reviews
            }
        elif isinstance(obj, Review):
            return {
                "id": obj.id,
                "doctor_id": obj.doctor_id,
                "description": obj.description
            }
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


@app.route('/')
def index():
    return redirect(url_for('doctors'))


@app.route('/doctors', methods=['GET'])
def retrieve_doctors():
    doctors = Doctor.query.all()
    return make_response(json.dumps(doctors, cls=CustomEncoder, indent=3), 200)


@app.route('/doctors/<int:doc_id>', methods=['GET'])
def retrieve_doctor(doc_id):
    doctor = Doctor.query.filter_by(id=doc_id).first()
    return make_response(json.dumps(doctor, cls=CustomEncoder, indent=3), 200)


@app.route('/doctors/<int:doc_id>/reviews', methods=['GET'])
def retrieve_reviews(doc_id):
    reviews = Review.query.filter_by(doctor_id=doc_id).all()
    doctor = Doctor.query.filter_by(id=doc_id).first()

    # Partially hardcoded json to preserve structure seen in prompt, and to avoid redundancy
    return make_response(json.dumps({ "reviews": reviews, "doctor": {"id": doctor.id, "name": doctor.name}}, cls=CustomEncoder, indent=3), 200)


@app.route('/doctors/<int:doc_id>/reviews/<int:review_id>', methods=['GET'])
def retrieve_review(doc_id, review_id):
    review = Review.query.filter_by(doctor_id=doc_id, id=review_id).first()
    doctor = Doctor.query.filter_by(id=doc_id).first()

    # Partially hardcoded json to preserve structure seen in prompt, and to avoid redundancy
    return make_response(json.dumps({ "review": review, "doctor": {"id": doctor.id, "name": doctor.name}}, cls=CustomEncoder, indent=3), 200)


@app.route('/doctors', methods=['POST'])
def add_doctor():
    dct = request.get_json(force=True)
    doctor = Doctor(dct["doctor"]["name"])
    db.session.add(doctor)
    db.session.commit()
    return make_response(jsonify({'status': 'CREATED'}), 201)


@app.route('/doctors/<int:doc_id>/reviews', methods=['POST'])
def add_review(doc_id):
    dct = request.get_json(force=True)
    review = Review(doc_id, dct["review"]["description"])
    db.session.add(review)
    db.session.commit()
    return make_response(jsonify({'status': 'CREATED'}), 201)


@app.route('/doctors/<int:doc_id>', methods=['DELETE'])
def delete_doctor(doc_id):
    doctor = Doctor.query.filter_by(id=doc_id).first()
    db.session.delete(doctor)
    db.session.commit()
    return make_response(jsonify({'status': 'DELETED'}), 204)


@app.route('/doctors/<int:doc_id>/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(doc_id, review_id):
    review = Review.query.filter_by(doctor_id=doc_id, id=review_id).first()
    db.session.delete(review)
    db.session.commit()
    return make_response(jsonify({'status': 'DELETED'}), 204)


if __name__ == '__main__':
    app.run(debug=False)
