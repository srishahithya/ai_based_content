"""
Clean dummy data and seed the database with proper courses, subjects,
and resources covering all learning styles: text, video, audio, interactive, mixed.

Run: python clean_and_seed.py
"""
import sqlite3
import os

UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# STEP 1: CLEAN - remove dummy/duplicate data
# ============================================================
def clean_database():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    print("=" * 60)
    print("STEP 1: CLEANING DUMMY DATA")
    print("=" * 60)

    # Delete all existing resources (will be re-added with proper content)
    c.execute("DELETE FROM resources")
    print("[-] Removed all old resources")

    # Delete dummy subjects (Python1, J, and any single/short names)
    c.execute("DELETE FROM subjects WHERE name IN ('Python1', 'J')")
    print("[-] Removed dummy subjects: Python1, J")

    # Delete the duplicate 'Data Science' course (id=2 has no good subjects)
    c.execute("DELETE FROM subjects WHERE course_id=2")
    c.execute("DELETE FROM courses WHERE id=2")
    print("[-] Removed duplicate Data Science course (id=2)")

    conn.commit()
    conn.close()
    print("[OK] Database cleaned\n")


# ============================================================
# STEP 2: SEED - add proper courses, subjects, and resources
# ============================================================

# Comprehensive learning content
COURSES = [
    {
        "name": "Data Science",
        "subjects": [
            {
                "name": "Python",
                "notes_title": "Python Programming - Complete Guide",
                "notes": """PYTHON PROGRAMMING - COMPLETE NOTES

1. INTRODUCTION TO PYTHON
Python is a high-level, interpreted programming language known for its simplicity and readability.
Created by Guido van Rossum in 1991. Used for web development, data science, AI, automation.

2. KEY FEATURES
- Easy to learn and read syntax
- Interpreted (no compilation)
- Dynamically typed
- Object-oriented and functional
- Huge standard library
- Cross-platform compatible

3. BASIC SYNTAX
# Variables and printing
name = "Student"
age = 20
print(f"Hello, {name}! You are {age} years old")

# Conditional
if age >= 18:
    print("Adult")
else:
    print("Minor")

4. DATA TYPES
- int: 10, -5, 1000
- float: 3.14, -0.5
- str: "Hello"
- bool: True, False
- list: [1, 2, 3]
- tuple: (1, 2, 3)
- dict: {"key": "value"}
- set: {1, 2, 3}

5. LOOPS AND FUNCTIONS
# For loop
for i in range(5):
    print(i)

# Function definition
def add(a, b):
    return a + b

result = add(3, 5)  # result = 8

6. OBJECT-ORIENTED PROGRAMMING
class Student:
    def __init__(self, name):
        self.name = name
    def greet(self):
        return f"Hi, I'm {self.name}"

7. POPULAR LIBRARIES
- NumPy: Numerical computing
- Pandas: Data analysis
- Matplotlib: Visualization
- Scikit-learn: Machine learning
- TensorFlow: Deep learning

8. BEST PRACTICES
- Use meaningful variable names
- Follow PEP 8 style guide
- Write clean, readable code
- Use virtual environments
- Comment complex logic
""",
                "video": "https://www.youtube.com/embed/kqtD5dpn9C8",
                "audio": "https://www.youtube.com/embed/rfscVS0vtbw",
                "interactive": "https://www.programiz.com/python-programming/online-compiler/",
                "image": "https://www.python.org/static/community_logos/python-logo-master-v3-TM.png"
            },
            {
                "name": "NumPy",
                "notes_title": "NumPy - Numerical Computing in Python",
                "notes": """NUMPY - NUMERICAL COMPUTING NOTES

1. INTRODUCTION
NumPy (Numerical Python) is the fundamental package for scientific computing in Python.
Provides powerful N-dimensional array objects and tools for array operations.

2. INSTALLATION
pip install numpy

3. CREATING ARRAYS
import numpy as np

# From list
arr = np.array([1, 2, 3, 4, 5])

# Zeros and ones
zeros = np.zeros((3, 3))
ones = np.ones((2, 4))

# Range
arr = np.arange(0, 10, 2)  # [0, 2, 4, 6, 8]

# Random
rand = np.random.rand(3, 3)

4. ARRAY OPERATIONS
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# Element-wise
add = a + b       # [5, 7, 9]
mul = a * b       # [4, 10, 18]

# Statistical
mean = np.mean(a)
std = np.std(a)
sum_val = np.sum(a)

5. INDEXING AND SLICING
arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(arr[0, 1])    # 2
print(arr[:, 1])    # [2, 5, 8]
print(arr[1:, :2])  # [[4, 5], [7, 8]]

6. RESHAPING
arr = np.arange(12)
reshaped = arr.reshape(3, 4)

7. BROADCASTING
Enables operations between arrays of different shapes.

8. LINEAR ALGEBRA
# Matrix multiplication
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
C = np.dot(A, B)

# Inverse
inv = np.linalg.inv(A)

9. USE CASES
- Data preprocessing
- Image processing
- Scientific calculations
- Machine learning foundations
- Signal processing
""",
                "video": "https://www.youtube.com/embed/QUT1VHiLmmI",
                "audio": "https://www.youtube.com/embed/8JfDAm9y_7s",
                "interactive": "https://numpy.org/doc/stable/user/quickstart.html",
                "image": "https://numpy.org/images/logo.svg"
            },
            {
                "name": "Pandas",
                "notes_title": "Pandas - Data Analysis Library",
                "notes": """PANDAS - DATA ANALYSIS NOTES

1. INTRODUCTION
Pandas is a powerful data manipulation and analysis library for Python.
Built on top of NumPy, it provides DataFrame and Series structures.

2. INSTALLATION
pip install pandas

3. CORE DATA STRUCTURES
import pandas as pd

# Series (1D labeled array)
s = pd.Series([1, 2, 3, 4], index=['a', 'b', 'c', 'd'])

# DataFrame (2D table)
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['NY', 'LA', 'SF']
})

4. READING DATA
df = pd.read_csv('data.csv')
df = pd.read_excel('data.xlsx')
df = pd.read_json('data.json')

5. INSPECTING DATA
df.head()         # First 5 rows
df.tail()         # Last 5 rows
df.info()         # Data types and info
df.describe()     # Statistics
df.shape          # (rows, cols)
df.columns        # Column names

6. SELECTING DATA
df['Name']              # Single column
df[['Name', 'Age']]     # Multiple columns
df.iloc[0]              # By position
df.loc[0]               # By label
df[df['Age'] > 25]      # Filter

7. DATA CLEANING
df.dropna()                    # Remove missing
df.fillna(0)                   # Fill missing
df.drop_duplicates()           # Remove duplicates
df.rename(columns={'A': 'B'})  # Rename

8. GROUPING AND AGGREGATION
grouped = df.groupby('City').mean()
summary = df.groupby('City').agg({'Age': ['mean', 'max', 'min']})

9. MERGING AND JOINING
merged = pd.merge(df1, df2, on='key')
concat = pd.concat([df1, df2])

10. VISUALIZATION
df.plot(kind='bar')
df.plot(kind='line')
df.hist()
""",
                "video": "https://www.youtube.com/embed/vmEHCJofslg",
                "audio": "https://www.youtube.com/embed/zmdjNSmRXF4",
                "interactive": "https://pandas.pydata.org/docs/getting_started/intro_tutorials/",
                "image": "https://pandas.pydata.org/static/img/pandas.svg"
            }
        ]
    },
    {
        "name": "Java",
        "subjects": [
            {
                "name": "Core Java",
                "notes_title": "Core Java Programming",
                "notes": """CORE JAVA - COMPLETE NOTES

1. INTRODUCTION
Java is a popular, object-oriented programming language.
Developed by Sun Microsystems (now Oracle) in 1995.
Write Once, Run Anywhere (WORA) via JVM.

2. KEY FEATURES
- Platform independent
- Object-oriented
- Strongly typed
- Garbage collection
- Multi-threaded
- Secure and robust

3. HELLO WORLD PROGRAM
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}

4. DATA TYPES
Primitive:
- byte (8-bit), short (16-bit), int (32-bit), long (64-bit)
- float (32-bit), double (64-bit)
- char (16-bit Unicode)
- boolean (true/false)

Reference:
- String, Arrays, Classes, Interfaces

5. CONTROL STATEMENTS
// If-else
if (score >= 90) {
    grade = "A";
} else if (score >= 80) {
    grade = "B";
}

// For loop
for (int i = 0; i < 10; i++) {
    System.out.println(i);
}

// Switch
switch (day) {
    case 1: System.out.println("Monday"); break;
    case 2: System.out.println("Tuesday"); break;
    default: System.out.println("Other");
}

6. METHODS
public int add(int a, int b) {
    return a + b;
}

7. ARRAYS
int[] numbers = {1, 2, 3, 4, 5};
int[] arr = new int[10];

for (int num : numbers) {
    System.out.println(num);
}

8. STRING HANDLING
String s = "Hello Java";
s.length();
s.toUpperCase();
s.substring(0, 5);
s.replace("Java", "World");

9. EXCEPTION HANDLING
try {
    int result = 10 / 0;
} catch (ArithmeticException e) {
    System.out.println("Error: " + e.getMessage());
} finally {
    System.out.println("Cleanup");
}

10. COMMON PACKAGES
- java.lang: Basic classes
- java.util: Collections, Date
- java.io: Input/Output
- java.net: Networking
- java.sql: Database
""",
                "video": "https://www.youtube.com/embed/eIrMbAQSU34",
                "audio": "https://www.youtube.com/embed/grEKMHGYyns",
                "interactive": "https://www.jdoodle.com/online-java-compiler",
                "image": "https://upload.wikimedia.org/wikipedia/en/thumb/3/30/Java_programming_language_logo.svg/121px-Java_programming_language_logo.svg.png"
            },
            {
                "name": "OOP Concepts",
                "notes_title": "Object-Oriented Programming in Java",
                "notes": """OBJECT-ORIENTED PROGRAMMING (OOP) - JAVA NOTES

1. INTRODUCTION
OOP is a programming paradigm based on the concept of "objects" which contain
data (attributes) and code (methods). Java is a pure OOP language.

2. FOUR PILLARS OF OOP

A) ENCAPSULATION
Bundling data and methods that work on that data within one unit (class).
Hide internal state using private variables and provide access via getters/setters.

class Student {
    private String name;
    private int age;

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
}

B) INHERITANCE
A class can inherit properties and methods from another class.

class Animal {
    void eat() { System.out.println("Eating"); }
}

class Dog extends Animal {
    void bark() { System.out.println("Barking"); }
}

C) POLYMORPHISM
Same method behaves differently based on the object.

// Method Overriding
class Shape {
    void draw() { System.out.println("Drawing shape"); }
}

class Circle extends Shape {
    void draw() { System.out.println("Drawing circle"); }
}

// Method Overloading
class Calculator {
    int add(int a, int b) { return a + b; }
    double add(double a, double b) { return a + b; }
}

D) ABSTRACTION
Hide implementation details, show only essential features.

abstract class Vehicle {
    abstract void start();
    void stop() { System.out.println("Stopped"); }
}

interface Drawable {
    void draw();
}

3. CLASSES AND OBJECTS
class Car {
    String brand;
    int year;

    Car(String brand, int year) {
        this.brand = brand;
        this.year = year;
    }
}

Car myCar = new Car("Toyota", 2024);

4. CONSTRUCTORS
- Default constructor
- Parameterized constructor
- Constructor overloading
- Constructor chaining with this() and super()

5. ACCESS MODIFIERS
- public: Accessible everywhere
- private: Only within class
- protected: Within package and subclasses
- default: Within same package

6. STATIC KEYWORD
- static variables: Shared among all instances
- static methods: Can be called without object
- static blocks: Executed when class is loaded

7. FINAL KEYWORD
- final variable: Cannot be changed
- final method: Cannot be overridden
- final class: Cannot be inherited
""",
                "video": "https://www.youtube.com/embed/pTB0EiLXUC8",
                "audio": "https://www.youtube.com/embed/6T_HgnjoYwM",
                "interactive": "https://www.w3schools.com/java/java_oop.asp",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Java_logo.svg/121px-Java_logo.svg.png"
            }
        ]
    },
    {
        "name": "PowerBI",
        "subjects": [
            {
                "name": "Introduction to PowerBI",
                "notes_title": "Power BI Fundamentals",
                "notes": """POWER BI - FUNDAMENTALS NOTES

1. INTRODUCTION
Power BI is Microsoft's business analytics service that provides interactive
visualizations and business intelligence capabilities.

2. KEY COMPONENTS
- Power BI Desktop: Windows application for creating reports
- Power BI Service: Cloud-based sharing platform
- Power BI Mobile: iOS/Android apps
- Power BI Gateway: Connects on-premise data
- Power BI Report Server: On-premise hosting

3. DATA SOURCES
Power BI connects to:
- Excel, CSV, JSON, XML files
- SQL Server, MySQL, PostgreSQL, Oracle
- Web APIs and REST services
- Azure services (SQL DB, Synapse)
- Salesforce, Google Analytics
- SharePoint lists

4. POWER QUERY EDITOR
Used for data transformation (ETL):
- Remove duplicates and nulls
- Filter rows and columns
- Split/merge columns
- Pivot/Unpivot data
- Create custom columns
- Merge queries (like SQL joins)
- Append queries (union)

5. DATA MODELING
- Create relationships between tables
- Types: One-to-Many, Many-to-Many, One-to-One
- Star schema (fact + dimension tables)
- Snowflake schema
- Calculated columns and measures

6. DAX BASICS (Data Analysis Expressions)
// Simple aggregations
Total Sales = SUM(Sales[Amount])
Average Price = AVERAGE(Products[Price])

// CALCULATE with filters
Sales 2024 = CALCULATE([Total Sales], YEAR(Date[Date]) = 2024)

// Time intelligence
YTD Sales = TOTALYTD([Total Sales], Calendar[Date])
MoM Growth = [Total Sales] - CALCULATE([Total Sales], DATEADD(Calendar[Date], -1, MONTH))

7. VISUALIZATIONS
- Column/Bar charts
- Line and Area charts
- Pie and Donut charts
- Scatter plots
- Maps (filled, bubble)
- Tables and Matrix
- KPI cards
- Gauges
- Tree maps
- Waterfall charts
- Slicers (filters)

8. REPORTS VS DASHBOARDS
Reports:
- Multiple pages
- Rich interactivity
- Created in Desktop
- Detailed analysis

Dashboards:
- Single page
- Pinned tiles from reports
- Real-time updates
- High-level overview

9. SHARING AND SECURITY
- Publish to Power BI Service
- Workspaces for team collaboration
- Create apps for distribution
- Row-level security (RLS)
- Embed in websites

10. BEST PRACTICES
- Keep data model simple
- Use meaningful names
- Create reusable measures
- Optimize DAX formulas
- Use appropriate visuals
- Test performance regularly
""",
                "video": "https://www.youtube.com/embed/AGrl-H87pRU",
                "audio": "https://www.youtube.com/embed/TmhQCQr_DCA",
                "interactive": "https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-getting-started",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/New_Power_BI_Logo.svg/120px-New_Power_BI_Logo.svg.png"
            },
            {
                "name": "DAX and Visualizations",
                "notes_title": "DAX Formulas and Advanced Visualizations",
                "notes": """DAX AND ADVANCED VISUALIZATIONS - POWER BI

1. WHAT IS DAX?
Data Analysis Expressions (DAX) is a formula language used in Power BI,
Excel Power Pivot, and Analysis Services. It's similar to Excel formulas
but more powerful.

2. DAX SYNTAX
Measure Name = FUNCTION(Table[Column])

Example:
Total Revenue = SUM(Sales[Amount])

3. COMMON DAX FUNCTIONS

A) Aggregation Functions
- SUM(column)
- AVERAGE(column)
- MIN(column), MAX(column)
- COUNT(column)
- COUNTROWS(table)
- DISTINCTCOUNT(column)

B) Logical Functions
- IF(condition, true_result, false_result)
- SWITCH(expression, value1, result1, ...)
- AND(), OR(), NOT()

C) Filter Functions
- CALCULATE(expression, filter)
- FILTER(table, condition)
- ALL(table), ALLEXCEPT()
- RELATED(column)

D) Time Intelligence
- TOTALYTD(expression, dates)
- SAMEPERIODLASTYEAR(dates)
- DATEADD(dates, -1, MONTH)
- DATESBETWEEN(dates, start, end)

4. CALCULATED COLUMNS VS MEASURES
Calculated Column:
- Evaluated row by row
- Stored in the table
- Uses row context
Example: Full Name = [First Name] & " " & [Last Name]

Measure:
- Evaluated based on filter context
- Not stored (calculated on demand)
- More efficient
Example: Total Sales = SUM(Sales[Amount])

5. VISUALIZATIONS GUIDE

When to use what:
- Comparison: Bar/Column charts
- Trend over time: Line chart
- Parts of whole: Pie/Donut (only if <5 categories)
- Distribution: Histogram, Box plot
- Correlation: Scatter plot
- Geographic: Maps
- KPIs: Cards, Gauges
- Hierarchical: Tree map

6. FORMATTING BEST PRACTICES
- Consistent color scheme
- Clear titles and labels
- Remove chart junk
- Use whitespace effectively
- Highlight important data
- Keep it simple

7. INTERACTIVITY
- Slicers for filtering
- Cross-filtering between visuals
- Drill-through for detail pages
- Bookmarks for scenarios
- Buttons for navigation

8. MOBILE OPTIMIZATION
- Create mobile layout
- Use vertical orientation
- Larger fonts for touch
- Simpler visuals
- Test on actual devices

9. PERFORMANCE TIPS
- Limit number of visuals per page
- Use aggregations for large datasets
- Avoid calculated columns when possible
- Use variables in DAX
- Filter data at source
""",
                "video": "https://www.youtube.com/embed/9OyVYTlZa2Y",
                "audio": "https://www.youtube.com/embed/CGl228sEsuI",
                "interactive": "https://learn.microsoft.com/en-us/dax/",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/New_Power_BI_Logo.svg/120px-New_Power_BI_Logo.svg.png"
            }
        ]
    },
    {
        "name": "Web Development",
        "subjects": [
            {
                "name": "HTML & CSS",
                "notes_title": "HTML and CSS Fundamentals",
                "notes": """HTML & CSS - COMPLETE NOTES

1. HTML INTRODUCTION
HTML (HyperText Markup Language) is the standard markup language for web pages.
It describes the structure and content of a web page.

2. BASIC HTML STRUCTURE
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Page</title>
</head>
<body>
    <h1>Hello World</h1>
    <p>This is a paragraph.</p>
</body>
</html>

3. COMMON HTML TAGS
- Headings: <h1> to <h6>
- Paragraph: <p>
- Links: <a href="url">text</a>
- Images: <img src="image.jpg" alt="desc">
- Lists: <ul>, <ol>, <li>
- Divisions: <div>, <span>
- Forms: <form>, <input>, <button>
- Tables: <table>, <tr>, <td>

4. SEMANTIC HTML
<header>, <nav>, <main>, <article>,
<section>, <aside>, <footer>

5. CSS INTRODUCTION
CSS (Cascading Style Sheets) controls the visual presentation of HTML.
Three ways to apply CSS:
- Inline: <p style="color: red;">
- Internal: <style> in head
- External: <link rel="stylesheet" href="style.css">

6. CSS SELECTORS
/* Element selector */
p { color: blue; }

/* Class selector */
.highlight { background: yellow; }

/* ID selector */
#header { font-size: 24px; }

/* Descendant selector */
div p { margin: 10px; }

7. BOX MODEL
- Content: The actual content
- Padding: Space inside border
- Border: The border itself
- Margin: Space outside border

.box {
    width: 200px;
    padding: 20px;
    border: 2px solid black;
    margin: 10px;
}

8. FLEXBOX
.container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
}

9. CSS GRID
.grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 20px;
}

10. RESPONSIVE DESIGN
@media (max-width: 768px) {
    .container {
        flex-direction: column;
    }
}

11. CSS COLORS AND UNITS
- Colors: red, #ff0000, rgb(255,0,0), hsl(0,100%,50%)
- Units: px, em, rem, %, vw, vh

12. COMMON PROPERTIES
- color, background-color
- font-family, font-size, font-weight
- margin, padding, border
- width, height
- display, position
- transform, transition, animation
""",
                "video": "https://www.youtube.com/embed/mU6anWqZJcc",
                "audio": "https://www.youtube.com/embed/G3e-cpL7ofc",
                "interactive": "https://www.w3schools.com/html/tryit.asp",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/HTML5_logo_and_wordmark.svg/121px-HTML5_logo_and_wordmark.svg.png"
            },
            {
                "name": "JavaScript",
                "notes_title": "JavaScript Programming",
                "notes": """JAVASCRIPT - PROGRAMMING NOTES

1. INTRODUCTION
JavaScript is a high-level, interpreted programming language that runs in browsers
and servers (Node.js). It's the language of the web.

2. VARIABLES
// Modern way
let name = "John";        // Can be reassigned
const age = 25;           // Cannot be reassigned
var oldWay = "legacy";    // Avoid using

3. DATA TYPES
- Number: 42, 3.14
- String: "Hello", 'World', `template`
- Boolean: true, false
- Null: null
- Undefined: undefined
- Object: { key: value }
- Array: [1, 2, 3]

4. OPERATORS
// Arithmetic: +, -, *, /, %, **
// Comparison: ==, ===, !=, !==, <, >, <=, >=
// Logical: &&, ||, !
// Assignment: =, +=, -=, *=, /=

5. CONTROL FLOW
// If-else
if (age >= 18) {
    console.log("Adult");
} else {
    console.log("Minor");
}

// Ternary
const status = age >= 18 ? "Adult" : "Minor";

// Switch
switch (day) {
    case "Monday": console.log("Start"); break;
    default: console.log("Other");
}

6. LOOPS
// For loop
for (let i = 0; i < 5; i++) {
    console.log(i);
}

// For...of (arrays)
for (const item of array) {
    console.log(item);
}

// For...in (objects)
for (const key in object) {
    console.log(key, object[key]);
}

// While
while (condition) { ... }

7. FUNCTIONS
// Function declaration
function add(a, b) {
    return a + b;
}

// Arrow function
const multiply = (a, b) => a * b;

// Default parameters
function greet(name = "World") {
    return `Hello, ${name}!`;
}

8. ARRAYS
const fruits = ["apple", "banana", "orange"];

fruits.push("grape");          // Add to end
fruits.pop();                  // Remove from end
fruits.map(f => f.toUpperCase());
fruits.filter(f => f.length > 5);
fruits.reduce((sum, f) => sum + f.length, 0);

9. OBJECTS
const person = {
    name: "Alice",
    age: 30,
    greet() {
        return `Hi, I'm ${this.name}`;
    }
};

// Destructuring
const { name, age } = person;

10. DOM MANIPULATION
document.getElementById("myId");
document.querySelector(".myClass");
element.innerHTML = "New content";
element.style.color = "red";
element.addEventListener("click", handler);

11. ASYNC JAVASCRIPT
// Promises
fetch("/api/data")
    .then(response => response.json())
    .then(data => console.log(data));

// Async/Await
async function getData() {
    const response = await fetch("/api/data");
    return await response.json();
}

12. ES6+ FEATURES
- Template literals: `Hello ${name}`
- Destructuring: const {a, b} = obj;
- Spread/Rest: ...args
- Modules: import/export
- Classes: class MyClass {}
""",
                "video": "https://www.youtube.com/embed/PkZNo7MFNFg",
                "audio": "https://www.youtube.com/embed/hdI2bqOjy3c",
                "interactive": "https://playcode.io/javascript",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/JavaScript-logo.png/120px-JavaScript-logo.png"
            }
        ]
    },
    {
        "name": "Machine Learning",
        "subjects": [
            {
                "name": "Supervised Learning",
                "notes_title": "Supervised Machine Learning",
                "notes": """SUPERVISED LEARNING - COMPLETE NOTES

1. WHAT IS SUPERVISED LEARNING?
Supervised learning is a type of machine learning where the model learns from
labeled data (input-output pairs). The goal is to predict outputs for new inputs.

2. TYPES OF SUPERVISED LEARNING

A) CLASSIFICATION
Predicting discrete categories/classes.
Examples:
- Email: Spam or Not Spam
- Image: Cat, Dog, or Bird
- Medical: Disease or Healthy

B) REGRESSION
Predicting continuous numerical values.
Examples:
- House price prediction
- Stock price forecasting
- Temperature prediction

3. COMMON ALGORITHMS

A) LINEAR REGRESSION
Predicts a continuous value using a linear equation.
y = mx + b

from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)

B) LOGISTIC REGRESSION
Used for binary classification despite the name.
Outputs probability between 0 and 1.

C) DECISION TREES
Tree-like model of decisions.
Easy to interpret but prone to overfitting.

D) RANDOM FOREST
Ensemble of decision trees.
Reduces overfitting, better accuracy.

E) SUPPORT VECTOR MACHINES (SVM)
Finds the best boundary between classes.
Works well in high-dimensional spaces.

F) K-NEAREST NEIGHBORS (KNN)
Classifies based on majority vote of k nearest points.
Simple but computationally expensive.

G) NEURAL NETWORKS
Multiple layers of interconnected nodes.
Can learn complex patterns.

4. WORKFLOW STEPS

1. Data Collection
2. Data Cleaning (handle missing values, outliers)
3. Feature Engineering
4. Split into Train/Test sets (usually 80/20)
5. Choose Algorithm
6. Train the Model
7. Evaluate Performance
8. Tune Hyperparameters
9. Deploy

5. EVALUATION METRICS

For Classification:
- Accuracy = Correct / Total
- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- F1 Score = 2 * (Precision * Recall) / (Precision + Recall)
- Confusion Matrix

For Regression:
- Mean Absolute Error (MAE)
- Mean Squared Error (MSE)
- Root Mean Squared Error (RMSE)
- R-squared (R²)

6. OVERFITTING AND UNDERFITTING
- Overfitting: Model memorizes training data, poor on new data
- Underfitting: Model too simple, poor on both sets

Solutions:
- Cross-validation
- Regularization (L1, L2)
- More training data
- Feature selection
- Simpler model

7. PRACTICAL EXAMPLE (PYTHON)
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Predict and evaluate
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Accuracy: {accuracy}")
""",
                "video": "https://www.youtube.com/embed/4qVRBYAdLAo",
                "audio": "https://www.youtube.com/embed/ukzFI9rgwfU",
                "interactive": "https://scikit-learn.org/stable/tutorial/basic/tutorial.html",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Scikit_learn_logo_small.svg/120px-Scikit_learn_logo_small.svg.png"
            }
        ]
    }
]


