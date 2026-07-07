"""
Seed script to add sample Notes, Videos, and Audio resources for all courses/subjects.
Run: python seed_resources.py
"""
import sqlite3
import os

UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- SAMPLE CONTENT LIBRARY ----------------
# Maps course/subject keyword -> content (notes text, video url, audio url)
CONTENT_LIBRARY = {
    "python": {
        "notes": """PYTHON PROGRAMMING - COMPLETE NOTES

1. INTRODUCTION TO PYTHON
Python is a high-level, interpreted programming language known for its simplicity and readability.
Created by Guido van Rossum in 1991, Python supports multiple programming paradigms.

2. KEY FEATURES
- Easy to learn and read
- Interpreted language (no compilation needed)
- Dynamically typed
- Object-oriented
- Large standard library
- Cross-platform

3. BASIC SYNTAX
# Variables
name = "Student"
age = 20
price = 99.99

# Print output
print("Hello, World!")
print(f"Name: {name}, Age: {age}")

# Conditional statements
if age >= 18:
    print("Adult")
else:
    print("Minor")

4. DATA TYPES
- int: Integer numbers (10, -5, 100)
- float: Decimal numbers (3.14, -0.5)
- str: Text ("Hello")
- bool: True/False
- list: Ordered collection [1, 2, 3]
- dict: Key-value pairs {"name": "John"}
- tuple: Immutable list (1, 2, 3)
- set: Unique values {1, 2, 3}

5. LOOPS
# For loop
for i in range(5):
    print(i)

# While loop
count = 0
while count < 5:
    print(count)
    count += 1

6. FUNCTIONS
def greet(name):
    return f"Hello, {name}!"

result = greet("Alice")
print(result)

7. OBJECT-ORIENTED PROGRAMMING
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        return f"I am {self.name}, {self.age} years old"

8. FILE HANDLING
# Read file
with open("file.txt", "r") as f:
    content = f.read()

# Write file
with open("output.txt", "w") as f:
    f.write("Hello")

9. POPULAR LIBRARIES
- NumPy: Numerical computing
- Pandas: Data analysis
- Matplotlib: Data visualization
- Scikit-learn: Machine learning
- TensorFlow/PyTorch: Deep learning
- Flask/Django: Web development

10. BEST PRACTICES
- Use meaningful variable names
- Write comments for complex logic
- Follow PEP 8 style guide
- Use virtual environments
- Write unit tests
- Handle exceptions properly
""",
        "video_url": "https://www.youtube.com/embed/kqtD5dpn9C8",
        "audio_url": "https://www.youtube.com/embed/rfscVS0vtbw"
    },
    "java": {
        "notes": """JAVA PROGRAMMING - COMPLETE NOTES

1. INTRODUCTION TO JAVA
Java is a popular, object-oriented programming language developed by Sun Microsystems in 1995.
Write Once, Run Anywhere (WORA) - Java runs on any device with JVM.

2. KEY FEATURES
- Platform independent (JVM)
- Object-oriented
- Strongly typed
- Automatic memory management (Garbage Collection)
- Multi-threaded
- Secure and robust

3. BASIC SYNTAX
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}

4. DATA TYPES
Primitive:
- int, long, short, byte (integers)
- float, double (decimals)
- char (single character)
- boolean (true/false)

Reference:
- String, Arrays, Objects

5. VARIABLES AND OPERATORS
int age = 20;
String name = "Student";
double price = 99.99;

// Operators: +, -, *, /, %, ==, !=, &&, ||

6. CONTROL STATEMENTS
// If-else
if (age >= 18) {
    System.out.println("Adult");
} else {
    System.out.println("Minor");
}

// For loop
for (int i = 0; i < 5; i++) {
    System.out.println(i);
}

// While loop
int count = 0;
while (count < 5) {
    count++;
}

7. OBJECT-ORIENTED CONCEPTS
- Class and Object
- Inheritance (extends)
- Polymorphism (method overriding)
- Encapsulation (private fields, getters/setters)
- Abstraction (abstract classes, interfaces)

class Student {
    private String name;

    public Student(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }
}

8. COLLECTIONS FRAMEWORK
- ArrayList: Dynamic array
- LinkedList: Doubly linked list
- HashMap: Key-value pairs
- HashSet: Unique elements
- TreeMap: Sorted key-value

9. EXCEPTION HANDLING
try {
    int result = 10 / 0;
} catch (ArithmeticException e) {
    System.out.println("Error: " + e.getMessage());
} finally {
    System.out.println("Always executes");
}

10. POPULAR FRAMEWORKS
- Spring Boot: Web applications
- Hibernate: Database ORM
- JUnit: Testing
- Maven/Gradle: Build tools
- Android SDK: Mobile apps
""",
        "video_url": "https://www.youtube.com/embed/eIrMbAQSU34",
        "audio_url": "https://www.youtube.com/embed/grEKMHGYyns"
    },
    "powerbi": {
        "notes": """POWER BI - COMPLETE NOTES

1. INTRODUCTION TO POWER BI
Power BI is Microsoft's business analytics service that provides interactive visualizations
and business intelligence capabilities with a simple interface.

2. KEY COMPONENTS
- Power BI Desktop: Windows app for creating reports
- Power BI Service: Cloud-based service for sharing
- Power BI Mobile: Mobile apps for viewing reports
- Power BI Gateway: Connects on-premise data
- Power BI Report Server: On-premise report hosting

3. DATA SOURCES
Power BI can connect to:
- Excel files
- SQL Server, MySQL, PostgreSQL
- CSV, JSON, XML files
- Web APIs
- Azure services
- Google Analytics
- Salesforce

4. POWER QUERY EDITOR
Used for data transformation:
- Remove duplicates
- Filter rows
- Split columns
- Merge queries
- Append queries
- Pivot/Unpivot
- Create custom columns

5. DATA MODELING
- Create relationships between tables
- One-to-many, many-to-many relationships
- Star schema and snowflake schema
- Calculated columns and measures

6. DAX (Data Analysis Expressions)
Basic DAX functions:
- SUM(), AVERAGE(), COUNT()
- CALCULATE() - Modify filter context
- FILTER() - Filter a table
- RELATED() - Get related column
- YEAR(), MONTH(), DAY() - Date functions
- IF(), SWITCH() - Conditional logic

Example:
Total Sales = SUM(Sales[Amount])
YTD Sales = TOTALYTD([Total Sales], Calendar[Date])

7. VISUALIZATIONS
Common chart types:
- Bar and Column charts
- Line charts
- Pie and Donut charts
- Scatter plots
- Maps (geographic data)
- Tables and Matrix
- Cards (KPIs)
- Gauges
- Tree maps
- Waterfall charts

8. FILTERS AND SLICERS
- Page filters
- Report filters
- Visual filters
- Slicers for interactive filtering
- Drill-through filters
- Cross-filtering between visuals

9. DASHBOARDS VS REPORTS
Reports:
- Multiple pages
- Rich interactivity
- Created in Desktop

Dashboards:
- Single page overview
- Pinned tiles from reports
- Real-time updates
- Available only in Service

10. SHARING AND COLLABORATION
- Publish to Power BI Service
- Share with workspaces
- Create apps for distribution
- Embed in websites/SharePoint
- Email subscriptions
- Row-level security (RLS)
""",
        "video_url": "https://www.youtube.com/embed/AGrl-H87pRU",
        "audio_url": "https://www.youtube.com/embed/TmhQCQr_DCA"
    },
    "matplotlib": {
        "notes": """MATPLOTLIB - DATA VISUALIZATION NOTES

1. INTRODUCTION
Matplotlib is the most popular Python library for creating static, animated,
and interactive visualizations.

2. INSTALLATION
pip install matplotlib

3. BASIC IMPORT
import matplotlib.pyplot as plt
import numpy as np

4. LINE PLOT
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]
plt.plot(x, y)
plt.xlabel('X axis')
plt.ylabel('Y axis')
plt.title('Line Plot')
plt.show()

5. BAR CHART
categories = ['A', 'B', 'C', 'D']
values = [25, 40, 30, 55]
plt.bar(categories, values)
plt.title('Bar Chart')
plt.show()

6. SCATTER PLOT
x = np.random.rand(50)
y = np.random.rand(50)
plt.scatter(x, y, color='red')
plt.title('Scatter Plot')
plt.show()

7. HISTOGRAM
data = np.random.randn(1000)
plt.hist(data, bins=30)
plt.title('Histogram')
plt.show()

8. PIE CHART
sizes = [30, 25, 20, 25]
labels = ['A', 'B', 'C', 'D']
plt.pie(sizes, labels=labels, autopct='%1.1f%%')
plt.title('Pie Chart')
plt.show()

9. SUBPLOTS
fig, axes = plt.subplots(2, 2)
axes[0, 0].plot([1, 2, 3])
axes[0, 1].bar(['A', 'B'], [1, 2])
axes[1, 0].scatter([1, 2], [3, 4])
axes[1, 1].hist([1, 2, 2, 3])
plt.tight_layout()
plt.show()

10. CUSTOMIZATION
- Colors: 'red', 'blue', '#FF5733'
- Line styles: '-', '--', ':', '-.'
- Markers: 'o', 's', '^', '*'
- Legends: plt.legend()
- Grids: plt.grid(True)
- Save: plt.savefig('plot.png')
""",
        "video_url": "https://www.youtube.com/embed/3Xc3CA655Y4",
        "audio_url": "https://www.youtube.com/embed/wB9C0Mz9gSo"
    }
}

