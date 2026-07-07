from flask import Flask, render_template, request, redirect, session, flash,jsonify
import sqlite3, os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Create database if not exists
# def init_db():
#     if not os.path.exists("database.db"):
#         conn = sqlite3.connect("database.db")
#         c = conn.cursor()
#         c.execute("""
#             CREATE TABLE users(
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 name TEXT,
#                 email TEXT UNIQUE,
#                 password TEXT
#             )
#         """)
        
#         c.execute("""
#             CREATE TABLE IF NOT EXISTS courses(
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 name TEXT,
#                 description TEXT,
#                 level TEXT
#             )
#         """)
        
        
#         c.execute("""
#             CREATE TABLE IF NOT EXISTS subjects(
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 course_id INTEGER,
#                 name TEXT,
#                 FOREIGN KEY(course_id) REFERENCES courses(id)
#             )
#         """)
        
#         c.execute("""
#             CREATE TABLE IF NOT EXISTS resources(
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 course_id INTEGER,
#                 subject_id INTEGER,
#                 title TEXT,
#                 file_type TEXT,
#                 file_path TEXT,
#                 FOREIGN KEY(course_id) REFERENCES courses(id),
#                 FOREIGN KEY(subject_id) REFERENCES subjects(id)
#             )
#         """)
        
#         c.execute("""
#             CREATE TABLE IF NOT EXISTS quizzes(
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 course_id INTEGER,
#                 subject_id INTEGER,
#                 question TEXT,
#                 option1 TEXT,
#                 option2 TEXT,
#                 option3 TEXT,
#                 option4 TEXT,
#                 correct_option TEXT,
#                 FOREIGN KEY(course_id) REFERENCES courses(id),
#                 FOREIGN KEY(subject_id) REFERENCES subjects(id)
#             )
#         """)
        

#         c.execute("""
#             CREATE TABLE IF NOT EXISTS user_activity(
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 user_id INTEGER,
#                 course_id INTEGER,
#                 subject_id INTEGER,
#                 resource_id INTEGER,
#                 quiz_id INTEGER,
#                 score INTEGER,
#                 time_spent INTEGER,
#                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
#                 FOREIGN KEY(user_id) REFERENCES users(id),
#                 FOREIGN KEY(course_id) REFERENCES courses(id),
#                 FOREIGN KEY(subject_id) REFERENCES subjects(id),
#                 FOREIGN KEY(resource_id) REFERENCES resources(id),
#                 FOREIGN KEY(quiz_id) REFERENCES quizzes(id)
#             )
#         """)
        

#         conn.commit()
#         conn.close()

# init_db()

import os
import sqlite3

