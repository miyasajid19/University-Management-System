from flask import Flask, request, render_template, redirect, url_for, session,render_template_string,send_from_directory
import mysql.connector
import datetime
app = Flask(__name__)
app.secret_key = '1234'

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
        result = mycursor.fetchone()[0]
        if result is None:
            result = 102367000
        else:
            result =int(result)+ 1
        mail = FirstName[0] + LastName + str(digits)+'_be'+str(datetime.datetime.now().date().year)[-2:]+'@thapar.edu'
        mycursor.execute("select * from students where College_Email=%s", (mail,))
        if mycursor.fetchone():
            return generateIDPass(UserType,FirstName,LastName,int(digits)+1)
            
    elif UserType=='faculty':
        mycursor.execute("SELECT MAX(Faculty_ID) FROM faculty")
        result = mycursor.fetchone()[0]
        if result is None:
            result = 102367000
        else:
            result += 1
        mail = FirstName[0] + LastName + str(digits) + '@thapar.edu'
        mycursor.execute("select * from faculty where Faculty_Email=%s", (mail,))
        if mycursor.fetchone():
            return generateIDPass(UserType,FirstName,LastName,digits+1)
            
    password = FirstName[:3] + LastName[-3:] + str(result)[-2:] + '@tiet'
    return mail, password, result
@app.route('/')
def main():
    return render_template('index.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userType=request.form.get('userType')
        if(userType=='student'):
            FirstName = request.form.get('firstname').lower().strip()
            MiddleName = request.form.get('middlename').lower().strip()
            LastName = request.form.get('lastname').lower().strip()
            DOB = request.form.get('dob')
            gender = request.form.get('gender')
            street = request.form.get('street').lower().strip()
            district = request.form.get('district').lower().strip()
            state = request.form.get('state').lower().strip()
            country = request.form.get('country').lower().strip()
            email = request.form.get('email').lower().strip()
            phones = request.form.get('phone').lower().strip().split(',')
            print(phones)
            mail, password, result = generateIDPass('student', FirstName, LastName)
            query = "INSERT INTO `students`(`Student_ID`, `First_Name`, `Middle_Name`, `Last_Name`, `Street`, `District`, `State`, `Country`, `Gender`, `Date_of_Birth`, `Email`, `College_Email`, `Password`, `Enrollment_Year`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (result, FirstName, MiddleName, LastName, street, district, state, country, gender, DOB, email, mail, password, datetime.datetime.now().year)
            mycursor.execute(query, values)
            for phone in phones:
                sql="INSERT INTO `student_phone_no`(`Student_ID`, `Phone`) VALUES (%s, %s)"
                values=(result,phone)
                mycursor.execute(sql,values)
        else:
            FirstName = request.form.get('firstname').lower().strip()
            MiddleName = request.form.get('middlename').lower().strip()
            LastName = request.form.get('lastname').lower().strip()
            Date_of_Joining = request.form.get('facultyDOJ')
            facultyDesignation = request.form.get('facultyDesignation')
            facultyStatus = request.form.get('facultyStatus')
            facultyCourseName=request.form.get('facultyCourseName')
            facultyCourseID=request.form.get('facultyCourseID')
            facultyDepartmentID=request.form.get('facultyDepartmentID')
            email = request.form.get('email').lower().strip()
            phones = request.form.get('phone').lower().strip().split(',')


        mydb.commit()
        print(request.form)
        return f"Form has been submitted. Admin will verify your details and send you an email.<br>"
    return render_template('register.html')

@app.route('/signin')
def login():
    return render_template('registration.html')
if __name__ == '__main__':

    app.run(debug=True)