# Default content if subject doesn't match
DEFAULT_CONTENT = {
    "notes": """LEARNING NOTES

Welcome to this course module. These notes cover the fundamental concepts.

1. INTRODUCTION
This subject forms an important part of your curriculum.
Focus on understanding core concepts before moving to advanced topics.

2. KEY TOPICS
- Fundamentals and basics
- Core concepts and terminology
- Practical applications
- Real-world examples
- Best practices

3. STUDY TIPS
- Read regularly
- Take notes while learning
- Practice with examples
- Review concepts weekly
- Ask questions when stuck

4. RESOURCES FOR FURTHER LEARNING
- Official documentation
- Online tutorials
- Community forums
- Practice exercises
- Books and references

5. ASSESSMENT
You will be assessed through quizzes that test your understanding.
The system will also monitor your engagement and provide personalized recommendations.
""",
    "video_url": "https://www.youtube.com/embed/rfscVS0vtbw",
    "audio_url": "https://www.youtube.com/embed/rfscVS0vtbw"
}


def get_content(subject_name):
    """Find matching content for a subject."""
    key = subject_name.lower().replace(" ", "").replace("package", "").strip()
    for k, v in CONTENT_LIBRARY.items():
        if k in key or key in k:
            return v
    return DEFAULT_CONTENT


