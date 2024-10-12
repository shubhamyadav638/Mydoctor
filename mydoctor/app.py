from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from cryptography.fernet import Fernet
import secrets
import datetime

app = Flask(__name__)
app.secret_key = "shubham123456"

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mydoctor'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# mail configurations
app.config['MAIL_SERVER'] = 'smtp.hostinger.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'support@citygrocerymall.com'
app.config['MAIL_PASSWORD'] = 'Bipin@007'

mysql = MySQL(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    search_term = request.args.get('search_term')
    print(search_term)
    cur = mysql.connection.cursor()
    if search_term is not None:
        cur.execute("SELECT u.*,p.specialization,p.qualification,p.experience,p.address	 FROM users as u join profiles as p On p.user_id=u.id WHERE u.user_type = %s AND u.name LIKE %s", (3,'%'+search_term+'%'))
    else:
        cur.execute("SELECT u.*,p.specialization,p.qualification,p.experience,p.address	 FROM users as u join profiles as p On p.user_id=u.id WHERE u.user_type = %s", (3,))
    # Fetch all rows returned by the query
    doctors = cur.fetchall()
    cur.close()
    return render_template('index.html',doctors=doctors)

@app.route('/registration', methods=['GET','POST'])
def registration():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form['email']
        phone_no = request.form['phone_no']
        password = request.form['password']

        confirm_password = request.form['confirm_password']

        if full_name == "" or email == "" or phone_no == "" or password == "" or confirm_password == "":
            flash("Please Fill All the fields !!",'error')
            return redirect(url_for('registration'))
        if password != confirm_password :
            flash("Password and Confirm password is not matched !!",'error')
            return redirect(url_for('registration'))

        #hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        hashed_password = password
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        is_email = cur.fetchone()
        if(is_email == None):
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (name, email, phone, password, user_type) VALUES (%s, %s, %s, %s, %s)", (full_name, email, phone_no, hashed_password,2))
            mysql.connection.commit()
            cur.close()
        else:
            flash("Email Alredy exitst !!",'error')
            return redirect(url_for('registration'))
    
        msg = Message('My Doctor', sender='support@citygrocerymall.com', recipients=[email])
        msg.html = render_template('emails/welcome.html', recipient_name=full_name)
        mail.send(msg)
    
        flash("Your Registration have been successfully done !!",'success')

        return redirect(url_for('registration'))

    return render_template('registration.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if isLogin() == True :
       return redirect(url_for('home')) 
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s and password=%s and user_type=%s", (username_or_email,password,2,))
        user = cur.fetchone()
        cur.close()
       

        # hashed_password = user['password']
        if user :
            session['user'] = user
            # You can add a flash message here to show successful login
            flash("Login Successfully Done !",'success')
            return redirect(url_for('home'))
        
        flash("Incorrect password !!",'error')
        return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('home'))



@app.route('/forgot-password', methods=['GET','POST'])
def forgot_password():
     if request.method == 'POST':
            email = request.form['email']
        
        # Generate token
            unique_no = random.uniform(1,9999)
           # token  = cipher_suite.encrypt(unique_no.encode())
            
            # Store token, email, and timestamp in the database
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO reset_passwords (email, token, action_type) VALUES (%s, %s, %s)", (email, unique_no, 'password'))
            mysql.connection.commit()

            msg = Message('My Doctor', sender='support@citygrocerymall.com', recipients=[email])
            msg.html = render_template('emails/password-reset.html', token=unique_no)
            mail.send(msg)
            
            # Send reset email (You need to implement this part)
            # Include a link to the password reset page with the token
            
            flash("Password reset link sent to your email.")

            return redirect(url_for('forgot_password'))
        
     return render_template('forgot-password.html')

@app.route('/reset-password/<token>', methods=['GET','POST'])
def reset_password(token):
    print(token)

@app.route('/doctor-registration', methods=['GET','POST'])
def doctor_registration():
    old_data = {'full_name': '', 'email': ''}
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form['email']
        phone_no = request.form['phone_no']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        specialization = request.form['specialization']
        qualification = request.form['qualification']
        experience = request.form['experience']
        license = request.form['license']
        doctor_fee = request.form['doctor_fee']
        address = request.form['address']
        city = request.form['city']
        zip_code = request.form['zip_code']
        if full_name == "" or email == "" or phone_no == "" or password == "" or confirm_password == "" or specialization == "" or qualification == "" or experience == "" or license == "" or address == "" or city == "" or zip_code == "" :
            flash("Please Fill All the fields !!",'error')
            return redirect(url_for('doctor_registration'))
        if password != confirm_password :
            flash("Password and Confirm password is not matched !!",'error')
            return redirect(url_for('doctor_registration'))

        # hashed_password = bcrypt.generate_password_hash(password,10).decode('utf-8')
        hashed_password = password

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, phone, password, user_type) VALUES (%s, %s, %s, %s, %s)", (full_name, email, phone_no,hashed_password,3))
        mysql.connection.commit()
        user_id = cur.lastrowid
        cur.execute("INSERT INTO profiles (user_id, specialization, qualification, experience, license, address, city, zip_code, doctor_fee) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (user_id, specialization, qualification,experience,license,address,city,zip_code,doctor_fee))
        mysql.connection.commit()
        cur.close()

        flash("Your Registration have been successfully done !!",'success')
        if not full_name:
            old_data['full_name'] = full_name

        #return redirect(url_for('doctor_registration'))
        render_template('doctor_registration.html', old_data=old_data)

    return render_template('doctor_registration.html', old_data=old_data)

@app.route('/doctor-login', methods=['GET','POST'])
def doctor_login():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s and password=%s and user_type=%s", (username_or_email,password,3,))
        user = cur.fetchone()
        cur.close()
       

        # hashed_password = user['password']
        if user :
            session['user'] = user
            print(user)
            # You can add a flash message here to show successful login
            flash("Login Successfully Done !",'success')
            return redirect(url_for('home'))
        
        flash("Incorrect password !!",'error')

        return redirect(url_for('doctor_login'))

    return render_template('doctor-login.html')



@app.route('/book-appointment/<doctor_id>', methods=['GET','POST'])
def book_appointment(doctor_id):
    if isLogin() == False:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user = session['user']

        doctor_id = request.form.get('doctor_id')
        patient_name = request.form.get('patient_name')
        appointment_date = request.form.get('appointment_date')
        messages = request.form.get('messages')
        if patient_name == "" or appointment_date == "" or messages == "" :
            flash("Please Fill All the fields !!",'error')
            return redirect(url_for('book_appointment', doctor_id=doctor_id))
        

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM profiles WHERE user_id = %s", (doctor_id,))
        doctor_profile = cur.fetchone()
         
        cur.execute("INSERT INTO doctor_appintments (doctor_id,user_id, patient_name, appointment_date,doctor_fee) VALUES (%s, %s, %s, %s, %s)", (doctor_id,user['id'], patient_name, appointment_date, doctor_profile['doctor_fee']))
        mysql.connection.commit()
        cur.close()

        flash("Your appointment have been successfully done !!",'success')
        return redirect(url_for('book_appointment', doctor_id=doctor_id))
    
    
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT * FROM users WHERE id = %s", (doctor_id,))
    doctor = cur1.fetchone()
    cur1.close()
    return render_template('book_appointment.html', doctor=doctor)

@app.route('/profile',  methods=['GET','POST'])
def profile():
    if isLogin() == False :
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        if 'profile_image' not in request.files:
            flash('No Image Found', 'error')
            return redirect(url_for('profile')) 
        
        myfile = request.files['profile_image']
        if myfile.filename == '':
            flash('No image selected', 'error')
            return redirect(url_for('profile'))
        

        print(app.static_folder)
        image_path = '/images/uploads/' + myfile.filename
        myfile.save(app.static_folder+image_path)
        user = session['user']
        user_id = user['id']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET profile_img = %s WHERE id = %s", (image_path, user_id))
        mysql.connection.commit()
        cur.close()
        flash('Profile Updated Successfully !!', 'success')
        return redirect(url_for('profile'))

    user = session['user']
    cur = mysql.connection.cursor()
    cur.execute("SELECT u.*,p.specialization,p.qualification,p.experience,p.address	 FROM users as u join profiles as p On p.user_id=u.id WHERE u.id = %s", (user['id'],))
    # Fetch all rows returned by the query
    user_info = cur.fetchone()
    cur.close()
    return render_template('profile.html',user_info=user_info)

@app.route('/my-appointment', methods=['GET','POST'])
def my_appointment():
    if isLogin() == False :
        return redirect(url_for('home'))
    user = session['user']
    user_id=user['id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT da.*, du.name as doctor_name, bu.name as book_by  FROM doctor_appintments as da JOIN users as du ON da.doctor_id = du.id JOIN users as bu ON da.user_id = bu.id  WHERE da.user_id = %s", (user_id,))
    # Fetch all rows returned by the query
    appointments = cur.fetchall()
    cur.close()

    return render_template('my-appointment.html', appointments=appointments)

@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if isLogin() == False :
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        # Get the current user ID from the session or request data
        user = session['user']
        user_id = user['id']
        old_password = request.form['old_password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s and password=%s", (user_id,old_password))
        user = cur.fetchone()
        # Get the new password from the form
        if(user):
            new_password = request.form['new_password']

            # Update the password in the database
            
            cur.execute("UPDATE users SET password = %s WHERE id = %s", (new_password, user_id))
            mysql.connection.commit()
            cur.close()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('change_password')) 
        else:
            flash('Incorrect old Password !', 'error')
            return redirect(url_for('change_password')) 

        
    return render_template('change-password.html')

def isLogin():
    user = session.get('user');
    if user :
        return True
    else:
        return False

if __name__=='__main__':
   app.debug = True
   app.run()