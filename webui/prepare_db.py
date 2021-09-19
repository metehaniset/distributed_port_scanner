from app import db
from app.models import User, Scan

# u = User(username='admin', email='admin@localhost')
# u.set_password('admin')
# db.session.add(u)
# db.session.commit()

# u = User.query.get(1)
# s = Scan(work_id='9666b652-d082-4d72-b26b-2c98fd696499', ip='192.168.1.0/24', port='20-100', owner=u)
# db.session.add(s)
# db.session.commit()


# users = User.query.all()
# for u in users:
#     print(u.id, u.username)
#
# u = User.query.get(1)
# s = Scan(work_id='9666b652-d082-4d72-b26b-2c98fd696499', scan_params='192.168.1.0/24 20-100', owner=u)
# db.session.add(s)
# db.session.commit()
#
# u = User.query.get(1)
# scans = u.scans.all()
#
# for s in scans:
#     print(s.work_id, s.scan_params)


# Remove all records on DB
# users = User.query.all()
# for u in users:
#     db.session.delete(u)
#
# posts = Scan.query.all()
# for p in posts:
#     db.session.delete(p)
#
# db.session.commit()
