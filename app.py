from flask import Flask, render_template, request, redirect, session, flash, jsonify, url_for
import sqlite3
import os
import json
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4', 'avi'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------------- DATABASE INIT ----------------
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

        # Subjects table
        c.execute("""
            CREATE TABLE subjects(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
        """)

        # Resources table
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

        # Quizzes table
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

        # Quiz history table
        c.execute("""
            CREATE TABLE quiz_history(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER,
                subject_id INTEGER,
                score INTEGER NOT NULL,
                correct INTEGER NOT NULL,
                total INTEGER NOT NULL,
                cognitive_state TEXT,
                engagement_level TEXT,
                time_spent INTEGER DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE SET NULL,
                FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE SET NULL
            )
        """)

        conn.commit()
        conn.close()

init_db()

# Migrate existing database - add quiz_history table if it doesn't exist
def migrate_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quiz_history'")
    if not c.fetchone():
        c.execute("""
            CREATE TABLE quiz_history(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER,
                subject_id INTEGER,
                score INTEGER NOT NULL,
                correct INTEGER NOT NULL,
                total INTEGER NOT NULL,
                cognitive_state TEXT,
                engagement_level TEXT,
                time_spent INTEGER DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE SET NULL,
                FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE SET NULL
            )
        """)
        conn.commit()
    conn.close()

migrate_db()


# Add difficulty column to quizzes & resources if missing (for dynamic difficulty adjustment)
def migrate_difficulty():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    for table in ("quizzes", "resources"):
        c.execute(f"PRAGMA table_info({table})")
        cols = [row[1] for row in c.fetchall()]
        if "difficulty" not in cols:
            try:
                c.execute(f"ALTER TABLE {table} ADD COLUMN difficulty TEXT DEFAULT 'medium'")
                pass  # Migration successful
            except Exception as e:
                pass  # Table already exists
    conn.commit()
    conn.close()

migrate_difficulty()


