from flask import Flask,render_template

app = Flask(__name__)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/hello/<name>")
def hello(name):
    return f"Hello, {name}!"
   
@app.errorhandler(404)
def error(e):
    return render_template("error.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)

