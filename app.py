import sqlite3
from flask import Flask,render_template,g,request,session,redirect,url_for,flash
from werkzeug.security import generate_password_hash,check_password_hash
from db import get_db
import db

app = Flask(__name__)

app.config['SECRET_KEY'] = b'\xdd\x8c\xc5\xc9\xea+\x14\xb4\xb5\x01\xae\xe1)h\x92\xbf\xff\xffP\xd2\xda^\x85\x04'
db.init_app(app)

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db',None)
    if db is not None:
        db.close()

@app.before_request
def load_before_request():
    user_id = session.get('user_id')
    if user_id is None:
        g.user=None
    else:
        g.user = get_db().execute('select * from users WHERE id = ?',(user_id,)).fetchone()

@app.route('/')
def index():
    db = get_db()
    question_answer = db.execute('select questions.question_text, questions.answer_text, users.name from questions join users on users.id = questions.expert_id where answer_text is not null').fetchall()
    return render_template('index.html',question_answer=question_answer)

@app.route('/register/', methods = ['POST','GET'])
def register():
    error = None
    if request.method == 'POST':
        
        alert = False
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        # user = db.execute('select * from users where name = ?',(username,)).fetchone()
        # db.commit()
        
        try:
            db.execute('INSERT INTO users (name,password,admin,expert) VALUES (?,?,?,?)',(username,generate_password_hash(password),0,0)) 
            db.commit()
        except db.IntegrityError:
            error = f" User { username } already exist."
        if error is None:
            alert = True
            return render_template('register.html',alert=alert)
        flash(error)
    return render_template('register.html')

@app.route('/login/',methods = ["POST","GET"])
def login():
    error = None
    if request.method == "POST":
        db = get_db()
        username = request.form['username']
        password = request.form['password']
        user = db.execute('SELECT * FROM users WHERE name =?',(username,)).fetchone()
        if user is None or not check_password_hash(user['password'],password) :
            error = 'Invalid Credentials.'
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        flash(error)


    return render_template('login.html')

@app.route('/ask_question/', methods = ['GET','POST'])
def ask_question():
    if not g.user:
        return redirect('login')
    db = get_db()
    experts = db.execute('select id , name from users where expert = 1').fetchall()
    if request.method == 'POST':
        db.execute('insert into questions (question_text, ask_by_id, expert_id) values (?,?,?)',(request.form['question'], g.user['id'], request.form['expert']))
        db.commit()
    return render_template('ask_question.html',experts=experts)
    
@app.route('/unanswered')
def unanswered():
    if not g.user:
        return redirect('login')
    db = get_db()
    questions = db.execute('select questions.id,questions.question_text,users.name from questions join users on users.id = questions.ask_by_id where questions.answer_text is null and questions.expert_id = ?',(g.user['id'],)).fetchall()
    return render_template('unanswered.html',questions=questions)

@app.route('/answer/<question_id>', methods = ['GET','POST'])
def answer(question_id):
    db = get_db()
    question = db.execute('select id,question_text from questions where id = ?',(question_id,)).fetchone()

    if request.method == 'POST':
        db.execute('update  questions set answer_text = ? where id = ?',(request.form['answer'], question_id))
        db.commit()
        return redirect(url_for('unanswered'))
    return render_template('answer.html',question=question)

@app.route('/setup')
def setup():
    if not g.user:
        return redirect('login')
    db = get_db()
    users = db.execute('select * from users ').fetchall()
    return render_template('setup.html',users=users)

@app.route('/promote/<user_id>')
def promote(user_id):
    if not g.user:
        return redirect('login')
    db =get_db()
    db.execute('update users set expert=1 where id = ?',(user_id,))
    db.commit()
    
    return redirect(url_for('setup'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/database/')
def database():
    if not g.user:
        return redirect('login')
    db = get_db()
    users = db.execute('select * from users join questions on users.id = questions.ask_by_id').fetchall()
    return render_template('database.html',users=users)
        


if __name__ == '__main__':
    app.run(debug=True)