# ---------------- AUTO-SEED DATABASE ON STARTUP ----------------
def auto_seed():
    """Seed courses, subjects, quizzes, and resources if the database is empty."""
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM courses")
    if c.fetchone()[0] > 0:
        conn.close()
        return  # Already seeded

    # Courses and subjects
    courses = [
        ("Data Science", "Learn data science fundamentals", "Beginner",
         ["Python", "NumPy", "Pandas"]),
        ("Java", "Master Java programming", "Intermediate",
         ["Core Java", "OOP Concepts"]),
        ("PowerBI", "Business analytics with Power BI", "Beginner",
         ["Introduction to PowerBI", "DAX and Visualizations"]),
        ("Web Development", "Build modern web applications", "Beginner",
         ["HTML & CSS", "JavaScript"]),
        ("Machine Learning", "Learn ML algorithms", "Advanced",
         ["Supervised Learning"]),
    ]

    for name, desc, level, subjects in courses:
        c.execute("INSERT INTO courses(name, description, level) VALUES (?,?,?)",
                  (name, desc, level))
        course_id = c.lastrowid
        for subj in subjects:
            c.execute("INSERT INTO subjects(course_id, name) VALUES (?,?)",
                      (course_id, subj))

    conn.commit()

    # Seed quizzes
    quizzes = {
        "Python": [
            ("Which keyword defines a function in Python?", "func", "def", "function", "define", "def", "easy"),
            ("What is the output of print(type([]))?", "<class 'list'>", "<class 'tuple'>", "<class 'dict'>", "<class 'set'>", "<class 'list'>", "easy"),
            ("Which method adds to the end of a list?", "push()", "add()", "append()", "insert()", "append()", "medium"),
            ("What does 'self' refer to in a class?", "The class itself", "The instance", "A static var", "Parent class", "The instance", "medium"),
            ("What is a lambda function?", "A named function", "An anonymous function", "A recursive function", "A class method", "An anonymous function", "hard"),
        ],
        "NumPy": [
            ("Which creates a NumPy array?", "np.array()", "np.list()", "np.make()", "np.new()", "np.array()", "easy"),
            ("Default type of np.zeros()?", "int", "float", "bool", "str", "float", "easy"),
            ("Which gives array shape?", ".size", ".shape", ".dim", ".len", ".shape", "medium"),
            ("np.arange(0,10,2) returns?", "[0,2,4,6,8]", "[0,1,2]", "[2,4,6,8,10]", "[0,10]", "[0,2,4,6,8]", "medium"),
            ("Matrix multiplication function?", "np.mul()", "np.dot()", "np.times()", "np.prod()", "np.dot()", "hard"),
        ],
        "Pandas": [
            ("2D structure in Pandas?", "Series", "DataFrame", "Panel", "Array", "DataFrame", "easy"),
            ("Read CSV in Pandas?", "pd.read_csv()", "pd.load_csv()", "pd.open_csv()", "pd.csv()", "pd.read_csv()", "easy"),
            ("Drop missing values?", "fill()", "dropna()", "remove()", "clean()", "dropna()", "medium"),
            ("df.head() returns?", "Last 5 rows", "First 5 rows", "Columns", "Shape", "First 5 rows", "medium"),
            ("Group data method?", "groupby()", "sortby()", "splitby()", "cluster()", "groupby()", "hard"),
        ],
        "Core Java": [
            ("Keyword to declare a class?", "class", "Class", "new", "define", "class", "easy"),
            ("Entry point of Java program?", "start()", "main()", "run()", "init()", "main()", "easy"),
            ("Loop that runs at least once?", "for", "while", "do-while", "foreach", "do-while", "medium"),
            ("Size of int in Java?", "2 bytes", "4 bytes", "8 bytes", "Depends", "4 bytes", "medium"),
            ("Keyword to prevent inheritance?", "static", "final", "const", "sealed", "final", "hard"),
        ],
        "OOP Concepts": [
            ("Which hides internal details?", "Inheritance", "Polymorphism", "Encapsulation", "Abstraction", "Encapsulation", "easy"),
            ("Which allows code reuse?", "Polymorphism", "Inheritance", "Encapsulation", "Overloading", "Inheritance", "easy"),
            ("Overloading is which polymorphism?", "Runtime", "Compile-time", "Inheritance", "Abstraction", "Compile-time", "medium"),
            ("Keyword to inherit in Java?", "implements", "extends", "inherits", "super", "extends", "medium"),
            ("What is an abstract class?", "Only static methods", "Cannot be instantiated", "A final class", "A private class", "Cannot be instantiated", "hard"),
        ],
        "Introduction to PowerBI": [
            ("Power BI is used for?", "Coding", "Data visualization", "Gaming", "Word processing", "Data visualization", "easy"),
            ("Who developed Power BI?", "Google", "Microsoft", "Oracle", "IBM", "Microsoft", "easy"),
            ("Build reports in which view?", "Report view", "Data view", "Model view", "Query view", "Report view", "medium"),
            ("Power BI file format?", ".pbix", ".pbi", ".pwr", ".bix", ".pbix", "medium"),
            ("Power Query is for?", "Visualization", "Data transformation", "Modeling", "Publishing", "Data transformation", "hard"),
        ],
        "DAX and Visualizations": [
            ("DAX stands for?", "Data Analysis Expressions", "Digital Analytics Extension", "Data Access XML", "Dynamic Axis Engine", "Data Analysis Expressions", "easy"),
            ("Chart for parts of whole?", "Line", "Pie chart", "Bar", "Scatter", "Pie chart", "easy"),
            ("Current date in DAX?", "NOW()", "TODAY()", "DATE()", "CURRENT()", "TODAY()", "medium"),
            ("Sum a column in DAX?", "ADD()", "SUM()", "TOTAL()", "PLUS()", "SUM()", "medium"),
            ("CALCULATE is used to?", "Modify filter context", "Create tables", "Sort data", "Render visuals", "Modify filter context", "hard"),
        ],
        "HTML & CSS": [
            ("HTML stands for?", "Hyper Text Markup Language", "High Text Machine Language", "Hyperlink Text Mark Language", "Home Tool Markup Language", "Hyper Text Markup Language", "easy"),
            ("Line break tag?", "<break>", "<lb>", "<br>", "<newline>", "<br>", "easy"),
            ("CSS property for text color?", "font-color", "text-color", "color", "foreground", "color", "medium"),
            ("Semantic HTML tag?", "<div>", "<span>", "<article>", "<b>", "<article>", "medium"),
            ("CSS flex enables?", "Grid layout", "Flexible box layout", "Animation", "Transitions", "Flexible box layout", "hard"),
        ],
        "JavaScript": [
            ("Declares a constant?", "var", "let", "const", "static", "const", "easy"),
            ("typeof null returns?", "null", "object", "undefined", "number", "object", "easy"),
            ("Add to end of array?", "push()", "pop()", "shift()", "unshift()", "push()", "medium"),
            ("What is the DOM?", "Data Object Model", "Document Object Model", "Digital Ordered Map", "Display Object Mode", "Document Object Model", "medium"),
            ("'this' in arrow function?", "The function", "Global object", "Enclosing lexical scope", "undefined", "Enclosing lexical scope", "hard"),
        ],
        "Supervised Learning": [
            ("Supervised learning uses?", "Unlabeled data", "Labeled data", "No data", "Reward signals", "Labeled data", "easy"),
            ("Classification algorithm?", "K-Means", "Linear Regression", "Decision Tree", "PCA", "Decision Tree", "easy"),
            ("Classification metric?", "MSE", "Accuracy", "RMSE", "R-squared", "Accuracy", "medium"),
            ("Predicts continuous values?", "Logistic Regression", "Linear Regression", "KNN Classifier", "Naive Bayes", "Linear Regression", "medium"),
            ("What is overfitting?", "Model too simple", "Model fits noise", "Low accuracy", "Fast training", "Model fits noise", "hard"),
        ],
    }

    for subj_name, questions in quizzes.items():
        c.execute("SELECT id, course_id FROM subjects WHERE name=?", (subj_name,))
        row = c.fetchone()
        if not row:
            continue
        subj_id, crs_id = row
        for q, o1, o2, o3, o4, correct, diff in questions:
            c.execute("""INSERT INTO quizzes(course_id, subject_id, question,
                         option1, option2, option3, option4, correct_option, difficulty)
                         VALUES (?,?,?,?,?,?,?,?,?)""",
                      (crs_id, subj_id, q, o1, o2, o3, o4, correct, diff))

    # Video and audio URLs per subject
    media_urls = {
        "Python": ("https://www.youtube.com/embed/kqtD5dpn9C8", "https://www.youtube.com/embed/rfscVS0vtbw"),
        "NumPy": ("https://www.youtube.com/embed/QUT1VHiLmmI", "https://www.youtube.com/embed/8JfDAm9y_7s"),
        "Pandas": ("https://www.youtube.com/embed/vmEHCJofslg", "https://www.youtube.com/embed/zmdjNSmRXF4"),
        "Core Java": ("https://www.youtube.com/embed/eIrMbAQSU34", "https://www.youtube.com/embed/grEKMHGYyns"),
        "OOP Concepts": ("https://www.youtube.com/embed/pTB0EiLXUC8", "https://www.youtube.com/embed/6T_HgnjoYwM"),
        "Introduction to PowerBI": ("https://www.youtube.com/embed/AGrl-H87pRU", "https://www.youtube.com/embed/TmhQCQr_DCA"),
        "DAX and Visualizations": ("https://www.youtube.com/embed/9OyVYTlZa2Y", "https://www.youtube.com/embed/CGl228sEsuI"),
        "HTML & CSS": ("https://www.youtube.com/embed/mU6anWqZJcc", "https://www.youtube.com/embed/G3e-cpL7ofc"),
        "JavaScript": ("https://www.youtube.com/embed/PkZNo7MFNFg", "https://www.youtube.com/embed/hdI2bqOjy3c"),
        "Supervised Learning": ("https://www.youtube.com/embed/4qVRBYAdLAo", "https://www.youtube.com/embed/ukzFI9rgwfU"),
    }

    # Seed resources: text notes + video + audio for each subject
    c.execute("SELECT s.id, s.course_id, s.name FROM subjects s")
    for subj_id, crs_id, subj_name in c.fetchall():
        # Text notes
        notes_filename = f"notes_{crs_id}_{subj_id}.txt"
        notes_path = os.path.join(UPLOAD_FOLDER, notes_filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        if not os.path.exists(notes_path):
            with open(notes_path, "w", encoding="utf-8") as f:
                f.write(f"{subj_name} - Study Notes\n\nComprehensive notes for {subj_name}.")
        c.execute("""INSERT INTO resources(title, file_type, file_path, course_id, subject_id, difficulty)
                     VALUES (?,?,?,?,?,?)""",
                  (f"{subj_name} - Study Notes", "text", f"uploads/{notes_filename}", crs_id, subj_id, "medium"))

        # Video and audio
        urls = media_urls.get(subj_name, ("https://www.youtube.com/embed/rfscVS0vtbw", "https://www.youtube.com/embed/rfscVS0vtbw"))
        c.execute("""INSERT INTO resources(title, file_type, file_path, course_id, subject_id, difficulty)
                     VALUES (?,?,?,?,?,?)""",
                  (f"{subj_name} - Video Tutorial", "video", urls[0], crs_id, subj_id, "medium"))
        c.execute("""INSERT INTO resources(title, file_type, file_path, course_id, subject_id, difficulty)
                     VALUES (?,?,?,?,?,?)""",
                  (f"{subj_name} - Audio Lecture", "audio", urls[1], crs_id, subj_id, "medium"))

    conn.commit()
    conn.close()

auto_seed()


# ---------------- DIFFICULTY ADJUSTMENT (driven by cognitive state) ----------------
def decide_target_difficulty(cognitive_state=None, engagement_level=None, last_score=None):
    """
    Dynamically decide the next difficulty level based on the learner's
    predicted cognitive state and recent quiz performance.
    Returns one of: 'easy', 'medium', 'hard'.
    """
    negative_states = {"confused", "stressed", "tired", "sad", "fear"}
    positive_states = {"engaged", "focused", "happy"}

    score_level = None
    if last_score is not None:
        if last_score < 50:
            score_level = "low"
        elif last_score < 80:
            score_level = "mid"
        else:
            score_level = "high"

    # Cognitive state dominates the decision
    if cognitive_state in negative_states or engagement_level == "Low Engagement":
        return "easy"
    if cognitive_state in positive_states or engagement_level == "Highly Engaged":
        if score_level == "low":
            return "medium"
        return "hard"
    # Neutral / unknown cognitive state → follow performance
    if score_level == "high":
        return "hard"
    if score_level == "low":
        return "easy"
    return "medium"


# ---------------- PRE-WARM FER DETECTOR (background thread) ----------------
_fer_detector = None
_fer_loading = False
_fer_available = False

# Try importing FER dependencies at module level
try:
    import cv2 as _cv2
    import numpy as _np
    _fer_available = True
except ImportError:
    _fer_available = False

def preload_fer():
    """Load FER in background so Flask starts immediately."""
    global _fer_detector, _fer_loading
    _fer_loading = True
    try:
        from fer import FER
        _fer_detector = FER(mtcnn=False)
    except Exception as e:
        _fer_detector = None
    finally:
        _fer_loading = False

if _fer_available:
    import threading
    threading.Thread(target=preload_fer, daemon=True).start()


# ---------------- UTILS ----------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")


# ---------------- ADMIN ----------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/admin/dashboard")
        flash("Invalid admin credentials")
    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin/login")
    return render_template("admin_dashboard.html")


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


# ---------------- COURSES ----------------
@app.route("/admin/courses")
def admin_courses():
    if "admin" not in session:
        return redirect("/admin/login")
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM courses")
    courses = c.fetchall()
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


@app.route("/admin/courses/add", methods=["POST"])
def admin_add_course():
    if "admin" not in session:
        return redirect("/admin/login")
    name = request.form["name"]
    description = request.form["description"]
    level = request.form["level"]
    subjects_input = request.form.get("subjects", "")
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO courses(name, description, level) VALUES (?, ?, ?)",
              (name, description, level))
    course_id = c.lastrowid
    subjects = [s.strip() for s in subjects_input.split(",") if s.strip()]
    for subject_name in subjects:
        c.execute("INSERT INTO subjects(course_id, name) VALUES (?, ?)", (course_id, subject_name))
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
        subjects_input = request.form.get("subjects", "")
        c.execute("UPDATE courses SET name=?, description=?, level=? WHERE id=?",
                  (name, description, level, cid))
        c.execute("DELETE FROM subjects WHERE course_id=?", (cid,))
        subjects = [s.strip() for s in subjects_input.split(",") if s.strip()]
        for subject_name in subjects:
            c.execute("INSERT INTO subjects(course_id, name) VALUES (?, ?)", (cid, subject_name))
        conn.commit()
        conn.close()
        return redirect("/admin/courses")
    c.execute("SELECT * FROM courses WHERE id=?", (cid,))
    course = c.fetchone()
    c.execute("SELECT name FROM subjects WHERE course_id=?", (cid,))
    subjects = [s[0] for s in c.fetchall()]
    conn.close()
    return render_template("admin_edit_course.html", course=course, subjects=subjects)


