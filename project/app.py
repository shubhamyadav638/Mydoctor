from flask import Flask,render_template
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/registration')
def registration():
    return render_template('registration.html')

@app.route('/login')
def login():
    return render_template('login_page.html')

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html')

if __name__=='__main__':
   app.run(debug=True)