from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('login.html')
@app.route('/create-shipment')
def create_shipment():
    return render_template('create-shipment.html')
@app.route('/shipment-history')
def shipment_history():
    return render_template('shipment-history.html')


if __name__ == '__main__':
    app.run(debug=True)


