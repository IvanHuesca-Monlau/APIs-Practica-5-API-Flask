from flask import Flask, jsonify, redirect, render_template, request, url_for
import pymysql

# New Flask application instance creation
app = Flask(__name__)

def get_connection():
    # Opens a connection with the database
    connection = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="apis-5-flask",
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# This route renders the home page with a form to create new users.
@app.route("/")
def home():
    return render_template("home.html")

# This route checks if the connection to the database is working
@app.route("/db")
def db_status():
    try:
        connection = get_connection()
        connection.close()
        return jsonify({
            "ok": True,
            "mensaje": "Succesfully connected to the database"
        })
    except Exception as error:
        return jsonify({
            "ok": False,
            "error": str(error)
        }), 500

# This route retrieves all users from the database and returns them as a JSON list.
@app.route("/usuarios")
def list_users():
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users ORDER BY id")
        users = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(users)
    except Exception as error:
        return jsonify({
            "ok": False,
            "error": str(error)
        }), 500

# This route retrieves a single user by their id and returns it as JSON.
@app.route("/usuarios/<int:user_id>")
def get_user(user_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if user is None:
            return jsonify({
                "error": "User not found"
            }), 404
            
        return jsonify(user)
    except Exception as error:
        return jsonify({
            "ok": False,
            "error": str(error)
        }), 500

# This route creates a new user in the database using data from the HTML form
@app.route("/usuarios", methods=["POST"])
def create_user():
    name = request.form.get("name")
    email = request.form.get("email")
    
    if not name or not email:
        return jsonify({
            "error": "Name or email is missing"
        }), 400
        
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (name, email)
        )
        connection.commit()
        new_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        return redirect(url_for("get_user", user_id=new_id))
    except Exception as error:
        return jsonify({
            "ok": False,
            "error": str(error)
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