def init_db():
    if not os.path.exists("database.db"):
        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # Users table for registered users
        c.execute("""
            CREATE TABLE users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        # Courses table
        c.execute("""
            CREATE TABLE courses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                level TEXT
            )
        """)

        # Subjects table linked to courses
        c.execute("""
            CREATE TABLE subjects(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
        """)

        # Resources table linked to course and subject
        c.execute("""
            CREATE TABLE resources(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE,
                FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
            )
        """)

        # Quizzes table linked to course and subject
        c.execute("""
            CREATE TABLE quizzes(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                option1 TEXT NOT NULL,
                option2 TEXT NOT NULL,
                option3 TEXT NOT NULL,
                option4 TEXT NOT NULL,
                correct_option TEXT NOT NULL,
                FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE,
                FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
            )
        """)

        # User activity table tracking engagement and scores
        c.execute("""
            CREATE TABLE user_activity(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER,
                subject_id INTEGER,
                resource_id INTEGER,
                quiz_id INTEGER,
                score INTEGER,
                time_spent INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE SET NULL,
                FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE SET NULL,
                FOREIGN KEY(resource_id) REFERENCES resources(id) ON DELETE SET NULL,
                FOREIGN KEY(quiz_id) REFERENCES quizzes(id) ON DELETE SET NULL
            )
        """)

        conn.commit()
        conn.close()

init_db()

from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "static/uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4', 'avi'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# def allowed_file(filename):
#     return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS





# ---------------- HOME PAGE ----------------
@app.route("/")
def home():
    return render_template("home.html")

# ---------------- ADMIN LOGIN ----------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Default admin credentials
        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/admin/dashboard")
        else:
            flash("Invalid admin credentials")
            return redirect("/admin/login")

    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin/login")
    return render_template("admin_dashboard.html")

# ---------------- USER REGISTER ----------------
@app.route("/user/register", methods=["GET", "POST"])
def user_register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users(name,email,password) VALUES (?,?,?)",
                      (name, email, password))
            conn.commit()
            conn.close()
            flash("Registration Successful! Please Login.")
            return redirect("/user/login")
        except:
            flash("Email already exists!")
            return redirect("/user/register")

    return render_template("user_register.html")

# ---------------- USER LOGIN ----------------
@app.route("/user/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = user[0]
            return redirect("/user/dashboard")
        else:
            flash("Invalid Username or Password")
            return redirect("/user/login")

    return render_template("user_login.html")

# ---------------- USER DASHBOARD ----------------
@app.route("/user/dashboard")
def user_dashboard():
    if "user" not in session:
        return redirect("/user/login")
    return render_template("user_dashboard.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")




@app.route("/admin/users")
def admin_view_users():
    if "admin" not in session:
        return redirect("/admin/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT id, name, email FROM users")
    users = c.fetchall()
    conn.close()

    return render_template("admin_view_users.html", users=users)



# - ADMIN ADD COURSE
@app.route("/admin/courses", methods=["GET"])
def admin_courses():
    if "admin" not in session:
        return redirect("/admin/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM courses")
    courses = c.fetchall()
    conn.close()

    return render_template("admin_courses.html", courses=courses)



@app.route("/admin/courses/add", methods=["POST"])
def admin_add_course():
    if "admin" not in session:
        return redirect("/admin/login")

    name = request.form["name"]
    description = request.form["description"]
    level = request.form["level"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO courses(name, description, level) VALUES (?, ?, ?)",
              (name, description, level))
    conn.commit()
    conn.close()

    return redirect("/admin/courses")



@app.route("/admin/courses/edit/<int:cid>", methods=["GET", "POST"])
def edit_course(cid):
    if "admin" not in session:
        return redirect("/admin/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        level = request.form["level"]

        c.execute("""UPDATE courses 
                     SET name=?, description=?, level=? 
                     WHERE id=?""",
                  (name, description, level, cid))
        conn.commit()
        conn.close()
        return redirect("/admin/courses")

    c.execute("SELECT * FROM courses WHERE id=?", (cid,))
    course = c.fetchone()
    conn.close()

    return render_template("admin_edit_course.html", course=course)




@app.route("/admin/resources")
def admin_resources():
    if "admin" not in session:
        return redirect("/admin/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM courses")
    courses = c.fetchall()

    c.execute("SELECT r.id, r.title, r.file_type, r.file_path, c.name, s.name  FROM resources r  JOIN courses c ON r.course_id = c.id JOIN subjects s ON r.subject_id = s.id")

    resources = c.fetchall()
    conn.close()

    return render_template("admin_resources.html",
                           courses=courses,
                           resources=resources)



# @app.route("/admin/get_subjects/<int:course_id>")
# def get_subjects(course_id):
#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()
#     c.execute("SELECT id, name FROM subjects WHERE course_id=?", (course_id,))
#     subjects = c.fetchall()
#     conn.close()

#     return {"subjects": subjects}

@app.route('/admin/get_subjects/<int:course_id>')
def get_subjects(course_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, name FROM subjects WHERE course_id=?", (course_id,))
    subjects = c.fetchall()
    conn.close()
    return jsonify({'subjects': subjects})

# @app.route("/admin/resources/upload", methods=["POST"])
# def upload_resource():
#     if "admin" not in session:
#         return redirect("/admin/login")

#     course_id = request.form["course_id"]
#     subject_id = request.form["subject_id"]
#     title = request.form["title"]
#     file = request.files["file"]

#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

#         file_type = filename.split(".")[-1]

#         conn = sqlite3.connect("database.db")
#         c = conn.cursor()
#         c.execute("""
#             INSERT INTO resources(course_id, subject_id, title, file_type, file_path)
#             VALUES (?, ?, ?, ?, ?)""",
#             (course_id, subject_id, title, file_type, filename)
#         )
#         conn.commit()
#         conn.close()

#     return redirect("/admin/resources")
# Upload resources page + handle upload POST
from flask import Flask, render_template, request, redirect, url_for, g

@app.route('/admin/resources/upload', methods=['GET', 'POST'])
def upload_resources():
    if 'admin' not in session:
        return redirect('/admin/login')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Fetch courses for dropdown
    c.execute("SELECT id, name FROM courses")
    courses = c.fetchall()

    # Fetch uploaded resources with joined course and subject names
    c.execute('''
        SELECT r.id, r.title, r.type, r.filename, c.name, s.name
        FROM resources r
        JOIN courses c ON r.course_id = c.id
        JOIN subjects s ON r.subject_id = s.id
    ''')
    resources = c.fetchall()

    if request.method == 'POST':
        course_id = request.form.get('course_id')
        subject_id = request.form.get('subject_id')
        title = request.form.get('title')
        file = request.files.get('file')

        if not (course_id and subject_id and title and file and allowed_file(file.filename)):
            return "Missing or invalid data", 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)

        # Determine type by file extension (simple method)
        ext = filename.rsplit('.', 1)[1].lower()
        if ext in ['mp3']:
            filetype = 'audio'
        elif ext in ['mp4', 'avi']:
            filetype = 'video'
        elif ext in ['pdf']:
            filetype = 'pdf'
        else:
            filetype = 'text'

        # Insert into DB
        c.execute('''
            INSERT INTO resources (title, type, filename, course_id, subject_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, filetype, filename, course_id, subject_id))
        conn.commit()

        conn.close()
        return redirect(url_for('upload_resources'))

    conn.close()
    return render_template('admin_resources.html', courses=courses, resources=resources)



import sqlite3

app = Flask(__name__)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('database.db')
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()













@app.route('/admin/subjects', methods=['GET', 'POST'])
def admin_subjects():
    db = get_db()
    c = db.cursor()
    if request.method == 'POST':
        course_id = request.form['course_id']
        subject_name = request.form['subject_name']
        c.execute("INSERT INTO subjects (course_id, name) VALUES (?, ?)", (course_id, subject_name))
        db.commit()
        return redirect(url_for('admin_subjects'))

    # Get all courses for dropdown
    c.execute("SELECT id, name FROM courses")
    courses = c.fetchall()

    # Get all subjects joined with courses for display
    c.execute("""SELECT subjects.id, subjects.name, courses.name 
                 FROM subjects 
                 JOIN courses ON subjects.course_id = courses.id""")
    subjects = c.fetchall()

    return render_template('admin_subjects.html', courses=courses, subjects=subjects)

@app.route("/admin/quizzes")
def admin_quizzes():
    if "admin" not in session:
        return redirect("/admin/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM courses")
    courses = c.fetchall()

    c.execute("""SELECT q.id, q.question, c.name, s.name 
                 FROM quizzes q 
                 JOIN courses c ON q.course_id = c.id
                 JOIN subjects s ON q.subject_id = s.id""")
    quizzes = c.fetchall()
    conn.close()

    return render_template("admin_quizzes.html", courses=courses, quizzes=quizzes)




@app.route("/admin/quizzes/add", methods=["POST"])
def add_quiz():
    if "admin" not in session:
        return redirect("/admin/login")

    course_id = request.form["course_id"]
    subject_id = request.form["subject_id"]
    question = request.form["question"]
    option1 = request.form["option1"]
    option2 = request.form["option2"]
    option3 = request.form["option3"]
    option4 = request.form["option4"]
    correct_option = request.form["correct_option"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""INSERT INTO quizzes(course_id, subject_id, question, 
                                     option1, option2, option3, option4, correct_option)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
              (course_id, subject_id, question, option1, option2, option3, option4, correct_option))
    conn.commit()
    conn.close()

    return redirect("/admin/quizzes")




@app.route("/admin/quizzes/get_subjects/<int:course_id>")
def get_quiz_subjects(course_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT id, name FROM subjects WHERE course_id=?", (course_id,))
    subjects = c.fetchall()
    conn.close()
    return {"subjects": subjects}


@app.route("/user/resource/<int:resource_id>")
def view_resource(resource_id):
    if "user" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Get resource info
    c.execute("SELECT course_id, subject_id FROM resources WHERE id=?", (resource_id,))
    res = c.fetchone()

    if res:
        course_id, subject_id = res
        # Insert activity
        c.execute("""INSERT INTO user_activity(user_id, course_id, subject_id, resource_id, time_spent)
                     VALUES (?, ?, ?, ?, ?)""", (user_id, course_id, subject_id, resource_id, 5))  # example time_spent=5 sec
        conn.commit()
    conn.close()

    return f"Resource {resource_id} viewed!"



@app.route("/user/quiz/<int:quiz_id>/submit", methods=["POST"])
def submit_quiz(quiz_id):
    if "user" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    score = int(request.form.get("score", 0))  # assume score is calculated

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT course_id, subject_id FROM quizzes WHERE id=?", (quiz_id,))
    res = c.fetchone()

    if res:
        course_id, subject_id = res
        c.execute("""INSERT INTO user_activity(user_id, course_id, subject_id, quiz_id, score)
                     VALUES (?, ?, ?, ?, ?)""", (user_id, course_id, subject_id, quiz_id, score))
        conn.commit()

    conn.close()
    return f"Quiz {quiz_id} submitted with score {score}"



@app.route("/admin/engagement")
def monitor_engagement():
    if "admin" not in session:
        return redirect("/admin/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""SELECT ua.id, u.username, c.name, s.name, r.title, q.question, ua.score, ua.time_spent, ua.timestamp
                 FROM user_activity ua
                 LEFT JOIN users u ON ua.user_id = u.id
                 LEFT JOIN courses c ON ua.course_id = c.id
                 LEFT JOIN subjects s ON ua.subject_id = s.id
                 LEFT JOIN resources r ON ua.resource_id = r.id
                 LEFT JOIN quizzes q ON ua.quiz_id = q.id
                 ORDER BY ua.timestamp DESC
              """)
    activities = c.fetchall()
    conn.close()

    return render_template("admin_engagement.html", activities=activities)











if __name__ == "__main__":
    app.run(debug=True)
