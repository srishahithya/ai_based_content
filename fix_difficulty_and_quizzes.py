"""
One-shot fixer:
1) Spreads difficulty across existing resources (easy/medium/hard mix)
2) Seeds additional quiz questions for each subject with mixed difficulties

Run once:  python fix_difficulty_and_quizzes.py
"""
import sqlite3

DB = "database.db"

# ---------- 1. Spread difficulty across resources ----------
def spread_resource_difficulty():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # Get all subject groupings
    c.execute("SELECT DISTINCT course_id, subject_id FROM resources")
    groups = c.fetchall()

    pattern = ["easy", "easy", "medium", "medium", "hard"]  # 2/2/1 for 5-item groups

    for course_id, subject_id in groups:
        c.execute(
            "SELECT id FROM resources WHERE course_id=? AND subject_id=? ORDER BY id",
            (course_id, subject_id),
        )
        ids = [row[0] for row in c.fetchall()]
        for idx, rid in enumerate(ids):
            diff = pattern[idx % len(pattern)]
            c.execute("UPDATE resources SET difficulty=? WHERE id=?", (diff, rid))
    conn.commit()
    conn.close()
    print("[OK] Resource difficulties spread.")


# ---------- 2. Seed quizzes per subject ----------
# Format: subject_name -> list of (question, o1, o2, o3, o4, correct, difficulty)
QUIZZES = {
    "Python": [
        ("Which keyword is used to define a function in Python?", "func", "def", "function", "define", "def", "easy"),
        ("What is the output of print(type([]))?", "<class 'list'>", "<class 'tuple'>", "<class 'dict'>", "<class 'set'>", "<class 'list'>", "easy"),
        ("Which method adds an element to the end of a list?", "push()", "add()", "append()", "insert()", "append()", "medium"),
        ("What does the 'self' parameter refer to in a class method?", "The class itself", "The instance of the class", "A static variable", "The parent class", "The instance of the class", "medium"),
        ("What is a lambda function in Python?", "A named function", "An anonymous function", "A recursive function", "A class method", "An anonymous function", "hard"),
        ("Which of these is NOT a valid Python data type?", "list", "tuple", "array", "dict", "array", "hard"),
    ],
    "NumPy": [
        ("Which function creates a NumPy array?", "np.array()", "np.list()", "np.make()", "np.new()", "np.array()", "easy"),
        ("What is the default data type of np.zeros()?", "int", "float", "bool", "str", "float", "easy"),
        ("Which attribute gives the shape of an array?", ".size", ".shape", ".dim", ".len", ".shape", "medium"),
        ("What does np.arange(0, 10, 2) return?", "[0,2,4,6,8]", "[0,1,2]", "[2,4,6,8,10]", "[0,10]", "[0,2,4,6,8]", "medium"),
        ("Which function performs matrix multiplication?", "np.mul()", "np.dot()", "np.times()", "np.prod()", "np.dot()", "hard"),
        ("What is broadcasting in NumPy?", "Auto-resize of arrays for operations", "Sending data over network", "Creating copies", "Removing dimensions", "Auto-resize of arrays for operations", "hard"),
    ],
    "Pandas": [
        ("Which data structure is 2-dimensional in Pandas?", "Series", "DataFrame", "Panel", "Array", "DataFrame", "easy"),
        ("How do you read a CSV file in Pandas?", "pd.read_csv()", "pd.load_csv()", "pd.open_csv()", "pd.csv()", "pd.read_csv()", "easy"),
        ("Which method drops missing values?", "fill()", "dropna()", "remove()", "clean()", "dropna()", "medium"),
        ("What does df.head() return?", "Last 5 rows", "First 5 rows", "Column names", "Shape", "First 5 rows", "medium"),
        ("Which method is used to group data?", "groupby()", "sortby()", "splitby()", "cluster()", "groupby()", "hard"),
        ("What does df.merge() do?", "Combines DataFrames on keys", "Deletes rows", "Sorts data", "Creates index", "Combines DataFrames on keys", "hard"),
    ],
    "Core Java": [
        ("Which keyword is used to declare a class?", "class", "Class", "new", "define", "class", "easy"),
        ("Which is the entry point of a Java program?", "start()", "main()", "run()", "init()", "main()", "easy"),
        ("Which type of loop is guaranteed to execute at least once?", "for loop", "while loop", "do-while loop", "foreach", "do-while loop", "medium"),
        ("What is the size of an int in Java?", "2 bytes", "4 bytes", "8 bytes", "Depends on system", "4 bytes", "medium"),
        ("Which keyword prevents inheritance?", "static", "final", "const", "sealed", "final", "hard"),
        ("What is JVM?", "Java Version Manager", "Java Virtual Machine", "Java Variable Method", "Java Verified Module", "Java Virtual Machine", "hard"),
    ],
    "OOP Concepts": [
        ("Which OOP concept hides internal details?", "Inheritance", "Polymorphism", "Encapsulation", "Abstraction", "Encapsulation", "easy"),
        ("Which OOP concept allows reusing code?", "Polymorphism", "Inheritance", "Encapsulation", "Overloading", "Inheritance", "easy"),
        ("Method overloading is an example of?", "Runtime polymorphism", "Compile-time polymorphism", "Inheritance", "Abstraction", "Compile-time polymorphism", "medium"),
        ("Which keyword is used to inherit a class in Java?", "implements", "extends", "inherits", "super", "extends", "medium"),
        ("What is an abstract class?", "A class with only static methods", "A class that cannot be instantiated", "A final class", "A private class", "A class that cannot be instantiated", "hard"),
        ("Can a class implement multiple interfaces in Java?", "No", "Yes", "Only 2", "Depends", "Yes", "hard"),
    ],
    "Introduction to PowerBI": [
        ("What is Power BI primarily used for?", "Coding", "Data visualization", "Gaming", "Word processing", "Data visualization", "easy"),
        ("Which company developed Power BI?", "Google", "Microsoft", "Oracle", "IBM", "Microsoft", "easy"),
        ("Which view is used to build reports?", "Report view", "Data view", "Model view", "Query view", "Report view", "medium"),
        ("What file format does Power BI Desktop save as?", ".pbix", ".pbi", ".pwr", ".bix", ".pbix", "medium"),
        ("What is Power Query used for?", "Visualization", "Data transformation", "Modeling", "Publishing", "Data transformation", "hard"),
        ("Which language is used in Power Query?", "DAX", "SQL", "M", "Python", "M", "hard"),
    ],
    "DAX and Visualizations": [
        ("DAX stands for?", "Data Analysis Expressions", "Digital Analytics Extension", "Data Access XML", "Dynamic Axis Engine", "Data Analysis Expressions", "easy"),
        ("Which chart shows parts of a whole?", "Line chart", "Pie chart", "Bar chart", "Scatter plot", "Pie chart", "easy"),
        ("Which function returns the current date in DAX?", "NOW()", "TODAY()", "DATE()", "CURRENT()", "TODAY()", "medium"),
        ("Which function sums a column in DAX?", "ADD()", "SUM()", "TOTAL()", "PLUS()", "SUM()", "medium"),
        ("What is CALCULATE used for in DAX?", "Modify filter context", "Create tables", "Sort data", "Render visuals", "Modify filter context", "hard"),
        ("What is a measure in Power BI?", "A static column", "A dynamic calculation", "A filter", "A visual", "A dynamic calculation", "hard"),
    ],
    "HTML & CSS": [
        ("What does HTML stand for?", "Hyper Text Markup Language", "High Text Machine Language", "Hyperlink Text Mark Language", "Home Tool Markup Language", "Hyper Text Markup Language", "easy"),
        ("Which tag is used for a line break?", "<break>", "<lb>", "<br>", "<newline>", "<br>", "easy"),
        ("Which CSS property changes text color?", "font-color", "text-color", "color", "foreground", "color", "medium"),
        ("Which HTML tag is semantic?", "<div>", "<span>", "<article>", "<b>", "<article>", "medium"),
        ("What does the CSS 'flex' property enable?", "Grid layout", "Flexible box layout", "Animation", "Transitions", "Flexible box layout", "hard"),
        ("What is the correct selector for ID 'main' in CSS?", ".main", "#main", "*main", "main", "#main", "hard"),
    ],
    "JavaScript": [
        ("Which keyword declares a constant?", "var", "let", "const", "static", "const", "easy"),
        ("What is the result of typeof null?", "null", "object", "undefined", "number", "object", "easy"),
        ("Which method adds an element to the end of an array?", "push()", "pop()", "shift()", "unshift()", "push()", "medium"),
        ("What is the DOM?", "Data Object Model", "Document Object Model", "Digital Ordered Map", "Display Object Mode", "Document Object Model", "medium"),
        ("What does 'this' refer to inside an arrow function?", "The function itself", "The global object", "The enclosing lexical scope", "undefined", "The enclosing lexical scope", "hard"),
        ("What is a closure in JavaScript?", "A loop", "A function with access to its outer scope", "A class", "An object method", "A function with access to its outer scope", "hard"),
    ],
    "Supervised Learning": [
        ("Supervised learning uses?", "Unlabeled data", "Labeled data", "No data", "Reward signals", "Labeled data", "easy"),
        ("Which is a classification algorithm?", "K-Means", "Linear Regression", "Decision Tree", "PCA", "Decision Tree", "easy"),
        ("Which metric is used for classification accuracy?", "MSE", "Accuracy", "RMSE", "R²", "Accuracy", "medium"),
        ("Which algorithm predicts continuous values?", "Logistic Regression", "Linear Regression", "KNN Classifier", "Naive Bayes", "Linear Regression", "medium"),
        ("What is overfitting?", "Model too simple", "Model fits noise in training data", "Low accuracy overall", "Fast training", "Model fits noise in training data", "hard"),
        ("Which technique helps prevent overfitting?", "Adding more features", "Regularization", "Removing data", "Increasing epochs", "Regularization", "hard"),
    ],
}


