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
            result = 1
        else:
            result += 1
        mail = FirstName[0] + LastName + str(digits) + '@thapar.edu'
        mycursor.execute("select * from faculty where official_mail=%s", (mail,))
        if mycursor.fetchone():
            return generateIDPass(UserType,FirstName,LastName,digits+1)
            
    password = FirstName[:3] + LastName[-3:] + str(result)[-2:] + '@tiet'
    return mail, password, result









def getFacultyCourses():
    mycursor.execute("SELECT  Course_ID,Course_Name FROM courses")
    courses = mycursor.fetchall()
    return courses



def getFacultyDepartments():
    mycursor.execute("SELECT  Department_ID,Department_Name FROM department")
    departments = mycursor.fetchall()
    return departments




courses={"courses":getFacultyCourses()}
departments={"departments":getFacultyDepartments()}




@app.route('/')
def main():
    return render_template('index.html')









@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userType = request.form.get('userType')
        FirstName = request.form.get('firstname').lower().strip()
        MiddleName = request.form.get('middlename').lower().strip()
        LastName = request.form.get('lastname').lower().strip()
        email = request.form.get('email').lower().strip()
        phones = request.form.get('phone').lower().strip().split(',')
        if userType == 'student':
            register_student(FirstName, MiddleName, LastName, email, phones, request.form)
        else:
            register_faculty(FirstName, MiddleName, LastName, email, phones, request.form)

        return "Form has been submitted. Admin will verify your details and send you an email.<br>"
    return render_template('registration.html')










