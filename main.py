from flask import Flask, request, render_template, redirect, url_for, session,render_template_string,send_from_directory
import mysql.connector
import datetime
app = Flask(__name__)
app.secret= '1234'

# Database connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="University Management System"
)
mycursor = mydb.cursor()

def generateIDPass(UserType,FirstName,LastName,digits=60):
    if UserType=='student':
        mycursor.execute("SELECT MAX(Student_ID) FROM students")
        if result:
            result=mycursor.fetchone()
            result=result+1
            mail=FirstName[0]+LastName+str(digits)
            mycursor.execute("select * from students where College_Email=%s",(mail,))
            if not mycursor.fetchone():
                return generateIDPass(UserType,FirstName,LastName,digits+1)
            
    elif UserType=='faculty':
        mycursor.execute("SELECT MAX(Faculty_ID) FROM faculty")
        if result:
            result=mycursor.fetchone()
            result=result+1
            mail=FirstName[0]+LastName+str(digits)+'@thapar.edu'
            mycursor.execute("select * from faculty where Faculty_Email=%s",(mail,))
            if not mycursor.fetchone():
                return generateIDPass(UserType,FirstName,LastName,digits+1)
    password=FirstName[:3]+LastName[-3:]+str(result)[:3]+'@tiet'
    return mail,password
@app.route('/')
def main():
    return render_template('index.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userType = request.form['userType']
        # firstname = request.form['firstname']
        # middlename = request.form['middlename']
        # lastname = request.form['lastname']
        # phone = request.form['phone']
        # email = request.form['email']
        # college_mail,password = generateIDPass(userType,firstname,lastname)
        # if userType=='student':
        #     street = request.form['street']
        #     district = request.form['district']
        #     state = request.form['state']
        #     country = request.form['country']
        #     gender = request.form['gender']
        #     date_of_birth = request.form['dob']
        # elif userType=='faculty':
        #     return "will make soon"
        # print(firstname, middlename, lastname, email, password,  street, district,  state, country, gender, date_of_birth, phone, sep="\n\n")
    
        # sql = "INSERT INTO `students` (`First_Name`, `Middle_Name`, `Last_Name`, `Street`, `District`, `State`, `Country`, `Gender`, `Date_of_Birth`, `Email`, `College_Email`, `Password`, `Enrollment_Year`,`Status`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        # val = (firstname, middlename, lastname, street, district, state, country, gender, date_of_birth, email, college_mail, password, datetime.datetime.now().year,'Pending')
        # mycursor.execute(sql, val)
        # mydb.commit()

        return f"form has been submitted. Admin will verify your details and send you an email.<br>"
    return render_template('register.html')
@app.route('/signin')
def login():
    return render_template('registration.html')
if __name__ == '__main__':
    app.run(debug=True)