from flask import Flask, render_template, request, redirect, session, flash,jsonify
import sqlite3, os

app = Flask(__name__)
app.secret_key = "your_secret_key"



# init_db()
import os
import sqlite3

def init_db():
    if not os.path.exists("database.db"):
        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # Users table
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

        # User activity table
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
# @app.route("/user/login", methods=["GET", "POST"])
# def user_login():
#     if request.method == "POST":
#         email = request.form["email"]
#         password = request.form["password"]

#         conn = sqlite3.connect("database.db")
#         c = conn.cursor()
#         c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
#         user = c.fetchone()
#         conn.close()

#         if user:
#             session["user_id"] = user[0]      # store ID for backend logic
#             session["user_name"] = user[1]    # store name for greeting
#             return redirect("/user/dashboard")

#         else:
#             flash("Invalid Username or Password")
#             return redirect("/user/login")

#     return render_template("user_login.html")
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
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            return redirect(url_for("user_dashboard"))
        else:
            flash("Invalid Username or Password")
            return redirect(url_for("user_login"))

    return render_template("user_login.html")



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
@app.route("/admin/courses")
def admin_courses():
    if "admin" not in session:
        return redirect("/admin/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Fetch all courses
    c.execute("SELECT * FROM courses")
    courses = c.fetchall()

    # Fetch subjects for each course
    courses_with_subjects = []
    for course in courses:
        c.execute("SELECT name FROM subjects WHERE course_id=?", (course[0],))
        subjects = [s[0] for s in c.fetchall()]
        courses_with_subjects.append({
            "id": course[0],
            "name": course[1],
            "description": course[2],
            "level": course[3],
            "subjects": ", ".join(subjects)
        })

    conn.close()
    return render_template("admin_courses.html", courses=courses_with_subjects)

# @app.route("/admin/courses", methods=["GET"])
# def admin_courses():
#     if "admin" not in session:
#         return redirect("/admin/login")

#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()
#     c.execute("SELECT * FROM courses")
#     courses = c.fetchall()
#     conn.close()

#     return render_template("admin_courses.html", courses=courses)

@app.route("/admin/courses/add", methods=["POST"])
def admin_add_course():
    if "admin" not in session:
        return redirect("/admin/login")

    name = request.form["name"]
    description = request.form["description"]
    level = request.form["level"]
    subjects_input = request.form.get("subjects", "")  # Optional field

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Insert course
    c.execute("INSERT INTO courses(name, description, level) VALUES (?, ?, ?)",
              (name, description, level))
    course_id = c.lastrowid  # Get the ID of the newly added course

    # Insert subjects if provided
    subjects = [s.strip() for s in subjects_input.split(",") if s.strip()]
    for subject_name in subjects:
        c.execute("INSERT INTO subjects(course_id, name) VALUES (?, ?)",
                  (course_id, subject_name))

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
        subjects_input = request.form.get("subjects", "")  # comma-separated subjects

        # Update course info
        c.execute("""UPDATE courses 
                     SET name=?, description=?, level=? 
                     WHERE id=?""",
                  (name, description, level, cid))

        # Delete existing subjects for this course
        c.execute("DELETE FROM subjects WHERE course_id=?", (cid,))

        # Insert updated subjects
        subjects = [s.strip() for s in subjects_input.split(",") if s.strip()]
        for subject_name in subjects:
            c.execute("INSERT INTO subjects(course_id, name) VALUES (?, ?)", (cid, subject_name))

        conn.commit()
        conn.close()
        return redirect("/admin/courses")

    # GET request: fetch course info
    c.execute("SELECT * FROM courses WHERE id=?", (cid,))
    course = c.fetchone()

    # Fetch existing subjects for display
    c.execute("SELECT name FROM subjects WHERE course_id=?", (cid,))
    subjects = [s[0] for s in c.fetchall()]

    conn.close()
    return render_template("admin_edit_course.html", course=course, subjects=subjects)





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
#     if "admin" not in session:
#         return jsonify({"error": "Unauthorized"}), 401  # Better than redirect for AJAX

#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()
#     c.execute("SELECT id, name FROM subjects WHERE course_id=?", (course_id,))
#     subjects = c.fetchall()
#     conn.close()

#     # Return JSON properly
#     # Example: {"subjects": [[1, "Math"], [2, "Science"]]}
#     return jsonify({"subjects": subjects})

@app.route("/user/get_subjects/<int:course_id>")
def get_subjects(course_id):
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT id, name FROM subjects WHERE course_id=?", (course_id,))
    subjects = c.fetchall()
    conn.close()

    # Proper JSON format
    return jsonify(subjects=[{"id": s[0], "name": s[1]} for s in subjects])


from flask import Flask, render_template, request, redirect, url_for, g

@app.route('/admin/resources/upload', methods=['GET', 'POST'])
def upload_resources():
    if 'admin' not in session:
        return redirect('/admin/login')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Fetch all courses
    c.execute("SELECT id, name FROM courses")
    courses = c.fetchall()

    # Fetch all subjects
    c.execute("SELECT id, name FROM subjects")
    subjects = c.fetchall()

    # Fetch resources with course & subject names
    c.execute('''
        SELECT r.id, r.title, r.file_type, r.file_path,
               COALESCE(c.name, '-') as course_name,
               COALESCE(s.name, '-') as subject_name
        FROM resources r
        LEFT JOIN courses c ON r.course_id = c.id
        LEFT JOIN subjects s ON r.subject_id = s.id
        ORDER BY r.id DESC
    ''')
    resources = c.fetchall()

    if request.method == 'POST':
        course_id = request.form.get('course_id')
        subject_id = request.form.get('subject_id')
        title = request.form.get('title')
        file = request.files.get('file')

        if not (course_id and subject_id and title and file and allowed_file(file.filename)):
            conn.close()
            return "Missing or invalid data", 400

        filename = secure_filename(file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Determine file type
        ext = filename.rsplit('.', 1)[1].lower()
        if ext in ['mp3']:
            file_type = 'audio'
        elif ext in ['mp4', 'avi', 'mov', 'mkv']:
            file_type = 'video'
        elif ext in ['pdf']:
            file_type = 'pdf'
        else:
            file_type = 'text'

        # Insert into DB
        c.execute('''
            INSERT INTO resources (title, file_type, file_path, course_id, subject_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, file_type, filename, course_id, subject_id))
        conn.commit()
        conn.close()
        return redirect(url_for('upload_resources'))

    conn.close()
    return render_template('admin_resources.html', courses=courses, subjects=subjects, resources=resources)


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
        return redirect("/user/login")  # fix

    user_id = session["user"]          # fix

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Get resource info
    c.execute("SELECT course_id, subject_id FROM resources WHERE id=?", (resource_id,))
    res = c.fetchone()

    if res:
        course_id, subject_id = res
        # Insert activity
        c.execute("""INSERT INTO user_activity(user_id, course_id, subject_id, resource_id, time_spent)
                     VALUES (?, ?, ?, ?, ?)""", (user_id, course_id, subject_id, resource_id, 5))
        conn.commit()
    conn.close()

    return f"Resource {resource_id} viewed!"



# @app.route("/user/quiz/<int:quiz_id>/submit", methods=["POST"])
# def submit_quiz(quiz_id):
#     if "user" not in session:
#         return redirect("/user/login")   # fix

#     user_id = session["user"]           # fix
#     score = int(request.form.get("score", 0))

#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()

#     c.execute("SELECT course_id, subject_id FROM quizzes WHERE id=?", (quiz_id,))
#     res = c.fetchone()

#     if res:
#         course_id, subject_id = res
#         c.execute("""INSERT INTO user_activity(user_id, course_id, subject_id, quiz_id, score)
#                      VALUES (?, ?, ?, ?, ?)""", (user_id, course_id, subject_id, quiz_id, score))
#         conn.commit()

#     conn.close()
#     return f"Quiz {quiz_id} submitted with score {score}"



@app.route("/admin/engagement")
def monitor_engagement():
    if "admin" not in session:
        return redirect("/admin/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""SELECT ua.id, u.name, c.name, s.name, r.title, q.question, ua.score, ua.time_spent, ua.timestamp
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




### USER

@app.route("/user/courses", methods=["GET", "POST"])
def choose_course_subject():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Fetch all courses
    c.execute("SELECT id, name FROM courses")
    courses = c.fetchall()
    subjects = []

    if request.method == "POST":
        course_id = request.form.get("course_id")
        subject_id = request.form.get("subject_id")
        if course_id and subject_id:
            session["course_id"] = course_id
            session["subject_id"] = subject_id
            return redirect("/user/resources")  # next step: recommended resources
        else:
            return "Please select course and subject", 400

    conn.close()
    return render_template("user_courses.html", courses=courses, subjects=subjects)



# app.py



from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3

# app = Flask(__name__)
# app.secret_key = "your_secret_key"

# # ---------------- User Dashboard ----------------
# @app.route("/user/dashboard")
# def user_dashboard():
#     if "user" not in session:
#         return redirect("/user/login")
#     return render_template("user_dashboard.html")


@app.route("/user/dashboard")
def user_dashboard():
    if "user_id" not in session:
        return redirect(url_for("user_login"))
    return render_template("user_dashboard.html", user_name=session.get("user_name"))


# ---------------- Learning Style ----------------
from flask import url_for

@app.route("/user/learning_style", methods=["GET", "POST"])
def learning_style():
    if "user_id" not in session:
        return redirect(url_for("user_login"))

    if request.method == "POST":
        style = request.form.get("learning_style")
        session["learning_style"] = style
        return redirect(url_for("user_courses"))  # use url_for
    return render_template("user_learning_style.html")


# # ---------------- Learning Style ----------------
# @app.route("/user/learning_style", methods=["GET", "POST"])
# def learning_style():
#     if "user_id" not in session:
#         return redirect("/user/login")

#     if request.method == "POST":
#         style = request.form.get("learning_style")
#         session["learning_style"] = style  # save selected style
#         return redirect("/user/courses")   # go to course selection

#     return render_template("user_learning_style.html")

# ---------------- Courses & Subjects ----------------
# @app.route("/user/courses", methods=["GET", "POST"])
# def user_courses():
#     if "user_id" not in session:
#         return redirect("/user/login")

#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()

#     # Fetch all courses
#     c.execute("SELECT id, name FROM courses")
#     courses = c.fetchall()
#     conn.close()

#     return render_template("user_courses.html", courses=courses)
# @app.route("/user/courses")
# def user_courses():
#     if "user_id" not in session:
#         return redirect("/user/login")

#     learning_style = session.get("learning_style")  # optional, if needed
#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()
#     c.execute("SELECT id, name FROM courses")
#     courses = c.fetchall()
#     conn.close()

#     return render_template("user_courses.html", courses=courses, learning_style=learning_style)

# ---------------- User Courses ----------------
# @app.route("/user/courses")
@app.route("/user/courses", methods=["GET", "POST"])
def user_courses():
    if "user" not in session:
        return redirect("/user/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Fetch all courses
    c.execute("SELECT id, name FROM courses")
    courses = c.fetchall()
    conn.close()

    return render_template("user_courses.html", courses=courses)


# ---------------- Fetch Subjects Dynamically ----------------
# @app.route("/user/fetch_subjects/<int:course_id>")
# def fetch_subjects(course_id):
#     if "user" not in session:
#         return redirect("/user/login")

#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()
#     c.execute("SELECT id, name FROM subjects WHERE course_id=?", (course_id,))
#     subjects = c.fetchall()
#     conn.close()

#     subjects_list = [{"id": s[0], "name": s[1]} for s in subjects]
#     return jsonify({"subjects": subjects_list})

# ---------------- Recommendations ----------------
# ---------------- User Recommendations ----------------
@app.route("/user/user_recommendations", methods=["GET", "POST"])
def user_recommendations():
    if "user_id" not in session:
        return redirect(url_for("user_login"))

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    courses = c.execute("SELECT id, name FROM courses").fetchall()
    subjects = []
    resources = []

    if request.method == "POST":
        selected_course = request.form.get("course")
        selected_subject = request.form.get("subject")

        if selected_course and selected_subject:
            c.execute("""
                SELECT title, file_type, file_path 
                FROM resources
                WHERE course_id=? AND subject_id=?
            """, (selected_course, selected_subject))
            resources = c.fetchall()

    conn.close()
    return render_template("user_recommendations.html",
                           courses=courses,
                           subjects=subjects,
                           resources=resources)


# Fetch subjects dynamically for dropdown

# ---------------- Fetch Subjects ----------------
@app.route("/user/get_subjects/<int:course_id>")
def fetch_subjects(course_id):
    if "user_id" not in session:
        return redirect(url_for("user_login"))

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT id, name FROM subjects WHERE course_id=?", (course_id,))
    subjects = c.fetchall()
    conn.close()

    return jsonify(subjects=[{"id": s[0], "name": s[1]} for s in subjects])










# @app.route("/user/get_subjects/<int:course_id>")
# def fetch_subjects(course_id):
#     if "user" not in session:
#         return redirect("/user/login")

#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()
#     c.execute("SELECT id, name FROM subjects WHERE course_id=?", (course_id,))
#     subjects = c.fetchall()
#     conn.close()

#     return jsonify(subjects=[{"id": s[0], "name": s[1]} for s in subjects])


# Load quiz page or fetch quiz based on selection
# @app.route("/user/quiz", methods=["GET", "POST"])
# def user_quiz():
#     if "user" not in session:
#         return redirect("/user/login")

#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()

#     # Always fetch courses for dropdown
#     c.execute("SELECT id, name FROM courses")
#     courses = c.fetchall()

#     quiz = None
#     selected_course = None
#     selected_subject = None

#     if request.method == "POST":
#         course_id = request.form.get("course_id")
#         subject_id = request.form.get("subject_id")

#         if not course_id or not subject_id:
#             flash("Please select a course and subject first.")
#             return redirect("/user/quiz")

#         # Fetch quiz questions
#         c.execute("""
#             SELECT * FROM quizzes
#             WHERE course_id=? AND subject_id=?
#         """, (course_id, subject_id))
#         rows = c.fetchall()
#         quiz = []
#         for row in rows:
#             quiz.append({
#                 "id": row[0],
#                 "course_id": row[1],
#                 "subject_id": row[2],
#                 "question": row[3],
#                 "option1": row[4],
#                 "option2": row[5],
#                 "option3": row[6],
#                 "option4": row[7],
#                 "correct_option": row[8]
#             })

#         # Get names
#         c.execute("SELECT name FROM courses WHERE id=?", (course_id,))
#         selected_course = c.fetchone()[0]
#         c.execute("SELECT name FROM subjects WHERE id=?", (subject_id,))
#         selected_subject = c.fetchone()[0]

#     conn.close()
#     return render_template("user_quiz.html",
#                            courses=courses,
#                            quiz=quiz,
#                            selected_course=selected_course,
#                            selected_subject=selected_subject)
# @app.route("/user/quiz", methods=["GET", "POST"])
# def user_quiz():
#     if "user" not in session:
#         flash("Please login first")
#         return redirect("/user/login")

#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()

#     courses = c.execute("SELECT id, name FROM courses").fetchall()
#     quiz = None

#     if request.method == "POST":
#         course_id = request.form.get("course")
#         subject_id = request.form.get("subject")

#         if course_id and subject_id:
#             # fetch quiz questions for selected course & subject
#             quiz = c.execute("""
#                 SELECT * FROM quizzes 
#                 WHERE course_id=? AND subject_id=?
#             """, (course_id, subject_id)).fetchall()
#         else:
#             flash("Please select both course and subject")

#     conn.close()
#     return render_template("user_quiz.html", courses=courses, quiz=quiz)

@app.route("/user/quiz", methods=["GET", "POST"])
def user_quiz():
    if "user_id" not in session:   # updated
        flash("Please login first")
        return redirect("/user/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    courses = c.execute("SELECT id, name FROM courses").fetchall()
    quiz = None

    if request.method == "POST":
        course_id = request.form.get("course")
        subject_id = request.form.get("subject")

        if course_id and subject_id:
            # fetch quiz questions for selected course & subject
            quiz = c.execute("""
                SELECT id, question, option1, option2, option3, option4 
                FROM quizzes 
                WHERE course_id=? AND subject_id=?
            """, (course_id, subject_id)).fetchall()
        else:
            flash("Please select both course and subject")

    conn.close()
    return render_template("user_quiz.html", courses=courses, quiz=quiz)


# Submit quiz and calculate marks
# @app.route("/user/quiz/submit", methods=["POST"])
# def submit_quiz():
#     if "user" not in session:
#         return redirect("/user/login")

#     # user_id = session["user"]
#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()

#     # Collect submitted answers
#     total = 0
#     correct = 0
#     for key, answer in request.form.items():
#         if key.startswith("q"):
#             quiz_id = int(key[1:])
#             c.execute("SELECT correct_option FROM quizzes WHERE id=?", (quiz_id,))
#             correct_option = c.fetchone()[0]
#             total += 1
#             if answer == correct_option:
#                 correct += 1

#     score = int((correct / total) * 100) if total else 0
#     flash(f"You scored {score}% ({correct}/{total})")

#     conn.close()
#     return redirect("/user/dashboard")


@app.route("/user/quiz/submit", methods=["POST"])
def submit_quiz():
    if "user_id" not in session:   # updated
        return redirect("/user/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    total = 0
    correct = 0

    for key, answer in request.form.items():
        if key.startswith("q"):
            quiz_id = int(key[1:])  # 'q1', 'q2', etc.
            c.execute("SELECT correct_option FROM quizzes WHERE id=?", (quiz_id,))
            correct_option = c.fetchone()[0]
            total += 1
            if answer == correct_option:
                correct += 1

    score = int((correct / total) * 100) if total else 0
    flash(f"You scored {score}% ({correct}/{total})")

    conn.close()
    return redirect("/user/dashboard")


if __name__ == "__main__":
    app.run(debug=True)