# ---------------- RESOURCES ----------------
@app.route("/admin/resources")
def admin_resources():
    if "admin" not in session:
        return redirect("/admin/login")
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM courses")
    courses = c.fetchall()
    c.execute("""SELECT r.id, r.title, r.file_type, r.file_path, c.name, s.name
                 FROM resources r
                 JOIN courses c ON r.course_id = c.id
                 JOIN subjects s ON r.subject_id = s.id""")
    resources = c.fetchall()
    conn.close()
    return render_template("admin_resources.html", courses=courses, resources=resources)


@app.route("/admin/resources/upload", methods=['GET', 'POST'])
def upload_resources():
    if 'admin' not in session:
        return redirect('/admin/login')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, name FROM courses")
    courses = c.fetchall()
    c.execute("SELECT id, name FROM subjects")
    subjects = c.fetchall()
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
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        ext = filename.rsplit('.', 1)[1].lower()
        if ext in ['mp3']: file_type='audio'
        elif ext in ['mp4', 'avi', 'mov', 'mkv']: file_type='video'
        elif ext in ['pdf']: file_type='pdf'
        else: file_type='text'
        c.execute("INSERT INTO resources (title, file_type, file_path, course_id, subject_id) VALUES (?,?,?,?,?)",
                  (title, file_type, filename, course_id, subject_id))
        conn.commit()
        conn.close()
        return redirect(url_for('upload_resources'))
    conn.close()
    return render_template('admin_resources.html', courses=courses, subjects=subjects)