def seed_quizzes():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    inserted = 0
    skipped = 0
    for subject_name, questions in QUIZZES.items():
        c.execute("SELECT id, course_id FROM subjects WHERE name=?", (subject_name,))
        row = c.fetchone()
        if not row:
            print(f"[WARN] Subject not found: {subject_name}")
            continue
        subject_id, course_id = row[0], row[1]

        for q in questions:
            question, o1, o2, o3, o4, correct, difficulty = q
            # Avoid duplicates
            c.execute(
                "SELECT id FROM quizzes WHERE course_id=? AND subject_id=? AND question=?",
                (course_id, subject_id, question),
            )
            if c.fetchone():
                skipped += 1
                continue
            c.execute(
                """INSERT INTO quizzes
                   (course_id, subject_id, question, option1, option2, option3, option4, correct_option, difficulty)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (course_id, subject_id, question, o1, o2, o3, o4, correct, difficulty),
            )
            inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] Quizzes inserted: {inserted}, skipped (duplicates): {skipped}")


def summary():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    print()
    print("=== RESOURCES by difficulty ===")
    for row in c.execute("SELECT difficulty, COUNT(*) FROM resources GROUP BY difficulty"):
        print(" ", row)
    print()
    print("=== QUIZZES by difficulty ===")
    for row in c.execute("SELECT difficulty, COUNT(*) FROM quizzes GROUP BY difficulty"):
        print(" ", row)
    print()
    print("=== QUIZZES per subject ===")
    for row in c.execute(
        """SELECT s.name, COUNT(q.id)
           FROM subjects s LEFT JOIN quizzes q ON q.subject_id=s.id
           GROUP BY s.id ORDER BY s.id"""
    ):
        print(" ", row)
    conn.close()


if __name__ == "__main__":
    spread_resource_difficulty()
    seed_quizzes()
    summary()