def seed_database():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    print("=" * 60)
    print("STEP 2: SEEDING PROPER CONTENT")
    print("=" * 60)

    total_resources = 0

    for course_data in COURSES:
        course_name = course_data["name"]

        # Check if course exists
        c.execute("SELECT id FROM courses WHERE name=?", (course_name,))
        row = c.fetchone()

        if row:
            course_id = row[0]
            print(f"\n[~] Course exists: {course_name} (id={course_id})")
        else:
            c.execute("INSERT INTO courses (name) VALUES (?)", (course_name,))
            course_id = c.lastrowid
            print(f"\n[+] Added Course: {course_name} (id={course_id})")

        for subject_data in course_data["subjects"]:
            subject_name = subject_data["name"]

            # Check if subject exists
            c.execute("SELECT id FROM subjects WHERE course_id=? AND name=?",
                      (course_id, subject_name))
            row = c.fetchone()

            if row:
                subject_id = row[0]
                print(f"  [~] Subject exists: {subject_name}")
            else:
                c.execute("INSERT INTO subjects (course_id, name) VALUES (?, ?)",
                          (course_id, subject_name))
                subject_id = c.lastrowid
                print(f"  [+] Added Subject: {subject_name}")

            # Write notes file
            notes_filename = f"notes_{course_id}_{subject_id}.txt"
            notes_path = os.path.join(UPLOAD_FOLDER, notes_filename)
            with open(notes_path, "w", encoding="utf-8") as f:
                f.write(subject_data["notes"])

            # Add resources for all learning styles
            resources = [
                (subject_data["notes_title"], "text", f"uploads/{notes_filename}"),
                (f"{subject_name} - Video Tutorial", "video", subject_data["video"]),
                (f"{subject_name} - Audio Lecture", "audio", subject_data["audio"]),
                (f"{subject_name} - Interactive Practice", "interactive", subject_data["interactive"]),
                (f"{subject_name} - Visual Guide", "image", subject_data["image"]),
            ]

            for title, file_type, file_path in resources:
                c.execute("""INSERT INTO resources (title, file_type, file_path, course_id, subject_id)
                             VALUES (?, ?, ?, ?, ?)""",
                          (title, file_type, file_path, course_id, subject_id))
                total_resources += 1

            print(f"      + 5 resources added (text, video, audio, interactive, image)")

    conn.commit()
    conn.close()

    print(f"\n{'=' * 60}")
    print(f"[DONE] Total resources added: {total_resources}")
    print(f"{'=' * 60}")


def show_summary():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    print("\n" + "=" * 60)
    print("FINAL DATABASE SUMMARY")
    print("=" * 60)

    c.execute("""
        SELECT co.name, s.name, COUNT(r.id), GROUP_CONCAT(DISTINCT r.file_type)
        FROM courses co
        LEFT JOIN subjects s ON s.course_id = co.id
        LEFT JOIN resources r ON r.subject_id = s.id
        GROUP BY co.id, s.id
        ORDER BY co.name, s.name
    """)

    for row in c.fetchall():
        course, subject, count, types = row
        print(f"  {course} -> {subject}: {count} resources ({types})")

    conn.close()


if __name__ == "__main__":
    clean_database()
    seed_database()
    show_summary()