def register_student(FirstName, MiddleName, LastName, email, phones, form):
    DOB = form.get('dob')
    gender = form.get('gender')
    street = form.get('street').lower().strip()
    district = form.get('district').lower().strip()
    state = form.get('state').lower().strip()
    country = form.get('country').lower().strip()
    mail, password, result = generateIDPass('student', FirstName, LastName)
    query = """
        INSERT INTO students (Student_ID, First_Name, Middle_Name, Last_Name, Street, District, State, Country, Gender, Date_of_Birth, Email, College_Email, Password, Enrollment_Year)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (result, FirstName, MiddleName, LastName, street, district, state, country, gender, DOB, email, mail, password, datetime.datetime.now().year)
    mycursor.execute(query, values)
    mydb.commit()
    for phone in phones:
        sql = "INSERT INTO student_phone_no (Student_ID, Phone) VALUES (%s, %s)"
        values = (result, phone)
        mycursor.execute(sql, values)
    mydb.commit()










def register_faculty(FirstName, MiddleName, LastName, email, phones, form):
    Date_of_Joining = datetime.datetime.now().date().strftime('%Y-%m-%d')
    facultyCourseID = form.get('facultyCourseID')
    facultyCourseName = form.get('facultyCourseName').strip()
    facultyDepartmentID = form.get('facultyDepartmentID')
    facultyDesignation = form.get('Designation')
    mail, password, result = generateIDPass('faculty', FirstName, LastName)
    print("first name",FirstName)
    print("middle name",MiddleName)
    print("last name",LastName)
    print("email",email)
    print("phones",phones)
    print("Date_of_Joining",Date_of_Joining)
    print("facultyCourseID",facultyCourseID)
    print("facultyCourseName",facultyCourseName)
    print("facultyDepartmentID",facultyDepartmentID)
    print("facultyDesignation",facultyDesignation)
    print("mail",mail)
    print("password",password)
    print("result",result)
    query = """ INSERT INTO `faculty`(`Faculty_ID`, `First_Name`, `Middle_Name`, `Last_Name`, `Date_of_Joining`,`Designation`,`mail`, `Official_Mail`, `Password`, `Course_ID`, `Department_ID`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
    values = (str(result), FirstName, MiddleName, LastName, Date_of_Joining, facultyDesignation, email, mail, password, facultyCourseID, facultyDepartmentID)
    mycursor.execute(query, values)
    for phone in phones:
        sql = "INSERT INTO faculty_phone_no (Faculty_ID, Phone) VALUES (%s, %s)"
        values = (result, phone)
        mycursor.execute(sql, values)
    mydb.commit()










@app.route('/signup')
def signup():
    return render_template('registration.html',**courses,**departments)





@app.route('/faculty/dashboard')
def facultyDashboard():
    return render_template('facultyDashboard.html')





@app.route('/faculty')
def faculty():
    return redirect(url_for('facultyDashboard'))


@app.route('/faculty/students')
def facultyStudents():
    print(session['user'])
    query = f"""
        SELECT CONCAT(s.first_name, ' ', s.Middle_Name, ' ', s.Last_Name) AS Full_Name, 
       c.Course_Name, 
       e.Enrolled_IN 
       FROM students s
       JOIN enrollment e ON s.Student_ID = e.Student_ID
       JOIN faculty f ON f.Course_ID = e.Course_ID
       JOIN courses c ON c.Course_ID = e.Course_ID
       WHERE f.Faculty_ID =  {session['user'][0]}
"""
    mycursor.execute(query)
    students = mycursor.fetchall()
    return render_template('students.html', students=students)


@app.route('/faculty/exams/add', methods=['GET', 'POST'])
def add():
    course_id=request.form.get('course_id')
    exam_date=request.form.get('exam_date')
    exam_duration=request.form.get('exam_duration')
    exam_type=request.form.get('exam_type')
    venue=request.form.get('venue')
    
    query="INSERT INTO `exams`(`Course_ID`, `Exam_Date`, `Exam_Duration`, `Exam_Type`, `Venue`) VALUES (%s, %s, %s, %s, %s)"
    values=(course_id,exam_date,exam_duration,exam_type,venue)
    mycursor.execute(query,values)
    mydb.commit()
    return "Exam Added Successfully"

@app.route('/faculty/exams')
def facultyExams():
    return render_template('exams.html')



@app.route('/student')
def student():
    return render_template('studentDashboard.html')








@app.route('/student/register', methods=['GET', 'POST'])
def course_register():
    if request.method == 'POST':
        student_id = request.form.get('studentId').strip()
        course_codes = request.form.get('courseCode').strip().split(',')

        mycursor.execute("SELECT Course_ID FROM enrollment WHERE Student_ID=%s", (student_id,))
        registered_courses = [x[0] for x in mycursor.fetchall()]

        new_course_codes = [code for code in course_codes if code not in registered_courses]
        if not new_course_codes:
            return "<script>alert('Already Registered for the course')</script>"

        for course_code in new_course_codes:
            mycursor.execute("SELECT Course_ID FROM courses WHERE Course_ID=%s", (course_code,))
            course_id = mycursor.fetchone()[0]

            query = "INSERT INTO `enrollment`(`Student_ID`, `Course_ID`, `Enrolled_IN`) VALUES (%s, %s, %s)"
            values = (student_id, course_id, datetime.datetime.now().date())
            mycursor.execute(query, values)
        
        mydb.commit()
        return "Course Registered Successfully"
    return render_template('studentDashboard.html')





@app.route('/student/courses')
def studentCourses():
    query = "SELECT * FROM courses"
    mycursor.execute(query)
    courses = {}
    for x in mycursor.fetchall():
        if x[2] not in courses:
            courses[x[2]] = []
        courses[x[2]].append({
            "code": x[0],
            "name": x[1],
            "credits": x[3]
        })
    return render_template('coursesRegistration.html', courses=courses)

@app.route('/admin/approve_student/<int:student_id>', methods=['POST'])
def approve_student(student_id):
    query = "UPDATE students SET Status='enrolled' WHERE Student_ID=%s"
    mycursor.execute(query, (student_id,))
    mydb.commit()
    return redirect(url_for('adminStudents'))

@app.route('/admin/reject_student/<int:student_id>', methods=['POST'])
def reject_student(student_id):
    query = "DELETE FROM `students` WHERE Student_ID=%s"
    mycursor.execute(query, (student_id,))
    mydb.commit()
    return redirect(url_for('adminStudents'))


@app.route('/admin/students')
def adminStudents():
    query = "SELECT Student_ID,CONCAT(First_Name, ' ', Middle_Name, ' ', Last_Name) AS Name, CONCAT(street, ', ', District, ', ', State, ', ', Country) AS Address, Gender, TIMESTAMPDIFF(YEAR, Date_of_Birth, CURRENT_DATE) AS Age, Email, Enrollment_Year, Graduation_Year, Status FROM students;"
    mycursor.execute(query)
    students = mycursor.fetchall()
    pending=list()
    enrolled=list()
    graduated=list()
    restricated=list()
    for student in students:
        if student[-1].lower()=='pending':
            pending.append(student)
        elif student[-1].lower()=='graduated':
            graduated.append(student)
        elif student[-1].lower()=='restricted':
            restricated.append(student)
        else:
            enrolled.append(student)
        
    return render_template('manage_students.html', pending=pending, enrolled=enrolled, graduated=graduated, restricated=restricated)

@app.route('/admin/view_student/<int:student_id>', methods=['GET', 'POST'])
def view_student(student_id):
    query = "SELECT * FROM students WHERE Student_ID=%s"
    mycursor.execute(query, (student_id,))
    details={}
    details["student"] = mycursor.fetchone()
    query="select c.Course_ID,c.Course_Name,c.Credits,c.Semester,e.Enrolled_IN from courses c INNER JOIN enrollment e on e.Course_ID=c.Course_ID WHERE e.Student_ID=%s;"
    mycursor.execute(query,(student_id,))
    details["courses"]=mycursor.fetchall()
    query="select Phone from student_phone_no where Student_ID=%s;"
    mycursor.execute(query,(student_id,))
    details["contacts"]=mycursor.fetchall()
    return render_template('view_student.html', **details)


@app.route('/admin/view_student/<int:student_id>/UnEnroll/<string:course_id>', methods=['POST'])
def UnEnroll(student_id, course_id):
    query = "DELETE FROM `enrollment` WHERE Student_ID=%s AND Course_ID=%s"
    mycursor.execute(query, (student_id, course_id))
    mydb.commit()
    return redirect(url_for('view_student', student_id=student_id))

@app.route('/admin/courses')
def adminCourses():
    query = "SELECT * FROM courses"
    mycursor.execute(query)
    courses = mycursor.fetchall()
    return render_template('manage_courses.html', courses=courses)

@app.route('/admin/courses/add_course', methods=['POST'])
def add_course():
    id = request.form.get('course_id')
    name = request.form.get('course_name')
    credits = request.form.get('credits')
    semester = request.form.get('semester')
    mycursor.execute("SELECT * FROM courses WHERE Course_ID=%s", (id,))
    if mycursor.fetchone():
        return "Course ID already exists"
    query = "INSERT INTO `courses`(`Course_ID`, `Course_Name`, `Credits`, `Semester`) VALUES (%s, %s, %s, %s)"
    values = (id, name, credits, semester)
    mycursor.execute(query, values)
    mydb.commit()
    print("courses added")
    return redirect(url_for('adminCourses'))

@app.route('/admin/course/update/<string:course_id>', methods=['GET', 'POST'])
def update_course(course_id):
    new_course_id = request.form.get("course_id")
    new_course_name = request.form.get("course_name")
    new_course_credits = request.form.get("credits")
    new_course_semester = request.form.get("semester")
    print("new_course_id",new_course_id)
    print("new_course_name",new_course_name)
    print("new_course_credits",new_course_credits)
    print("new_course_semester",new_course_semester)

    print(new_course_id,course_id)
    if(new_course_id!=course_id):
        query="SELECT * FROM courses WHERE Course_ID=%s"
        mycursor.execute(query,(new_course_id,))
        course=mycursor.fetchone()
        if course:
            return "can't update course id as it already exists"
        else:
            query="UPDATE courses SET  Course_ID=%s,Course_Name=%s, Credits=%s, Semester=%s WHERE Course_ID=%s"
            values=(new_course_id,new_course_name,new_course_credits,new_course_semester,course_id)
            mycursor.execute(query,values)
            mydb.commit()
    else:
        query="UPDATE courses SET  Course_Name=%s, Credits=%s, Semester=%s WHERE Course_ID=%s"
        values=(new_course_name,float(new_course_credits),new_course_semester,course_id)
        mycursor.execute(query,values)
        mydb.commit()    
    print("course updated")
    return redirect(url_for('adminCourses'))
        
@app.route('/admin/course/delete/<string:course_id>', methods=['POST'])
def delete_course(course_id):
    print("course deleted")
    query = "DELETE FROM `courses` WHERE Course_ID=%s"
    mycursor.execute(query, (course_id,))
    mydb.commit()
    return redirect(url_for('adminCourses'))
@app.route('/admin')
def admin():
    return render_template('adminDashboard.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('main'))    

@app.route('/login_user', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email').lower().strip()
        password = request.form.get('password').strip()
        userType = request.form.get('user-type')
        if userType == 'student':
            mycursor.execute("SELECT * FROM students WHERE College_Email=%s AND Password=%s", (email, password))
            user = mycursor.fetchone()
            if user:
                session['user'] = user
                return redirect(url_for('student'))
        elif userType == 'faculty':
            mycursor.execute("SELECT * FROM faculty WHERE official_mail=%s AND Password=%s", (email, password))
            user = mycursor.fetchone()
            if user:
                session['user'] = user
                return redirect(url_for('faculty'))
        elif userType == 'admin':
            mycursor.execute("SELECT * FROM admin WHERE Email=%s AND Password=%s", (email, password))
            user = mycursor.fetchone()
            print(user)
            if user:
                session['user'] = user
                return redirect(url_for('admin'))
        else:
            return "Invalid User Type"
    return render_template('signin.html')







@app.route('/signin')
def login():
    return render_template('signin.html',**courses,**departments)









if __name__ == '__main__':

    app.run(debug=True)