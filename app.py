from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

# ---------------- DATABASE SETUP ----------------

def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        assigned_to TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")

# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, password)
            )

            conn.commit()

        except:
            conn.close()
            return "Username already exists!"

        conn.close()

        return "Registration Successful!"

    return render_template("register.html")

# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cur.fetchone()

        conn.close()

        if user:
            return "Login Successful!"
        else:
            return "Invalid Username or Password"

    return render_template("login.html")

# ---------------- CREATE TASK ----------------

@app.route("/create_task", methods=["GET", "POST"])
def create_task():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        assigned_to = request.form["assigned_to"]
        status = request.form["status"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO tasks(title,description,assigned_to,status)
            VALUES(?,?,?,?)
        """,
        (title, description, assigned_to, status))

        conn.commit()
        conn.close()

        return redirect("/tasks")

    return render_template("create_task.html")

# ---------------- VIEW TASKS ----------------

@app.route("/tasks")
def tasks():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM tasks")
    all_tasks = cur.fetchall()

    conn.close()

    # Dashboard Counts
    total = len(all_tasks)

    pending = len([t for t in all_tasks if t[4] == "Pending"])
    inprogress = len([t for t in all_tasks if t[4] == "In Progress"])
    completed = len([t for t in all_tasks if t[4] == "Completed"])

    return render_template(
        "tasks.html",
        tasks=all_tasks,
        total=total,
        pending=pending,
        inprogress=inprogress,
        completed=completed
    )
# ---------------- DELETE TASK ----------------

@app.route("/delete_task/<int:id>")
def delete_task(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM tasks WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/tasks")

# ---------------- EDIT TASK ----------------

@app.route("/edit_task/<int:id>", methods=["GET", "POST"])
def edit_task(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        assigned_to = request.form["assigned_to"]
        status = request.form["status"]

        cur.execute("""
            UPDATE tasks
            SET title=?,
                description=?,
                assigned_to=?,
                status=?
            WHERE id=?
        """,
        (title, description, assigned_to, status, id))

        conn.commit()
        conn.close()

        return redirect("/tasks")

    cur.execute(
        "SELECT * FROM tasks WHERE id=?",
        (id,)
    )

    task = cur.fetchone()

    conn.close()

    return render_template("edit_task.html", task=task)

# ---------------- RUN APP ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)