from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user
from app.models import User
from app.models import Scan
from app.forms import StartScanForm
from app.search import find_all_with_work_id, find_scan_details_on_elastics
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from core.scan_manager import ScanManager
from app import db


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.route('/scan_details/<scan_id>')
@login_required
def scan_details(scan_id):
    scan = Scan.query.filter_by(scan_id=scan_id).first_or_404()
    # result, hit_count = find_all_with_work_id(scan_id)
    statistics = find_scan_details_on_elastics(scan_id)
    print(statistics)

    scan.completed_perc = round(statistics['host_count']['total'] * 100 / scan.ip_count, 2)
    scan.status = 'Completed' if scan.completed_perc == 100.0 else 'Running'

    return render_template('scan_details.html', scan=scan, statistics=statistics)


@app.route('/scan_list')
@login_required
def scan_list():
    scans = Scan.query.all()
    return render_template('scan_list.html', scans=scans)


@app.route('/start_scan', methods=['GET', 'POST'])
@login_required
def start_scan():
    form = StartScanForm()
    SCANNER = 'ugly'
    if form.validate_on_submit():
        sm = ScanManager()
        result = sm.send_to_scanners(scanner=SCANNER, host_string=form.ip.data, port_string=form.port.data, params_string=None)
        # print(result)
        if result is not None:
            scan = Scan(scan_id=result['scan_id'], ip=form.ip.data, port=form.port.data, params=form.params.data,
                        scanner=SCANNER, ip_count=result['ip_count'], owner=current_user)
            db.session.add(scan)
            db.session.commit()
            flash('Scan is started with scan_id: ' + result['scan_id'] + ' ip_count: ' + str(result['ip_count']))
            return redirect(url_for('scan_details', scan_id=result['scan_id']))
        else:
            flash('Unkown parameters')

    elif request.method == 'GET':
        form.ip.data = ''
        form.port.data = ''
    return render_template('start_scan.html', title='Start New Scan', form=form)
