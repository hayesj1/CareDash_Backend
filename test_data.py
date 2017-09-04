from REST import Doctor, Review
from REST import db

db.create_all()
d1 = Doctor('Dr. Jones')
db.session.add(d1)
db.session.commit()

r1d1 = Review(d1.id, 'He is cool')
r2d1 = Review(d1.id, 'He is so good with kids')
db.session.add(r1d1)
db.session.add(r2d1)
db.session.commit()

d2 = Doctor('Dr. Wong')
db.session.add(d2)
db.session.commit()

r1d2 = Review(d1.id, 'Dr. Wong took the time to answer all my questions. 5 Stars!')
r2d2 = Review(d1.id, 'She really knows her stuff!')
db.session.add(r1d2)
db.session.add(r2d2)
db.session.commit()

doctors = Doctor.query.all()
print(doctors)