# ---------------- QUIZZES ----------------
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
    c.execute("""INSERT INTO quizzes(course_id, subject_id, question, option1, option2, option3, option4, correct_option)
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


# ---------------- USER ----------------
@app.route("/user/register", methods=["GET", "POST"])
def user_register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users(name,email,password) VALUES (?,?,?)", (name,email,hashed_password))
            conn.commit()
            flash("Registration Successful! Please Login.")
            return redirect("/user/login")
        except:
            flash("Email already exists!")
            return redirect("/user/register")
        finally:
            conn.close()
    return render_template("user_register.html")


@app.route("/user/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            return redirect("/user/dashboard")
        flash("Invalid Username or Password")
    return render_template("user_login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# @app.route("/user/dashboard")
# def user_dashboard():
#     if "user_id" not in session:
#         return redirect("/user/login")
#     return render_template("user_dashboard.html", user_name=session.get("user_name"))


# # ---------------- USER COURSES / RESOURCES ----------------
# @app.route("/user/courses", methods=["GET", "POST"])
# def user_courses():
#     if "user_id" not in session:
#         return redirect("/user/login")
#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()
#     c.execute("SELECT id, name FROM courses")
#     courses = c.fetchall()
#     subjects = []
#     selected_course = None
#     if request.method == "POST":
#         selected_course = request.form.get("course_id")
#         selected_subject = request.form.get("subject_id")
#         if selected_course and selected_subject:
#             session["course_id"] = selected_course
#             session["subject_id"] = selected_subject
#             return redirect("/user/user_recommendations")
#     if selected_course:
#         c.execute("SELECT id, name FROM subjects WHERE course_id=?", (selected_course,))
#         subjects = c.fetchall()
#     conn.close()
#     return render_template("user_courses.html", courses=courses, subjects=subjects, selected_course=selected_course)


# @app.route("/user/user_recommendations", methods=["GET", "POST"])
# def user_recommendations():
#     if "user_id" not in session:
#         return redirect("/user/login")
#     course_id = session.get("course_id")
#     subject_id = session.get("subject_id")
#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()
#     c.execute("SELECT title, file_type, file_path FROM resources WHERE course_id=? AND subject_id=?", (course_id, subject_id))
#     resources = c.fetchall()
#     conn.close()
#     return render_template("user_recommendations.html", resources=resources)


# # ---------------- VIEW RESOURCE ----------------
# @app.route("/user/resource/<int:resource_id>")
# def view_resource(resource_id):
#     if "user_id" not in session:
#         return redirect("/user/login")
#     user_id = session["user_id"]
#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()
#     c.execute("SELECT course_id, subject_id FROM resources WHERE id=?", (resource_id,))
#     res = c.fetchone()
#     if res:
#         course_id, subject_id = res
#         c.execute("""INSERT INTO user_activity(user_id, course_id, subject_id, resource_id, time_spent)
#                      VALUES (?, ?, ?, ?, ?)""", (user_id, course_id, subject_id, resource_id, 5))
#         conn.commit()
#     conn.close()
#     return f"Resource {resource_id} viewed!"

# from flask import Flask, render_template, request, redirect, session

# # app = Flask(__name__)
# # app.secret_key = "your_secret_key"  # make sure you have this

# @app.route("/user/learning_style", methods=["GET", "POST"])
# def learning_style():
#     if "user_id" not in session:
#         return redirect("/user/login")
    
#     if request.method == "POST":
#         selected_style = request.form.get("learning_style")
#         # Save the learning style in session or database
#         session["learning_style"] = selected_style
#         # Redirect to next page, for example, recommendations
#         return redirect("/user/recommendations")
    
#     # For GET request, just render the form
#     return render_template("user_learning_style.html")


# # ---------------- QUIZ ----------------
# @app.route("/user/quiz", methods=["GET", "POST"])
# def user_quiz():
#     if "user_id" not in session:
#         return redirect("/user/login")
#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()
#     c.execute("SELECT id, name FROM courses")
#     courses = c.fetchall()
#     quiz = []
#     subjects = []
#     selected_course = None
#     if request.method == "POST":
#         selected_course = request.form.get("course_id")
#         selected_subject = request.form.get("subject_id")
#         if selected_course:
#             c.execute("SELECT id, name FROM subjects WHERE course_id=?", (selected_course,))
#             subjects = c.fetchall()
#         if selected_course and selected_subject:
#             c.execute("SELECT * FROM quizzes WHERE course_id=? AND subject_id=?", (selected_course, selected_subject))
#             quiz = c.fetchall()
#     conn.close()
#     return render_template("user_quiz.html", courses=courses, subjects=subjects, quiz=quiz, selected_course=selected_course)


# @app.route("/user/quiz/submit", methods=["POST"])
# def submit_quiz():
#     if "user_id" not in session:
#         return redirect("/user/login")
#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()
#     total = 0
#     correct = 0
#     for key, answer in request.form.items():
#         if key.startswith("q"):
#             qid = int(key[1:])
#             c.execute("SELECT correct_option FROM quizzes WHERE id=?", (qid,))
#             correct_option = c.fetchone()[0]
#             total += 1
#             if answer == correct_option:
#                 correct += 1
#     score = int((correct / total) * 100) if total else 0
#     flash(f"You scored: {score}% ({correct}/{total})")
#     conn.close()
#     return redirect("/user/dashboard")

# from flask import Flask, render_template, request, redirect, session, flash, jsonify
# import sqlite3

# app = Flask(__name__)
# app.secret_key = "your_secret_key"

# ---------------------- USER DASHBOARD ----------------------
@app.route("/user/dashboard")
def user_dashboard():
    if "user_id" not in session:
        return redirect("/user/login")
    return render_template("user_dashboard.html", user_name=session.get("user_name"))


# ---------------------- LEARNING STYLE ----------------------
@app.route("/user/learning_style", methods=["GET", "POST"])
def learning_style():
    if "user_id" not in session:
        return redirect("/user/login")

    if request.method == "POST":
        session["learning_style"] = request.form.get("learning_style")
        return redirect("/user/courses")

    return render_template("user_learning_style.html")


# ---------------------- SELECT COURSE + SUBJECT ----------------------
@app.route("/user/courses", methods=["GET", "POST"])
def user_courses():
    if "user_id" not in session:
        return redirect("/user/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Load all courses
    c.execute("SELECT id, name FROM courses")
    courses = c.fetchall()

    selected_course = None
    subjects = []

    if request.method == "POST":
        # Handle form submission for course selection
        selected_course = request.form.get("course_id")
        selected_subject = request.form.get("subject_id")
        
        # If both course and subject are selected, redirect to recommendations
        if selected_course and selected_subject:
            session["course_id"] = selected_course
            session["subject_id"] = selected_subject
            conn.close()
            return redirect("/user/recommendations")
        
        # If only course is selected, load its subjects
        elif selected_course:
            c.execute("SELECT id, name FROM subjects WHERE course_id=?", (selected_course,))
            subjects = c.fetchall()
    
    else:  # GET request
        # Check if course was previously selected via query parameter or session
        selected_course = request.args.get("course_id") or session.get("course_id")
        if selected_course:
            c.execute("SELECT id, name FROM subjects WHERE course_id=?", (selected_course,))
            subjects = c.fetchall()

    conn.close()

    return render_template("user_courses.html",
                           courses=courses,
                           subjects=subjects,
                           selected_course=selected_course)


# ---------------------- RECOMMENDED RESOURCES ----------------------
@app.route("/user/recommendations", methods=["GET", "POST"])
def user_recommendations():
    if "user_id" not in session:
        return redirect("/user/login")

    # Get course and subject from session or form
    if request.method == "POST":
        course_id = request.form.get("course_id")
        subject_id = request.form.get("subject_id")
        # Store in session for future use
        session["course_id"] = course_id
        session["subject_id"] = subject_id
    else:
        # GET request - get from session
        course_id = session.get("course_id")
        subject_id = session.get("subject_id")

    if not (course_id and subject_id):
        flash("Please select both course and subject.")
        return redirect("/user/courses")

    learning_style = session.get("learning_style")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Get resources matching course, subject, and optionally filter by learning style
    if learning_style and learning_style != "mixed":
        c.execute("""
            SELECT title, file_type, file_path
            FROM resources
            WHERE course_id=? AND subject_id=? AND file_type=?
        """, (course_id, subject_id, learning_style))
    else:
        c.execute("""
            SELECT title, file_type, file_path
            FROM resources
            WHERE course_id=? AND subject_id=?
        """, (course_id, subject_id))

    resources = c.fetchall()
    conn.close()

    return render_template("user_recommendations.html", resources=resources)


# ---------------------- QUIZ ----------------------
# ---------------------- QUIZ ----------------------
@app.route("/user/quiz", methods=["GET", "POST"])
def user_quiz():
    if "user_id" not in session:
        return redirect("/user/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Load all courses
    c.execute("SELECT id, name FROM courses")
    courses = c.fetchall()

    quiz = []
    subjects = []
    selected_course = None
    selected_subject = None

    if request.method == "POST":
        selected_course = request.form.get("course_id")
        selected_subject = request.form.get("subject_id")

        # If course is selected, load its subjects
        if selected_course:
            c.execute("SELECT id, name FROM subjects WHERE course_id=?", (selected_course,))
            subjects = c.fetchall()

        # If both course and subject are selected, load quiz questions
        # Dynamically pick difficulty based on learner's last cognitive state & score
        if selected_course and selected_subject:
            user_id = session.get("user_id")
            last_state, last_engagement, last_score = None, None, None
            if user_id:
                c.execute("""SELECT cognitive_state, engagement_level, score
                             FROM quiz_history WHERE user_id=?
                             ORDER BY id DESC LIMIT 1""", (user_id,))
                row = c.fetchone()
                if row:
                    last_state, last_engagement, last_score = row[0], row[1], row[2]

            target_difficulty = decide_target_difficulty(last_state, last_engagement, last_score)
            session['target_difficulty'] = target_difficulty
            # Logging disabled to avoid Windows handle errors
            # print(f"[ADAPTIVE] Quiz difficulty set to '{target_difficulty}' "
            #       f"(state={last_state}, engagement={last_engagement}, score={last_score})")

            # Try to load questions matching the target difficulty; fall back to any
            c.execute("""
                SELECT * FROM quizzes
                WHERE course_id=? AND subject_id=? AND COALESCE(difficulty,'medium')=?
            """, (selected_course, selected_subject, target_difficulty))
            quiz = c.fetchall()
            if not quiz:
                c.execute("""
                    SELECT * FROM quizzes
                    WHERE course_id=? AND subject_id=?
                """, (selected_course, selected_subject))
                quiz = c.fetchall()

    conn.close()
    
    return render_template("user_quiz.html",
                           courses=courses,
                           subjects=subjects,
                           quiz=quiz,
                           selected_course=selected_course,
                           selected_subject=selected_subject)


# ---------------------- COGNITIVE DATA ANALYSIS ----------------------
def analyze_cognitive_data(cognitive_data):
    """Analyze the cognitive states captured during quiz"""
    if not cognitive_data:
        return {
            'dominant_state': 'unknown',
            'avg_confidence': 0,
            'total_captures': 0,
            'state_counts': {},
            'engagement_level': 'No data',
            'recommendation': 'Camera was not available during the quiz.'
        }

    # Count each state
    state_counts = {}
    total_confidence = 0
    for entry in cognitive_data:
        emotion = entry.get('emotion', 'neutral')
        confidence = entry.get('confidence', 50)
        state_counts[emotion] = state_counts.get(emotion, 0) + 1
        total_confidence += confidence

    total_captures = len(cognitive_data)
    avg_confidence = int(total_confidence / total_captures) if total_captures else 0

    # Find dominant state
    dominant_state = max(state_counts, key=state_counts.get) if state_counts else 'neutral'

    # Determine engagement level
    positive_states = state_counts.get('focused', 0) + state_counts.get('engaged', 0) + state_counts.get('happy', 0)
    negative_states = state_counts.get('confused', 0) + state_counts.get('tired', 0) + state_counts.get('stressed', 0)
    positive_ratio = positive_states / total_captures if total_captures else 0

    if positive_ratio >= 0.7:
        engagement_level = 'Highly Engaged'
        recommendation = 'You were highly focused during the quiz. Keep up the great work!'
    elif positive_ratio >= 0.4:
        engagement_level = 'Moderately Engaged'
        recommendation = 'You showed mixed engagement. Try taking short breaks between study sessions.'
    else:
        engagement_level = 'Low Engagement'
        recommendation = 'You seemed to struggle during the quiz. Consider reviewing the material and trying again when you feel more rested.'

    return {
        'dominant_state': dominant_state,
        'avg_confidence': avg_confidence,
        'total_captures': total_captures,
        'state_counts': state_counts,
        'engagement_level': engagement_level,
        'recommendation': recommendation
    }


# ---------------------- SUBMIT QUIZ ----------------------
@app.route("/user/quiz/submit", methods=["POST"])
def submit_quiz():
    if "user_id" not in session:
        return redirect("/user/login")

    user_id = session["user_id"]
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    total = 0
    correct = 0
    quiz_course_id = None
    quiz_subject_id = None

    # Calculate score
    for key, answer in request.form.items():
        if key.startswith("q"):
            qid = int(key[1:])
            c.execute("SELECT correct_option, course_id, subject_id FROM quizzes WHERE id=?", (qid,))
            result = c.fetchone()
            if result:
                correct_option = result[0]
                if quiz_course_id is None:
                    quiz_course_id = result[1]
                    quiz_subject_id = result[2]
                total += 1
                if answer == correct_option:
                    correct += 1

    # Calculate percentage
    score = int((correct / total) * 100) if total else 0

    # Process cognitive data from camera monitoring
    cognitive_data_raw = request.form.get('cognitive_data', '[]')
    try:
        cognitive_data = json.loads(cognitive_data_raw) if cognitive_data_raw else []
    except:
        cognitive_data = []

    # Analyze cognitive states
    cognitive_summary = analyze_cognitive_data(cognitive_data)

    # Save quiz history to database - use course/subject from the quiz itself
    course_id = quiz_course_id or session.get('course_id')
    subject_id = quiz_subject_id or session.get('subject_id')
    c.execute("""INSERT INTO quiz_history(user_id, course_id, subject_id, score, correct, total,
                 cognitive_state, engagement_level)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
              (user_id, course_id, subject_id, score, correct, total,
               cognitive_summary.get('dominant_state', 'unknown'),
               cognitive_summary.get('engagement_level', 'No data')))
    conn.commit()

    # Store results in session to display on results page
    session['quiz_results'] = {
        'score': score,
        'correct': correct,
        'total': total,
        'cognitive_summary': cognitive_summary,
        'cognitive_history': cognitive_data
    }

    conn.close()
    return redirect("/user/quiz/results")


# ---------------------- QUIZ RESULTS PAGE ----------------------
@app.route("/user/quiz/results")
def quiz_results():
    if "user_id" not in session:
        return redirect("/user/login")
    
    # Get quiz results from session
    results = session.get('quiz_results', {})
    score = results.get('score', 0)
    correct = results.get('correct', 0)
    total = results.get('total', 0)
    cognitive_summary = results.get('cognitive_summary', {})
    cognitive_history = results.get('cognitive_history', [])

    # Clear results from session after displaying
    session.pop('quiz_results', None)

    return render_template("user_quiz_results.html",
                         score=score,
                         correct=correct,
                         total=total,
                         cognitive_summary=cognitive_summary,
                         cognitive_history=cognitive_history)


import base64
import random
from datetime import datetime

# ---------------------- ADAPTIVE LEARNING ----------------------
@app.route("/user/adaptive_learning")
def adaptive_learning():
    if "user_id" not in session:
        return redirect("/user/login")

    user_id = session["user_id"]

    # Get last quiz score from database (not session, which gets cleared)
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT score, correct, total FROM quiz_history WHERE user_id=? ORDER BY id DESC LIMIT 1", (user_id,))
    row = c.fetchone()
    conn.close()

    if row:
        score, correct, total = row
    else:
        score, correct, total = 0, 0, 0

    return render_template("user_adaptive_learning.html",
                         score=score,
                         correct=correct,
                         total=total)

@app.route("/user/capture_face", methods=["POST"])
def capture_face():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    try:
        image_data = request.json.get('image')
        if not image_data:
            return jsonify({"error": "No image data"}), 400

        # ---------------- REAL FER DETECTION (when packages available) ----------------
        if _fer_available:
            import cv2
            import numpy as np

            if ',' in image_data:
                image_data = image_data.split(',')[1]

            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return jsonify({"error": "Invalid image"}), 400

            try:
                global _fer_detector
                if _fer_detector is None:
                    from fer import FER
                    _fer_detector = FER(mtcnn=False)

                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                result_list = _fer_detector.detect_emotions(rgb_img)

                if result_list and len(result_list) > 0:
                    emotions_dict = result_list[0]['emotions']
                    detected_emotion = max(emotions_dict, key=emotions_dict.get)
                    confidence_score = int(emotions_dict[detected_emotion] * 100)
                    emotion_scores = {k: int(v * 100) for k, v in emotions_dict.items()}
                else:
                    return jsonify({
                        "success": False,
                        "error": "no_face",
                        "message": "No face detected. Please position your face in the camera."
                    }), 200
            except Exception as fer_err:
                return jsonify({
                    "success": False,
                    "error": "detection_failed",
                    "message": f"Face detection error: {str(fer_err)}"
                }), 200

            MIN_CONFIDENCE = 35
            if confidence_score < MIN_CONFIDENCE:
                return jsonify({
                    "success": False,
                    "error": "low_confidence",
                    "message": f"Low confidence ({confidence_score}%). Please ensure good lighting.",
                    "confidence_score": confidence_score
                }), 200

            emotion_to_cognitive = {
                'happy': 'engaged', 'neutral': 'focused', 'surprise': 'confused',
                'fear': 'stressed', 'angry': 'stressed', 'sad': 'tired', 'disgust': 'confused'
            }
            cognitive_state = emotion_to_cognitive.get(detected_emotion, 'focused')

            session['face_analysis'] = {
                'dominant_emotion': cognitive_state,
                'raw_emotion': detected_emotion,
                'confidence_score': confidence_score,
                'timestamp': datetime.now().isoformat()
            }

            return jsonify({
                "success": True,
                "dominant_emotion": cognitive_state,
                "raw_emotion": detected_emotion,
                "confidence_score": confidence_score,
                "message": f"{cognitive_state.capitalize()} detected ({confidence_score}% confidence)",
                "all_emotions": emotion_scores
            })

        # ---------------- FER NOT AVAILABLE (free tier warning) ----------------
        else:
            return jsonify({
                "success": False,
                "error": "fer_unavailable",
                "message": "FER module not available - free tier does not support TensorFlow. Please run locally for real emotion detection."
            }), 200

    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

# ---------------------- GET PERSONALIZED RECOMMENDATIONS ----------------------
@app.route("/user/get_recommendations")
def get_recommendations():
    if "user_id" not in session:
        return redirect("/user/login")
    
    user_id = session["user_id"]
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # --- 1. Get predicted cognitive state from face analysis ---
    face_data = session.get('face_analysis', {})
    confidence_score = face_data.get('confidence_score', 50)
    dominant_emotion = face_data.get('dominant_emotion', 'neutral')

    # --- 2. Get latest quiz performance from database ---
    c.execute("SELECT score, cognitive_state, engagement_level FROM quiz_history WHERE user_id=? ORDER BY id DESC LIMIT 1", (user_id,))
    last_quiz = c.fetchone()
    quiz_score = last_quiz[0] if last_quiz else 0
    cognitive_state = last_quiz[1] if last_quiz and last_quiz[1] else dominant_emotion
    engagement_level = last_quiz[2] if last_quiz and last_quiz[2] else None

    # --- 3. Dynamically decide target difficulty based on cognitive state ---
    target_difficulty = decide_target_difficulty(
        cognitive_state=cognitive_state,
        engagement_level=engagement_level,
        last_score=quiz_score
    )

    # --- 4. Learning state label & message ---
    if target_difficulty == "easy":
        learning_state = "struggling"
        message = ("We noticed you might need extra support. Here are easier "
                   "resources to help you build a stronger foundation:")
    elif target_difficulty == "medium":
        learning_state = "moderate"
        message = ("You're making good progress! Here are medium-level resources "
                   "to strengthen your understanding:")
    else:
        learning_state = "confident"
        message = ("Great job! Here are advanced resources to challenge you further:")

    # --- 5. Detect preferred learning format from past user activity ---
    c.execute("""
        SELECT r.file_type, COUNT(*) as cnt
        FROM user_activity ua
        JOIN resources r ON ua.resource_id = r.id
        WHERE ua.user_id=?
        GROUP BY r.file_type
        ORDER BY cnt DESC
        LIMIT 1
    """, (user_id,))
    pref_row = c.fetchone()
    preferred_format = pref_row[0].lower() if pref_row and pref_row[0] else None

    def format_bucket(file_type):
        ft = (file_type or "").lower()
        if ft in ("mp4", "mov", "avi", "mkv", "webm", "video", "audio", "mp3", "wav"):
            return "video"  # Group audio + video together as media
        if ft in ("pdf", "doc", "docx", "txt", "ppt", "pptx", "notes", "text"):
            return "notes"
        if ft in ("quiz",):
            return "quiz"
        return "other"

    preferred_bucket = format_bucket(preferred_format) if preferred_format else None

    # --- 6. Behaviour of similar learners: find learners with similar cognitive state ---
    c.execute("""
        SELECT DISTINCT user_id FROM quiz_history
        WHERE cognitive_state=? AND user_id<>?
        LIMIT 20
    """, (cognitive_state, user_id))
    similar_users = [row[0] for row in c.fetchall()]

    similar_resource_ids = []
    if similar_users:
        placeholders = ",".join("?" * len(similar_users))
        c.execute(f"""
            SELECT resource_id, COUNT(*) as freq
            FROM user_activity
            WHERE user_id IN ({placeholders}) AND resource_id IS NOT NULL
            GROUP BY resource_id
            ORDER BY freq DESC
            LIMIT 10
        """, similar_users)
        similar_resource_ids = [row[0] for row in c.fetchall()]

    # --- 7. Get course and subject from session ---
    course_id = session.get('course_id')
    subject_id = session.get('subject_id')

    recommendations = []

    if course_id and subject_id:
        # Resources at the target difficulty for this course/subject
        c.execute("""
            SELECT id, title, file_type, file_path, COALESCE(difficulty,'medium')
            FROM resources
            WHERE course_id=? AND subject_id=?
              AND COALESCE(difficulty,'medium')=?
        """, (course_id, subject_id, target_difficulty))
        filtered = c.fetchall()

        # Fallback: any difficulty for this course/subject
        if not filtered:
            c.execute("""
                SELECT id, title, file_type, file_path, COALESCE(difficulty,'medium')
                FROM resources
                WHERE course_id=? AND subject_id=?
            """, (course_id, subject_id))
            filtered = c.fetchall()

        # STRICT FORMAT FILTERING - Show ONLY user's preferred format
        # Determine how many resources we need
        if learning_state == "struggling":
            target_count = 4
        elif learning_state == "moderate":
            target_count = 3
        else:
            target_count = 2

        # STRICT FILTER: If user has a preferred format, show ONLY that format
        if preferred_bucket:
            # Filter to ONLY preferred format (video/notes/quiz)
            format_filtered = [r for r in filtered if format_bucket(r[2]) == preferred_bucket]

            # Within preferred format, rank by similar-learner usage
            def rank_by_similarity(r):
                return 0 if r[0] in similar_resource_ids else 1

            format_filtered.sort(key=rank_by_similarity)
            recommendations = format_filtered[:target_count]
        else:
            # No preference detected yet (new user) - use all formats with ranking
            def rank_key(r):
                in_sim = 0 if r[0] in similar_resource_ids else 1
                return in_sim

            filtered.sort(key=rank_key)
            recommendations = filtered[:target_count]
    else:
        # No course/subject chosen — use similar-learner + preferred-format driven picks
        c.execute("""
            SELECT r.id, r.title, r.file_type, r.file_path, c.name, s.name,
                   COALESCE(r.difficulty,'medium')
            FROM resources r
            JOIN courses c ON r.course_id = c.id
            JOIN subjects s ON r.subject_id = s.id
            ORDER BY RANDOM()
            LIMIT 20
        """)
        pool = c.fetchall()

        # STRICT FILTER by preferred format
        if preferred_bucket:
            # Only show user's preferred format
            pool = [r for r in pool if format_bucket(r[2]) == preferred_bucket]

        # Rank by difficulty match → similar learner usage
        def rank_key2(r):
            diff_match = 0 if r[6] == target_difficulty else 1
            in_sim = 0 if r[0] in similar_resource_ids else 1
            return (diff_match, in_sim)

        pool.sort(key=rank_key2)
        recommendations = pool[:4]

    conn.close()
    
    return jsonify({
        "recommendations": [
            {
                "id": rec[0],
                "title": rec[1],
                "type": rec[2],
                "file_path": rec[3],
                "course": rec[4] if len(rec) > 4 else "",
                "subject": rec[5] if len(rec) > 5 else ""
            } for rec in recommendations
        ],
        "learning_state": learning_state,
        "target_difficulty": target_difficulty,
        "cognitive_state": cognitive_state,
        "engagement_level": engagement_level,
        "preferred_format": preferred_bucket,
        "similar_learners_count": len(similar_users),
        "confidence_score": confidence_score,
        "quiz_score": quiz_score,
        "dominant_emotion": dominant_emotion,
        "message": message
    })


# ---------------------- TRACK RESOURCE VIEW (for preferred format detection) ----------------------
@app.route("/user/track_resource_view", methods=["POST"])
def track_resource_view():
    """Log when a user clicks/views a resource (needed for preferred format detection)"""
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]
    resource_id = request.json.get('resource_id')

    if not resource_id:
        return jsonify({"error": "Missing resource_id"}), 400

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Get course/subject from resource
    c.execute("SELECT course_id, subject_id FROM resources WHERE id=?", (resource_id,))
    row = c.fetchone()
    if row:
        course_id, subject_id = row[0], row[1]
        c.execute("""INSERT INTO user_activity(user_id, course_id, subject_id, resource_id)
                     VALUES (?, ?, ?, ?)""",
                  (user_id, course_id, subject_id, resource_id))
        conn.commit()

    conn.close()
    return jsonify({"success": True})


# ---------------------- GET PERSONALIZED RECOMMENDATIONS ----------------------
# @app.route("/user/get_recommendations")
# def get_recommendations():
#     if "user_id" not in session:
#         return redirect("/user/login")
    
#     user_id = session["user_id"]
#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()
    
#     # Get emotion data
#     emotion_data = session.get('emotion_analysis', {})
#     confidence_score = emotion_data.get('confidence_score', 50)
#     dominant_emotion = emotion_data.get('dominant_emotion', 'neutral')
    
#     # Get quiz performance
#     quiz_results = session.get('quiz_results', {})
#     quiz_score = quiz_results.get('score', 0)
    
#     # Determine learning state
#     if confidence_score < 40 or quiz_score < 60:
#         learning_state = "struggling"
#     elif confidence_score < 70 or quiz_score < 80:
#         learning_state = "moderate"
#     else:
#         learning_state = "confident"
    
#     # Get course and subject from session
#     course_id = session.get('course_id')
#     subject_id = session.get('subject_id')
    
#     recommendations = []
    
#     if course_id and subject_id:
#         # Get all resources for the course and subject
#         c.execute("""
#             SELECT id, title, file_type, file_path 
#             FROM resources 
#             WHERE course_id=? AND subject_id=?
#         """, (course_id, subject_id))
#         all_resources = c.fetchall()
        
#         if all_resources:
#             # Shuffle resources for variety
#             import random
#             random.shuffle(all_resources)
            
#             # Select resources based on learning state
#             if learning_state == "struggling":
#                 # More resources for struggling students
#                 recommendations = all_resources[:4]
#                 message = "We noticed you might need extra support. Here are some resources to help you understand better:"
#             elif learning_state == "moderate":
#                 recommendations = all_resources[:3]
#                 message = "You're making good progress! Here are some resources to strengthen your understanding:"
#             else:
#                 recommendations = all_resources[:2]
#                 message = "Great job! You're doing well. Here are some resources to challenge you further:"
#     else:
#         # If no specific course/subject, get random resources
#         c.execute("""
#             SELECT r.id, r.title, r.file_type, r.file_path, c.name, s.name
#             FROM resources r
#             JOIN courses c ON r.course_id = c.id
#             JOIN subjects s ON r.subject_id = s.id
#             ORDER BY RANDOM()
#             LIMIT 3
#         """)
#         recommendations = c.fetchall()
#         message = "Based on your current state, here are some learning resources:"
    
#     conn.close()
    
#     return jsonify({
#         "recommendations": [
#             {
#                 "id": rec[0],
#                 "title": rec[1],
#                 "type": rec[2],
#                 "file_path": rec[3],
#                 "course": rec[4] if len(rec) > 4 else "",
#                 "subject": rec[5] if len(rec) > 5 else ""
#             } for rec in recommendations
#         ],
#         "learning_state": learning_state,
#         "confidence_score": confidence_score,
#         "quiz_score": quiz_score,
#         "dominant_emotion": dominant_emotion,
#         "message": message
#     })

# ---------------------- PERFORMANCE DASHBOARD ----------------------
@app.route("/user/performance")
def user_performance():
    if "user_id" not in session:
        return redirect("/user/login")

    user_id = session["user_id"]
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Get all quiz history for charts
    c.execute("""
        SELECT qh.score, qh.correct, qh.total, qh.cognitive_state,
               qh.engagement_level, qh.timestamp,
               COALESCE(c.name, 'Unknown') as course_name,
               COALESCE(s.name, 'Unknown') as subject_name
        FROM quiz_history qh
        LEFT JOIN courses c ON qh.course_id = c.id
        LEFT JOIN subjects s ON qh.subject_id = s.id
        WHERE qh.user_id=?
        ORDER BY qh.timestamp ASC
    """, (user_id,))
    history = c.fetchall()

    # Calculate stats
    total_quizzes = len(history)
    avg_score = int(sum(h[0] for h in history) / total_quizzes) if total_quizzes else 0
    best_score = max(h[0] for h in history) if total_quizzes else 0
    total_correct = sum(h[1] for h in history)
    total_questions = sum(h[2] for h in history)

    # Scores over time for line chart
    scores_data = [{"score": h[0], "date": h[5][:10], "course": h[6]} for h in history]

    # Scores by course for bar chart
    course_scores = {}
    for h in history:
        course = h[6]
        if course not in course_scores:
            course_scores[course] = []
        course_scores[course].append(h[0])
    course_avg = {k: int(sum(v)/len(v)) for k, v in course_scores.items()}

    # Cognitive state distribution for pie chart
    state_counts = {}
    for h in history:
        state = h[3] or 'unknown'
        state_counts[state] = state_counts.get(state, 0) + 1

    conn.close()

    return render_template("user_performance.html",
                         user_name=session.get("user_name"),
                         total_quizzes=total_quizzes,
                         avg_score=avg_score,
                         best_score=best_score,
                         total_correct=total_correct,
                         total_questions=total_questions,
                         scores_data=json.dumps(scores_data),
                         course_avg=json.dumps(course_avg),
                         state_counts=json.dumps(state_counts))


# ---------------------- QUIZ HISTORY ----------------------
@app.route("/user/quiz_history")
def quiz_history_page():
    if "user_id" not in session:
        return redirect("/user/login")

    user_id = session["user_id"]
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        SELECT qh.id, qh.score, qh.correct, qh.total, qh.cognitive_state,
               qh.engagement_level, qh.timestamp,
               COALESCE(c.name, 'Unknown') as course_name,
               COALESCE(s.name, 'Unknown') as subject_name
        FROM quiz_history qh
        LEFT JOIN courses c ON qh.course_id = c.id
        LEFT JOIN subjects s ON qh.subject_id = s.id
        WHERE qh.user_id=?
        ORDER BY qh.timestamp DESC
    """, (user_id,))
    history = c.fetchall()
    conn.close()

    return render_template("user_quiz_history.html",
                         user_name=session.get("user_name"),
                         history=history)


# ---------------------- LEADERBOARD ----------------------
@app.route("/user/leaderboard")
def leaderboard():
    if "user_id" not in session:
        return redirect("/user/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Get top performers by average score (min 1 quiz)
    c.execute("""
        SELECT u.id, u.name,
               COUNT(qh.id) as quiz_count,
               ROUND(AVG(qh.score), 0) as avg_score,
               MAX(qh.score) as best_score,
               SUM(qh.correct) as total_correct
        FROM users u
        JOIN quiz_history qh ON u.id = qh.user_id
        GROUP BY u.id
        HAVING quiz_count >= 1
        ORDER BY avg_score DESC, best_score DESC
        LIMIT 50
    """)
    rankings = c.fetchall()
    conn.close()

    current_user_id = session.get("user_id")

    return render_template("user_leaderboard.html",
                         user_name=session.get("user_name"),
                         rankings=rankings,
                         current_user_id=current_user_id)


# ---------------------- CERTIFICATE GENERATION ----------------------
@app.route("/user/certificate/<int:history_id>")
def generate_certificate(history_id):
    if "user_id" not in session:
        return redirect("/user/login")

    user_id = session["user_id"]
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        SELECT qh.score, qh.correct, qh.total, qh.timestamp,
               COALESCE(c.name, 'Unknown') as course_name,
               COALESCE(s.name, 'Unknown') as subject_name
        FROM quiz_history qh
        LEFT JOIN courses c ON qh.course_id = c.id
        LEFT JOIN subjects s ON qh.subject_id = s.id
        WHERE qh.id=? AND qh.user_id=?
    """, (history_id, user_id))
    record = c.fetchone()
    conn.close()

    if not record:
        flash("Certificate not found.")
        return redirect("/user/quiz_history")

    if record[0] < 60:
        flash("Certificate is only available for scores 60% and above.")
        return redirect("/user/quiz_history")

    return render_template("user_certificate.html",
                         user_name=session.get("user_name"),
                         score=record[0],
                         correct=record[1],
                         total=record[2],
                         date=record[3][:10],
                         course=record[4],
                         subject=record[5])


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)
