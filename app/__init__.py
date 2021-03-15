import json
from datetime import datetime
from flask import Flask, render_template, url_for, redirect, request
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# set FLASK_ENV=development


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(80))
    menu = db.Column(db.String(80))
    kafedra = db.Column(db.String(80))
    facultet = db.Column(db.String(80))
    view = db.Column(db.Integer(), default=0)
    image = db.Column(db.String(80))
    about = db.Column(db.Text)
    dolshnost = db.Column(db.String(80))
    feedbacks = db.relationship('Feedback', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.name

class Facultet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    kafedras = db.relationship('Kafedra', backref='facultet', lazy='dynamic')

    def __repr__(self):
        return '<Facultet %r>' % self.name

class Correct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=True, nullable=False)
    data = db.Column(db.String(80), unique=True, nullable=False)
    def __repr__(self):
        return '<Correct %r>' % self.data


class Kafedra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    facultet_id= db.Column(db.Integer, db.ForeignKey('facultet.id'))

    def __repr__(self):
        return '<Kafedra %r>' % self.name

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    pub_date = db.Column(db.DateTime)
    user_id= db.Column(db.Integer, db.ForeignKey('user.id'))
    def __repr__(self):
        return '<Feedback by %r>' % self.user.name



@app.route('/')
def index():
    menu = Facultet.query.all()
    return render_template('index.html', User=User.query.paginate(2,max_per_page=15).items, menu=menu, str=str, menu_type='Выберите факультет', title='КубГУ - мнение студентов')


@app.route('/fac/<int:facultetid>')
def facultet(facultetid):
    facultet_check = Facultet.query.filter_by(id=facultetid).first()
    menu = Kafedra.query.filter_by(facultet=facultet_check).all()
    return render_template('index.html', User=User.query.filter_by(facultet=facultet_check.name).all(), menu=menu, str=str,menu_type=facultet_check.name, title=facultet_check.name)


@app.route('/kaf/<int:kafedraid>')
def kafedra(kafedraid):
    facultet_check = Facultet.query.filter_by(id=Kafedra.query.filter_by(id=kafedraid).first().facultet_id).first()
    menu = Kafedra.query.filter_by(facultet=facultet_check).all()
    return render_template('index.html', User=User.query.filter_by(kafedra=Kafedra.query.filter_by(id=kafedraid).first().name).all(), menu=menu, str=str,menu_type=facultet_check.name, title=Kafedra.query.filter_by(id=kafedraid).first().name, check=facultet_check.id)


@app.route('/user/<int:prepodid>')
def user(prepodid):
    prepods = User.query.all()
    for prepod in prepods:
        if prepodid == prepod.id:
            prepod.view+=1
            db.session.commit()
            menu = Facultet.query.filter_by(name=prepod.facultet).first().kafedras.all()
            return render_template('user_page.html', prepod=prepod, menu=menu,len=len, str=str,kafedra=Kafedra.query.filter_by(name=prepod.kafedra).first())
    return redirect(url_for('index'))


@app.route('/correct', methods=['POST'])
def correct():
    data = request.form['correct']
    user_id = request.form['user']
    corr = Correct(data=data,user_id=user_id)
    db.session.add(corr)
    db.session.commit()
    return redirect('/user/'+str(user_id))


@app.route('/u/<int:prepodid>')
def u(prepodid):
    menu = Kafedra.query.all()
    prepods = User.query.all()
    for prepod in prepods:
        if prepodid == prepod.id:
            return render_template('user_page.html', prepod=prepod, menu=menu,len=len, str=str,kafedra=Kafedra.query.filter_by(name=prepod.kafedra).first())
    return redirect(url_for('index'))


@app.route('/menu/<int:menu_id>')
def menu(menu_id):
    kafedra = Kafedra.query.filter_by(id=menu_id).first()
    prepods = User.query.filter_by(kafedra=kafedra.name).all()
    return render_template('index.html', User=prepods,menu=Kafedra.query.all(), str=str )


@app.route('/feedback', methods=['POST'])
def feedback():
    msg = request.form['message']
    prepod=User.query.filter_by(name=request.form['prepod']).first()
    new_feedback = Feedback(body=msg, user=prepod)
    db.session.add(new_feedback)
    db.session.commit()
    return redirect(url_for('u', prepodid=prepod.id))


@app.route('/neffos')
def neffos():
    prepods = os.listdir('app/static/images/prepods')
    for i in prepods:
        if not i[:i.index('.')].isdigit():
            user = User.query.filter_by(name=i[:i.index('.')]).first()
            if not user:
                k = Kafedra.query.filter_by(name=i).all()
                if not k:
                    db.session.add(Kafedra(name=i))
                    db.session.commit()
                new_user = User(name=x[:x.index('.')], image=x, menu=i, kafedra=i)
                db.session.add(new_user)
                db.session.commit()
                os.rename('app/static/images/prepods/'+i+'/'+x,'app/static/images/prepods/'+str(new_user.id)+'.'+new_user.image.split('.')[1] )
    return 'ok'


@app.route('/sokspesha')
def delete():
    u = User.query.all()
    for i in u:
        i.view = 0
    Feedback.query.delete()
    db.session.commit()
    json.dumps({'headers':str(request.headers),'remote_addr':str(request.remote_addr), 'client_ip':request.environ['REMOTE_ADDR']})
    return 'all clean'
