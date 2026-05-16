from flask import Flask, render_template
app= Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return f'Contact us at'

@app.route('/dashboard')
def dashboard():
    return f'Welcome to the dashboard!'



@app.route("/hello/<name>")
def hello(name):
    return f"Hello, {name}!"


if __name__ == '__main__':
    app.run(debug=True)


