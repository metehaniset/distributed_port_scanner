from app import db
from app.models import User, Scan

# u = User(username='admin', email='admin@localhost')
#
# db.session.add(u)
# db.session.commit()

# users = User.query.all()
# for u in users:
#     print(u.id, u.username)
#
# u = User.query.get(1)
# s = Scan(scan_id='9666b652-d082-4d72-b26b-2c98fd696499', scan_params='192.168.1.0/24 20-100', owner=u)
# db.session.add(s)
# db.session.commit()
#
# u = User.query.get(1)
# scans = u.scans.all()
#
# for s in scans:
#     print(s.scan_id, s.scan_params)