def seed():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Get all course-subject pairs
    c.execute("""
        SELECT s.id, s.course_id, s.name, co.name
        FROM subjects s
        JOIN courses co ON s.course_id = co.id
    """)
    subjects = c.fetchall()

    added = 0
    skipped = 0

    for subject_id, course_id, subject_name, course_name in subjects:
        print(f"\nProcessing: {course_name} -> {subject_name}")
        content = get_content(subject_name)

        # ---------------- NOTES (TEXT) ----------------
        notes_filename = f"notes_{course_id}_{subject_id}.txt"
        notes_path = os.path.join(UPLOAD_FOLDER, notes_filename)
        with open(notes_path, "w", encoding="utf-8") as f:
            f.write(content["notes"])

        c.execute("""SELECT id FROM resources WHERE course_id=? AND subject_id=? AND file_type='text'""",
                  (course_id, subject_id))
        if not c.fetchone():
            c.execute("""INSERT INTO resources (title, file_type, file_path, course_id, subject_id)
                         VALUES (?, ?, ?, ?, ?)""",
                      (f"{subject_name} - Study Notes", "text",
                       f"uploads/{notes_filename}", course_id, subject_id))
            print(f"  [+] Added Notes: {notes_filename}")
            added += 1
        else:
            print(f"  [~] Notes already exist, skipping")
            skipped += 1

        # ---------------- VIDEO ----------------
        c.execute("""SELECT id FROM resources WHERE course_id=? AND subject_id=? AND file_type='video'""",
                  (course_id, subject_id))
        if not c.fetchone():
            c.execute("""INSERT INTO resources (title, file_type, file_path, course_id, subject_id)
                         VALUES (?, ?, ?, ?, ?)""",
                      (f"{subject_name} - Video Tutorial", "video",
                       content["video_url"], course_id, subject_id))
            print(f"  [+] Added Video: {content['video_url']}")
            added += 1
        else:
            print(f"  [~] Video already exists, skipping")
            skipped += 1

        # ---------------- AUDIO ----------------
        c.execute("""SELECT id FROM resources WHERE course_id=? AND subject_id=? AND file_type='audio'""",
                  (course_id, subject_id))
        if not c.fetchone():
            c.execute("""INSERT INTO resources (title, file_type, file_path, course_id, subject_id)
                         VALUES (?, ?, ?, ?, ?)""",
                      (f"{subject_name} - Audio Lecture", "audio",
                       content["audio_url"], course_id, subject_id))
            print(f"  [+] Added Audio: {content['audio_url']}")
            added += 1
        else:
            print(f"  [~] Audio already exists, skipping")
            skipped += 1

    conn.commit()
    conn.close()

    print(f"\n{'='*50}")
    print(f"[DONE] Added {added} new resources, skipped {skipped} existing.")
    print(f"{'='*50}")


if __name__ == "__main__":
    seed()
