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
            result = 102367001
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
    session.clear()
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
    query = "INSERT INTO `fees`(`Student_ID`, `Amount`,  `Type`) VALUES (%s, %s,  %s)"
    values = (result, 1500,'Registration Fees')
    mycursor.execute(query, values)
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
    if 'user' not in session:
        return redirect(url_for('login'))
    query="SELECT faculty.Faculty_ID, CONCAT(faculty.First_Name,' ',faculty.Middle_Name,' ',faculty.Last_Name) AS Name, faculty.Date_of_Joining, faculty.Designation, faculty.Mail, faculty.Official_Mail, faculty.Password, courses.Course_Name ,department.Department_Name, department.Department_ID FROM faculty INNER JOIN   courses on courses.Course_ID = faculty.Course_ID INNER JOIN department on department.Department_ID =faculty.Department_ID WHERE faculty.Faculty_ID=%s;" 
    mycursor.execute(query,(session['user'][0],))
    faculty=mycursor.fetchall()[0]
    query="select phone from faculty_phone_no where Faculty_ID=%s"
    mycursor.execute(query,(session['user'][0],))
    phones=mycursor.fetchall()
    query="SELECT courses.Course_Name,exams.Exam_Type,exams.Exam_Date FROM exams INNER JOIN courses on courses.Course_ID=exams.Course_ID WHERE exams.Course_ID=%s AND exams.Exam_Date>=CURRENT_DATE ORDER BY exams.Exam_Date ASC;"
    mycursor.execute(query,(session['user'][9],))
    upcoming_exams=mycursor.fetchall()

    query="SELECT courses.Course_Name,exams.Exam_Type,exams.Exam_Date FROM exams INNER JOIN courses on courses.Course_ID=exams.Course_ID WHERE exams.Course_ID=%s AND exams.Exam_Date<CURRENT_DATE AND exams.Status='Unevaluated' ORDER BY exams.Exam_Date ASC;"
    mycursor.execute(query,(session['user'][9],))
    recent_exams=mycursor.fetchall()

    query="SELECT courses.Course_Name,exams.Exam_Type,exams.Exam_Date FROM exams INNER JOIN courses on courses.Course_ID=exams.Course_ID WHERE exams.Course_ID=%s AND exams.Status='Locked' ORDER BY exams.Exam_Date DESC LIMIT 3;"
    mycursor.execute(query,(session['user'][9],))
    locked_exams=mycursor.fetchall()
    return render_template('facultyDashboard.html',faculty=faculty,phones=phones,upcoming_exams=upcoming_exams,recent_exams=recent_exams,locked_exams=locked_exams)


@app.route('/faculty/update/<string:phones>', methods=['POST'])
def update_faculty(phones):
    if 'user' not in session:
        return redirect(url_for('login'))
    if(request.method=='POST'):
        Name=request.form.get('faculty_name')
        names=Name.split(' ')

        if(len(names)==1):
            FirstName=names[0]
            LastName=''
            MiddleName=''
        if(len(names)==2):
            FirstName=names[0]
            LastName=names[1]
            MiddleName=''
        else:
            FirstName=names[0]
            MiddleName=' '.join(names[1:-1])
            LastName=names[-1]
        phone_numbers = [phone[0] for phone in eval(phones)]
        print(phone_numbers, type(phone_numbers), sep="\n\n\n")
        for i in phone_numbers:
            new_phone = request.form.get(f'faculty_phone_{i}')
            if new_phone != i and new_phone:
                query="UPDATE faculty_phone_no SET Phone=%s WHERE Phone=%s and Faculty_ID=%s"
                values=(new_phone,i,session['user'][0])
                mycursor.execute(query,values)
                mydb.commit()
            elif not new_phone:
                query="DELETE FROM faculty_phone_no WHERE Phone=%s and Faculty_ID=%s"
                values=(i,session['user'][0])
                mycursor.execute(query,values)
                mydb.commit()

        personal_mail=request.form.get('faculty_personal_mail')
        work_mail=request.form.get('faculty_work_mail')
        password=request.form.get('faculty_password')
        query="UPDATE faculty SET First_Name=%s, Middle_Name=%s, Last_Name=%s, Mail=%s, Official_Mail=%s, Password=%s WHERE Faculty_ID=%s"
        values=(FirstName,MiddleName,LastName,personal_mail,work_mail,password,session['user'][0])
        mycursor.execute(query,values)
        mydb.commit()
        return redirect(url_for('facultyDashboard'))
    return render_template('facultyDashboard.html')




@app.route('/faculty')
def faculty():
    if 'user' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('facultyDashboard'))


@app.route('/faculty/students')
def facultyStudents():
    if 'user' not in session:
        return redirect(url_for('login'))
    query = f"""
        SELECT CONCAT(s.first_name, ' ', s.Middle_Name, ' ', s.Last_Name) AS Full_Name,s.Gender , c.Course_Name,e.Enrolled_IN , 
s.College_Email,s.student_id
       
       FROM students s
       JOIN enrollment e ON s.Student_ID = e.Student_ID
       JOIN faculty f ON f.Course_ID = e.Course_ID
       JOIN courses c ON c.Course_ID = e.Course_ID
       WHERE f.Faculty_ID = {session['user'][0]}
"""
    mycursor.execute(query)
    students = mycursor.fetchall()
    return render_template('students.html', students=students)

@app.route('/faculty/students/unenroll/<int:student_id>')
def faculty_unenroll_student(student_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "DELETE FROM enrollment WHERE Student_ID=%s and Course_ID=%s"
    mycursor.execute(query, (student_id, session['user'][9]))
    mydb.commit()
    return redirect(url_for('facultyStudents'))
@app.route('/faculty/exams/add', methods=['GET', 'POST'])
def add_exam():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        course_id = request.form.get('course_id')
        exam_date = request.form.get('exam_date')
        exam_duration = request.form.get('exam_duration')
        exam_charge = float(request.form.get('exam_charge'))
        exam_type = request.form.get('exam_type')
        venue = request.form.get('venue')
        
        query = """
            INSERT INTO exams (Course_ID, Exam_Date, Exam_Duration, Exam_Type, Venue) 
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (course_id, exam_date, exam_duration, exam_type, venue)
        mycursor.execute(query, values)
        mydb.commit()
        
        query = """
            INSERT IGNORE INTO takes_exams (Student_ID, Exam_ID) 
            SELECT enrollment.Student_ID, exams.Exam_ID 
            FROM enrollment 
            INNER JOIN exams ON exams.Course_ID = enrollment.Course_ID 
            WHERE exams.Course_ID = %s AND exams.Exam_Type = %s
        """
        mycursor.execute(query, (course_id, exam_type))
        mydb.commit()
        if(exam_charge>0):
            query = """
                INSERT IGNORE INTO fees (Student_ID, Exam_ID, Amount, Type) 
                SELECT enrollment.Student_ID, exams.Exam_ID,  %s, 'Exam Fee' 
                FROM enrollment 
                INNER JOIN exams ON exams.Course_ID = enrollment.Course_ID 
                WHERE exams.Course_ID = %s AND exams.Exam_Type = %s
            """
            mycursor.execute(query, (exam_charge,course_id, exam_type))
            mydb.commit()
        
        return redirect(url_for('facultyExams'))
    return render_template('exams.html', courses=getFacultyCourses())

@app.route('/faculty/exams/update/<int:exam_id>', methods=['POST'])
def update_exam(exam_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        print("here")
        course_id = request.form.get(f'course_id_{exam_id}')
        exam_date = request.form.get(f'exam_date_{exam_id}')
        exam_duration = request.form.get(f'exam_duration_{exam_id}')
        exam_type = request.form.get(f'exam_type_{exam_id}')
        venue = request.form.get(f'exam_venue_{exam_id}')
        query="Select count(*) from exams where course_id=%s and exam_type=%s"
        mycursor.execute(query,(course_id,exam_type))
        count=mycursor.fetchone()[0]

        if count>0:
            return "Exam with this type already exists"
        
        query = """
            UPDATE exams 
            SET Exam_Date=%s, Exam_Duration=%s, Exam_Type=%s, Venue=%s
            WHERE Exam_ID=%s
        """
        values = (exam_date, exam_duration, exam_type, venue, exam_id)
        mycursor.execute(query, values)
        mydb.commit()
        
        return redirect(url_for('facultyExams'))


@app.route('/faculty/exams/delete/<int:exam_id>')
def delete_exam(exam_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "DELETE FROM exams WHERE Exam_ID=%s"
    mycursor.execute(query, (exam_id,))
    mydb.commit()
    return redirect(url_for('facultyExams'))

@app.route('/faculty/exams')
def facultyExams():
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "SELECT * FROM exams WHERE Exam_Date>=CURRENT_DATE AND Course_ID=%s;"
    mycursor.execute(query, (session['user'][9],))
    upcoming_exams = mycursor.fetchall()
    query = "SELECT * FROM exams WHERE Exam_Date<CURRENT_DATE AND Course_ID=%s;"
    mycursor.execute(query, (session['user'][9],))
    recent_exams = mycursor.fetchall()
    return render_template('exams.html', upcoming_exams=upcoming_exams, recent_exams=recent_exams)

@app.route('/faculty/results/<int:exam_id>/evaluate', methods=['GET', 'POST'])
def evaluate(exam_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "SELECT Student_ID, CONCAT(First_Name, ' ', Middle_Name, ' ', Last_Name) AS Full_Name FROM students WHERE Student_ID IN ( SELECT takes_exams.Student_ID FROM takes_exams INNER JOIN exams ON exams.Exam_ID = takes_exams.Exam_ID WHERE exams.Exam_ID = %s ) AND Student_ID NOT IN ( SELECT results.Student_ID FROM results INNER JOIN exams ON results.Exam_ID = exams.Exam_ID WHERE exams.Exam_ID = %s );"
    mycursor.execute(query, (exam_id,exam_id))
    students_to_be_evaluted = mycursor.fetchall()
    query = """ SELECT students.Student_ID, CONCAT(students.First_Name, ' ', students.Middle_Name, ' ', students.Last_Name) AS Full_Name, results.Marks_Obtained, results.Grade FROM students INNER JOIN results ON results.Student_ID = students.Student_ID WHERE students.Student_ID IN ( SELECT takes_exams.Student_ID FROM takes_exams INNER JOIN exams ON exams.Exam_ID = takes_exams.Exam_ID WHERE exams.Exam_ID = %s ) AND results.Exam_ID = %s; """
    mycursor.execute(query, (exam_id,exam_id))
    students_evaluted = mycursor.fetchall()
    query = "SELECT students.Student_ID, CONCAT(students.First_Name, ' ', students.Middle_Name, ' ', students.Last_Name) AS Full_Name, results.Marks_Obtained, results.Grade FROM students INNER JOIN results ON results.Student_ID = students.Student_ID WHERE students.Student_ID IN ( SELECT takes_exams.Student_ID FROM takes_exams INNER JOIN exams ON exams.Exam_ID = takes_exams.Exam_ID WHERE exams.status = 'Locked' AND exams.Exam_ID = %s ) AND results.Exam_ID = %s;"
    mycursor.execute(query, (exam_id,exam_id))
    Locked_Result = mycursor.fetchall()
    print("Locked_Result",Locked_Result)
    print("students_evaluted",students_evaluted)
    print("students_to_be_evaluted",students_to_be_evaluted)
    return render_template('result_evaluation.html', students_to_be_evaluted=students_to_be_evaluted, students_evaluted=students_evaluted, Locked_Result=Locked_Result,exam_id=exam_id)



@app.route('/faculty/results/<int:exam_id>/evaluate/<int:student_id>', methods=['POST'])
def evaluate_student(exam_id, student_id):
    if (request.method=='POST'):
        
        if 'user' not in session:
            return redirect(url_for('login'))
        obtained_marks=request.form.get(f'obtained_marks_{student_id}')
        print("obtained marks",obtained_marks)
        # INSERT INTO `results`(`Exam_ID`, `Student_ID`, `Course_ID`, `Marks_Obtained`)
        query="SELECT Result_ID from results WHERE Exam_ID=%s AND Student_ID=%s"
        mycursor.execute(query,(exam_id,student_id))
        result=mycursor.fetchone()
        if (result):
            query="UPDATE results SET Marks_Obtained=%s WHERE Result_ID=%s"
            values=(obtained_marks,result[0])
            mycursor.execute(query,values)
        else:
            
            query = "INSERT INTO `results`(`Exam_ID`, `Student_ID`, `Course_ID`, `Marks_Obtained`) VALUES (%s, %s, %s, %s)"
            values = (exam_id, student_id, session['user'][9], obtained_marks)
            mycursor.execute(query, values)
        mydb.commit()
        return redirect(url_for('evaluate', exam_id=exam_id))
    
@app.route('/faculty/results/<int:exam_id>/evaluateall/<string:student_ids>', methods=['POST'])
def evaluate_students(exam_id, student_ids):
    
    if 'user' not in session:
        return redirect(url_for('login'))
    student_ids = student_ids.split(',')
    print(student_ids)
    for student_id in student_ids:
        print(student_id)
        obtained_marks = request.form.get(f'obtained_marks_{student_id}')
        if obtained_marks is None:
            print("None detected")
            continue
        print("obtained marks",obtained_marks)
        # INSERT INTO `results`(`Exam_ID`, `Student_ID`, `Course_ID`, `Marks_Obtained`)
        query="SELECT Result_ID from results WHERE Exam_ID=%s AND Student_ID=%s"
        mycursor.execute(query,(exam_id,student_id))
        result=mycursor.fetchone()
        if (result):
            query="UPDATE results SET Marks_Obtained=%s WHERE Result_ID=%s"
            values=(obtained_marks,result[0])
            mycursor.execute(query,values)
        else:
            
            query = "INSERT INTO `results`(`Exam_ID`, `Student_ID`, `Course_ID`, `Marks_Obtained`) VALUES (%s, %s, %s, %s)"
            print(f"INSERT INTO `results`(`Exam_ID`, `Student_ID`, `Course_ID`, `Marks_Obtained`) VALUES ({exam_id}, {student_id}, {session['user'][9]}, {obtained_marks})")
            values = (exam_id, student_id, session['user'][9], obtained_marks)
            mycursor.execute(query, values)
        mydb.commit()
    return redirect(url_for('evaluate', exam_id=exam_id))

def calculate_percentile(data, percentile):
    index = (percentile / 100) * (len(data) - 1)
    lower = int(index)
    upper = lower + 1
    weight = index - lower
    if upper < len(data):
        return data[lower] * (1 - weight) + data[upper] * weight
    else:
        return data[lower]

@app.route('/faculty/results/<int:exam_id>/grade/<string:student_ids>', methods=['POST'])
def result_grade(exam_id, student_ids):
    
    if 'user' not in session:
        return redirect(url_for('login'))
    student_ids = student_ids.split(',')
    query = "SELECT Marks_Obtained FROM results WHERE Exam_ID=%s"
    mycursor.execute(query, (exam_id,))
    obtained_marks = [float(mark[0]) for mark in mycursor.fetchall()]
    obtained_marks.sort()

    percentiles = {p: calculate_percentile(obtained_marks, p) for p in range(30, 100, 10)}
    grade_map = {
        90: 'A', 80: 'A-', 70: 'B', 60: 'B-', 50: 'C', 40: 'C-', 30: 'D', 0: 'E'
    }

    for student_id in student_ids:
        obtained_marks = float(request.form.get(f'obtained_marks_{student_id}', 0))
        grade = next(grade for p, grade in grade_map.items() if obtained_marks >= percentiles.get(p, 0))
        
        query = "UPDATE results SET Grade=%s, Status='Evaluated' WHERE Exam_ID=%s AND Student_ID=%s"
        mycursor.execute(query, (grade, exam_id, student_id))
    
    mydb.commit()
    return redirect(url_for('evaluate', exam_id=exam_id))

@app.route('/faculty/results/<int:exam_id>/lock', methods=['POST'])
def lock(exam_id):
    
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "UPDATE exams SET Status='Locked' WHERE Exam_ID=%s"
    mycursor.execute(query, (exam_id,))
    query = "UPDATE results SET Status='Locked' WHERE Exam_ID=%s"
    mycursor.execute(query, (exam_id,))
    mydb.commit()
    return redirect(url_for('facultyResults'))


@app.route('/faculty/results/<int:exam_id>/delete/<int:student_id>', methods=['POST'])
def delete_student_result(exam_id, student_id):
    
    if 'user' not in session:
        return redirect(url_for('login'))
    if (request.method=='POST'):
        obtained_marks=request.form.get(f'obtained_marks_{student_id}')
        print("obtained marks",obtained_marks)
        # INSERT INTO `results`(`Exam_ID`, `Student_ID`, `Course_ID`, `Marks_Obtained`)
        query="SELECT Result_ID from results WHERE Exam_ID=%s AND Student_ID=%s"
        mycursor.execute(query,(exam_id,student_id))
        result=mycursor.fetchone()
        print(result)
        if (result):
            try:

                query="DELETE FROM results WHERE Result_ID=%s"
                values=(result[0],)
                print(f"DELETE FROM results WHERE Result_ID={result[0]}")
                mycursor.execute(query,values)
                print("deleted")
                mydb.commit()
            except Exception as e:
                print(e)
        else:
            return "Student not evaluated"
        return redirect(url_for('evaluate', exam_id=exam_id))

@app.route('/faculty/results/<int:exam_id>/view', methods=['GET', 'POST'])
def view_results(exam_id):
    
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "SELECT results.Result_ID,results.Student_ID,CONCAT(students.First_Name,' ',students.Middle_Name,' ',students.Last_Name) AS Name,results.Marks_Obtained,results.Grade from results INNER JOIN students ON results.Student_ID=students.Student_ID INNER JOIN courses on results.Course_ID=courses.Course_ID WHERE results.Exam_ID=%s;"
    mycursor.execute(query, (exam_id,))
    results = mycursor.fetchall()
    query="SELECT DISTINCT courses.Course_Name, courses.Credits FROM courses INNER JOIN results ON results.Course_ID=courses.Course_ID WHERE results.Exam_ID=%s;"
    mycursor.execute(query,(exam_id,))  
    course=mycursor.fetchall()[0]
    return render_template('view_result.html', results=results, exam_id=exam_id,course=course)



@app.route('/faculty/results')
def facultyResults():
    
    if 'user' not in session:
        return redirect(url_for('login'))
    print(f"SELECT * FROM exams WHERE Course_ID={session['user'][9]} and Status='Unevaluated';")
    query = "SELECT * FROM exams WHERE Course_ID=%s and Status='Unevaluated';"
    mycursor.execute(query, (session['user'][9],))
    Exams_toEvaluate = mycursor.fetchall()

    query = "SELECT * FROM exams WHERE Course_ID=%s and Status='Evaluated';"
    mycursor.execute(query, (session['user'][9],))
    Evaluated = mycursor.fetchall()

    
    query = "SELECT * FROM exams WHERE Course_ID=%s and Status='Locked';"
    mycursor.execute(query, (session['user'][9],))
    Locked_Result = mycursor.fetchall()


    # query = "SELECT * FROM results WHERE Course_ID=%s';"
    # mycursor.execute(query, (session['user'][9],))
    # results = mycursor.fetchall()
    print("i am here")
    return render_template('results.html', Exams_toEvaluate=Exams_toEvaluate, Evaluated=Evaluated,Locked_Result=Locked_Result)

@app.route('/student/dashboard')
@app.route('/student')
def student():
    
    if 'user' not in session:
        return redirect(url_for('login'))
    query="SELECT `Student_ID`, CONCAT(`First_Name`, ' ', COALESCE(`Middle_Name`, ''), ' ', `Last_Name`) AS `Full_Name`, CONCAT( COALESCE(`Street`, ''), ', ', COALESCE(`District`, ''), ', ', COALESCE(`State`, ''), ', ', COALESCE(`Country`, '') ) AS `Full_Address`, `Gender`, `Date_of_Birth`, `Email`, `College_Email`, `Password`, `Enrollment_Year`, `Graduation_Year`, `Status` FROM `students` WHERE Student_ID=%s;"
    mycursor.execute(query,(session['user'][0],))
    student=mycursor.fetchall()[0]
    query="SELECT Phone FROM student_phone_no WHERE Student_ID=%s;"
    mycursor.execute(query,(session['user'][0],))
    phones=mycursor.fetchall()

    upcoming_exams_query = "SELECT courses.Course_Name,exams.Course_ID,exams.Exam_Type,exams.Exam_Duration,exams.Exam_Date,exams.Venue FROM exams INNER JOIN courses ON courses.Course_ID=exams.Course_ID WHERE exams.Exam_ID IN ( SELECT takes_exams.Exam_ID FROM takes_exams WHERE takes_exams.Student_ID = %s ) AND exams.Exam_Date >= CURRENT_DATE ORDER BY exams.Exam_Date ASC;"
    mycursor.execute(upcoming_exams_query,(session['user'][0],))
    upcoming_exams=mycursor.fetchall()

    recent_exams_query = "SELECT courses.Course_Name,exams.Course_ID,exams.Exam_Type,exams.Exam_Duration,exams.Exam_Date,exams.Venue FROM exams INNER JOIN courses ON courses.Course_ID=exams.Course_ID WHERE exams.Exam_ID IN ( SELECT takes_exams.Exam_ID FROM takes_exams WHERE takes_exams.Student_ID = %s ) AND exams.Exam_Date < CURRENT_DATE ORDER BY exams.Exam_Date ASC;"
    mycursor.execute(recent_exams_query,(session['user'][0],))
    recent_exams=mycursor.fetchall()
    
    query="SELECT  courses.Course_Name,courses.Course_ID,exams.Exam_Type,exams.Exam_Duration,exams.Exam_Date,exams.Venue FROM exams INNER JOIN courses ON exams.Course_ID = courses.Course_ID WHERE exams.Exam_ID IN ( SELECT takes_exams.Exam_ID FROM results INNER JOIN exams ON results.Exam_ID = exams.Exam_ID INNER JOIN takes_exams ON results.Exam_ID = takes_exams.Exam_ID WHERE results.Status = 'Locked' AND takes_exams.Student_ID = %s ) ORDER BY exams.Exam_Date ASC;"
    mycursor.execute(query,(session['user'][0],))
    locked_results=mycursor.fetchall()

    
    query="SELECT  courses.Course_Name,courses.Course_ID,exams.Exam_Type,exams.Exam_Duration,exams.Exam_Date,exams.Venue FROM exams INNER JOIN courses ON exams.Course_ID = courses.Course_ID WHERE exams.Exam_ID IN ( SELECT takes_exams.Exam_ID FROM results INNER JOIN exams ON results.Exam_ID = exams.Exam_ID INNER JOIN takes_exams ON results.Exam_ID = takes_exams.Exam_ID WHERE results.Status = 'Evaluated' AND takes_exams.Student_ID = %s ) ORDER BY exams.Exam_Date ASC;"
    mycursor.execute(query,(session['user'][0],))
    evaluated_results=mycursor.fetchall()
    session['phones']=phones
    return render_template('studentDashboard.html',student=student,phones=phones,upcoming_exams=upcoming_exams,recent_exams=recent_exams,locked_results=locked_results,evaluated_results=evaluated_results)

@app.route('/student/update/<int:student_id>/', methods=['POST'])
def update_student(student_id):
    
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name=request.form.get('studentName')
        names=name.split(' ')
        if(len(names)==1):
            FirstName=names[0]
            LastName=''
            MiddleName=''
        elif(len(names)==2):
            FirstName=names[0]
            LastName=names[1]
            MiddleName=''
        else:
            FirstName=names[0]
            MiddleName=' '.join(names[1:-1])
            LastName=names[-1]
        
        address=request.form.get('Address')
        address_parts = address.split(',')
        street = address_parts[0] if len(address_parts) > 0 else None
        district = address_parts[1] if len(address_parts) > 1 else None
        state = address_parts[2] if len(address_parts) > 2 else None
        country = address_parts[3] if len(address_parts) > 3 else None
        gender = request.form.get('gender')
        dob=request.form.get('DOB')

        email=request.form.get('studentEmail')
        workMail=request.form.get('WorkMail')

        password=request.form.get('password')

        query = """
            UPDATE students 
            SET First_Name=%s, Middle_Name=%s, Last_Name=%s, Street=%s, District=%s, State=%s, Country=%s, Gender=%s, Date_of_Birth=%s, Email=%s, College_Email=%s, Password=%s 
            WHERE Student_ID=%s
        """
        values = (FirstName, MiddleName, LastName, street, district, state, country, gender, dob, email, workMail, password, student_id)
        mycursor.execute(query, values)
        mydb.commit()
        for i in session['phones']:
            print(i,end="\n\n\n\n")
            i=i[0]
            print(i)
            new_phone = request.form.get(f'phone_{i}')
            if new_phone != i and new_phone:
                query="UPDATE student_phone_no SET Phone=%s WHERE Phone=%s and Student_ID=%s"
                print(f"UPDATE student_phone_no SET Phone={new_phone} WHERE Phone={i} and Student_ID={student_id}")
                values=(new_phone,i,student_id)
                mycursor.execute(query,values)
                mydb.commit()
            elif not new_phone:
                query="DELETE FROM student_phone_no WHERE Phone=%s and Student_ID=%s"
                print(f"DELETE FROM student_phone_no WHERE Phone={i} and Student_ID={student_id}")
                values=(i,student_id)
                mycursor.execute(query,values)
                mydb.commit()
        return redirect(url_for('student'))

@app.route('/student/fees')
def studentFees():
    
    if 'user' not in session:
        return redirect(url_for('login'))
    student_id = session['user'][0]
    def fetch_fees(query, params):
        mycursor.execute(query, params)
        return mycursor.fetchall()
    course_registration_fees_pending_query = """
        SELECT fees.Fee_ID, fees.Course_ID, courses.Course_Name, fees.Amount, fees.Issued_Date, fees.Type
        FROM fees
        INNER JOIN courses ON courses.Course_ID = fees.Course_ID
        WHERE fees.student_id = %s AND fees.Status = 'Pending'
    """
    course_registration_fees_pending = fetch_fees(course_registration_fees_pending_query, (student_id,))
    course_registration_fees_paid_query = """
        SELECT fees.Fee_ID, fees.Course_ID, courses.Course_Name, fees.Amount, fees.Issued_Date, fees.Payment_Date, fees.Type, fees.Payment_ID
        FROM fees
        INNER JOIN courses ON courses.Course_ID = fees.Course_ID
        WHERE fees.student_id = %s AND fees.Status != 'Pending'
    """
    course_registration_fees_paid = fetch_fees(course_registration_fees_paid_query, (student_id,))
    exam_fees_query_pending = """
        SELECT fees.Fee_ID, fees.Student_ID, fees.Exam_Id, fees.Amount, fees.Issued_Date, fees.Status, exams_with_courses.Exam_Type, exams_with_courses.Course_Name, exams_with_courses.Course_ID
        FROM fees
        INNER JOIN (
            SELECT exams.Exam_ID, courses.Course_Name, exams.Exam_Type, courses.Course_ID
            FROM exams
            INNER JOIN courses ON exams.Course_ID = courses.Course_ID
        ) AS exams_with_courses ON fees.Exam_ID = exams_with_courses.Exam_ID
        WHERE fees.student_id = %s AND fees.Status = 'Pending'
    """
    exam_fees_pending = fetch_fees(exam_fees_query_pending, (student_id,))

    exam_fees_query_paid = """
        SELECT fees.Fee_ID, fees.Student_ID, fees.Exam_Id, fees.Amount, fees.Issued_Date, fees.Payment_Date, fees.Payment_ID, exams_with_courses.Exam_Type, exams_with_courses.Course_Name, exams_with_courses.Course_ID
        FROM fees
        INNER JOIN (
            SELECT exams.Exam_ID, courses.Course_Name, exams.Exam_Type, courses.Course_ID
            FROM exams
            INNER JOIN courses ON exams.Course_ID = courses.Course_ID
        ) AS exams_with_courses ON fees.Exam_ID = exams_with_courses.Exam_ID
        WHERE fees.student_id = %s AND fees.Status != 'Pending'
    """
    exam_fees_paid = fetch_fees(exam_fees_query_paid, (student_id,))
    registration_fees_pending_query = """
        SELECT Fee_ID, Student_ID, Amount, Issued_Date, Type, Status
        FROM fees
        WHERE Student_ID = %s AND Type = 'Registration Fees' AND Status = 'Pending'
    """
    registration_fees_pending = fetch_fees(registration_fees_pending_query, (student_id,))
    registration_fees_paid_query = """
        SELECT Fee_ID, Student_ID, Amount, Issued_Date, Type, Payment_Date, Payment_ID
        FROM fees
        WHERE Student_ID = %s AND Type = 'Registration Fees' AND Status != 'Pending'
    """
    registration_fees_paid = fetch_fees(registration_fees_paid_query, (student_id,))
    return render_template(
        'fees.html',
        course_registration_fees_pending=course_registration_fees_pending,
        course_registration_fees_paid=course_registration_fees_paid,
        exam_fees_pending=exam_fees_pending,
        exam_fees_paid=exam_fees_paid,
        registration_fees_pending=registration_fees_pending,
        registration_fees_paid=registration_fees_paid
    )


@app.route('/student/fees/pay/<int:fee_id>', methods=['POST'])
def pay_fee(fee_id):
    
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method=='POST':
        payment_ID=request.form.get(f'payment_id_{fee_id}')
        query="select count(*) from fees where Payment_ID=%s"
        mycursor.execute(query,(payment_ID,))
        if mycursor.fetchone()[0]>0:
            return "Invalid Payment ID";
        query = "UPDATE fees SET Status='Paid', Payment_Date=%s, payment_ID=%s WHERE Fee_ID=%s"
        values = (datetime.datetime.now().date(),payment_ID,fee_id)
        mycursor.execute(query, values)
        mydb.commit()
        return redirect(url_for('studentFees'))

@app.route('/student/register', methods=['GET', 'POST'])
def course_register():
    
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        student_id = request.form.get('studentId').strip()
        course_codes = request.form.get('courseCode').strip().split(',')

        mycursor.execute("SELECT Course_ID FROM enrollment WHERE Student_ID=%s", (student_id,))
        registered_courses = [x[0] for x in mycursor.fetchall()]

        new_course_codes = [code for code in course_codes if code not in registered_courses]
        if not new_course_codes:
            return "<script>alert('Already Registered for the course')</script>"

        for course_code in new_course_codes:
            mycursor.execute("SELECT Course_ID,Price FROM courses WHERE Course_ID=%s", (course_code,))
            course_id,price = mycursor.fetchone()

            query = "INSERT INTO `enrollment`(`Student_ID`, `Course_ID`, `Enrolled_IN`) VALUES (%s, %s, %s)"
            values = (student_id, course_id, datetime.datetime.now().date())
            mycursor.execute(query, values)

            query = "INSERT INTO `fees`(`Student_ID`, `Course_ID`, `Amount`, `Type`) VALUES (%s, %s, %s, %s)"
            values = (student_id, course_id, price, 'Course Registration')
            mycursor.execute(query, values)
        mydb.commit()
        return "Course Registered Successfully"
    return render_template('studentDashboard.html')





@app.route('/student/courses')
def studentCourses():
    
    if 'user' not in session:
        return redirect(url_for('login'))
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

@app.route('/student/results')
def studentResults():
    
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "SELECT Results.Result_ID,results.Course_ID,courses.Course_Name,exams.Exam_Date,exams.Exam_Type,results.Marks_Obtained,results.Grade,results.Status FROM results INNER JOIN courses on courses.Course_ID=Results.Course_ID INNER JOIN exams ON exams.Exam_ID=results.Exam_ID WHERE Student_ID=%s AND results.Status='Unevaluated'"
    mycursor.execute(query, (session['user'][0],))
    Unevaluated_results = mycursor.fetchall()
    query = "SELECT Results.Result_ID,results.Course_ID,courses.Course_Name,exams.Exam_Date,exams.Exam_Type,results.Marks_Obtained,results.Grade,results.Status FROM results INNER JOIN courses on courses.Course_ID=Results.Course_ID INNER JOIN exams ON exams.Exam_ID=results.Exam_ID WHERE Student_ID=%s AND results.Status='Evaluated'"
    mycursor.execute(query, (session['user'][0],))
    Evaluated_results = mycursor.fetchall()
    query = "SELECT Results.Result_ID,results.Course_ID,courses.Course_Name,exams.Exam_Date,exams.Exam_Type,results.Marks_Obtained,results.Grade,results.Status FROM results INNER JOIN courses on courses.Course_ID=Results.Course_ID INNER JOIN exams ON exams.Exam_ID=results.Exam_ID WHERE Student_ID=%s AND results.Status='Locked'"
    mycursor.execute(query, (session['user'][0],))
    Locked_results = mycursor.fetchall()
    return render_template('student_result.html', Unevaluated_results=Unevaluated_results, Evaluated_results=Evaluated_results, Locked_results=Locked_results)

@app.route('/admin/approve_student/<int:student_id>')
def approve_student(student_id):
    
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "UPDATE students SET Status='enrolled' WHERE Student_ID=%s"
    mycursor.execute(query, (student_id,))
    mydb.commit()
    return redirect(url_for('adminStudents'))

@app.route('/admin/restrict_student/<int:student_id>')
def restrict_student(student_id):
    
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "UPDATE students SET Status='restricted' WHERE Student_ID=%s"
    mycursor.execute(query, (student_id,))
    mydb.commit()
    return redirect(url_for('adminStudents'))

@app.route('/admin/graduate_student/<int:student_id>')
def graduate_student(student_id):
    
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "UPDATE students SET Status='graduated' WHERE Student_ID=%s"
    mycursor.execute(query, (student_id,))
    mydb.commit()
    return redirect(url_for('adminStudents'))

@app.route('/admin/reject_student/<int:student_id>')
def reject_student(student_id):
    
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "DELETE FROM `students` WHERE Student_ID=%s"
    mycursor.execute(query, (student_id,))
    mydb.commit()
    return redirect(url_for('adminStudents'))


@app.route('/admin/students')
def adminStudents():
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "SELECT Student_ID,CONCAT(First_Name, ' ', Middle_Name, ' ', Last_Name) AS Name, CONCAT(street, ', ', District, ', ', State, ', ', Country) AS Address, Gender, TIMESTAMPDIFF(YEAR, Date_of_Birth, CURRENT_DATE) AS Age, Email, Enrollment_Year, Graduation_Year FROM students WHERE Status='Pending';"
    mycursor.execute(query)
    pending_students = mycursor.fetchall()
    
    query = "SELECT Student_ID,CONCAT(First_Name, ' ', Middle_Name, ' ', Last_Name) AS Name, CONCAT(street, ', ', District, ', ', State, ', ', Country) AS Address, Gender, TIMESTAMPDIFF(YEAR, Date_of_Birth, CURRENT_DATE) AS Age, Email, Enrollment_Year, Graduation_Year FROM students WHERE Status='Enrolled';"
    mycursor.execute(query)
    enrolled_students = mycursor.fetchall()

    
    query = "SELECT Student_ID,CONCAT(First_Name, ' ', Middle_Name, ' ', Last_Name) AS Name, CONCAT(street, ', ', District, ', ', State, ', ', Country) AS Address, Gender, TIMESTAMPDIFF(YEAR, Date_of_Birth, CURRENT_DATE) AS Age, Email, Enrollment_Year, Graduation_Year FROM students WHERE Status='Graduated';"
    mycursor.execute(query)
    graduted_students = mycursor.fetchall()
 
    query = "SELECT Student_ID,CONCAT(First_Name, ' ', Middle_Name, ' ', Last_Name) AS Name, CONCAT(street, ', ', District, ', ', State, ', ', Country) AS Address, Gender, TIMESTAMPDIFF(YEAR, Date_of_Birth, CURRENT_DATE) AS Age, Email, Enrollment_Year, Graduation_Year FROM students WHERE Status='Restricted';"
    mycursor.execute(query)
    restricated_students = mycursor.fetchall()
    return render_template('manage_students.html', pending_students=pending_students, enrolled_students=enrolled_students, graduted_students=graduted_students, restricated_students=restricated_students)

@app.route('/admin/view_student/<int:student_id>')
def view_student(student_id):
    if 'user' not in session:
        return redirect(url_for('login'))
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


@app.route('/admin/view_student/<int:student_id>/UnEnroll/<string:course_id>')
def UnEnroll(student_id, course_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "DELETE FROM `enrollment` WHERE Student_ID=%s AND Course_ID=%s"
    mycursor.execute(query, (student_id, course_id))
    mydb.commit()
    return redirect(url_for('view_student', student_id=student_id))

@app.route('/admin/courses')
def adminCourses():
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "SELECT * FROM courses"
    mycursor.execute(query)
    courses = mycursor.fetchall()
    return render_template('manage_courses.html', courses=courses)

@app.route('/admin/courses/add_course',methods=['POST'])
def add_course():
    if 'user' not in session:
        return redirect(url_for('login'))
    id = request.form.get('course_id')
    name = request.form.get('course_name')
    credits = request.form.get('credits')
    price = request.form.get('price')
    semester = request.form.get('semester')
    mycursor.execute("SELECT * FROM courses WHERE Course_ID=%s", (id,))
    if mycursor.fetchone():
        return "Course ID already exists"
    query = "INSERT INTO `courses`(`Course_ID`, `Course_Name`, `Credits`, `Semester`,`Price`) VALUES (%s, %s, %s, %s,%s)"
    values = (id, name, credits, semester, price)
    mycursor.execute(query, values)
    mydb.commit()
    print("courses added")
    return redirect(url_for('adminCourses'))

@app.route('/admin/course/update/<string:course_id>', methods=['GET', 'POST'])
def update_course(course_id):
    
    if 'user' not in session:
        return redirect(url_for('login'))
    new_course_id = request.form.get("course_id")
    new_course_name = request.form.get("course_name")
    new_course_credits = request.form.get("credits")
    new_course_semester = request.form.get("semester")
    new_course_price = request.form.get("price")
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
            query="UPDATE courses SET  Course_ID=%s,Course_Name=%s, Credits=%s, Semester=%s,price=%s WHERE Course_ID=%s"
            values=(new_course_id,new_course_name,new_course_credits,new_course_semester,new_course_price,course_id)
            mycursor.execute(query,values)
            mydb.commit()
    else:
        query="UPDATE courses SET  Course_Name=%s, Credits=%s, Semester=%s,price=%s WHERE Course_ID=%s"
        values=(new_course_name,float(new_course_credits),new_course_semester,new_course_price,course_id)
        mycursor.execute(query,values)
        mydb.commit()    
    print("course updated")
    return redirect(url_for('adminCourses'))
        
@app.route('/admin/course/delete/<string:course_id>')
def delete_course(course_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    print("course deleted")
    query = "DELETE FROM `courses` WHERE Course_ID=%s"
    mycursor.execute(query, (course_id,))
    mydb.commit()
    return redirect(url_for('adminCourses'))

@app.route('/admin/faculty')
def adminFaculty():
    if 'user' not in session:
        return redirect(url_for('login'))
    query="SELECT faculty.Faculty_ID, CONCAT(faculty.First_Name, ' ', COALESCE(faculty.Middle_Name, ''), ' ', faculty.Last_Name) AS Name, faculty.Date_of_Joining, faculty.Designation, faculty.Mail, faculty.Official_Mail, courses.Course_Name, department.Department_Name FROM faculty INNER JOIN courses ON courses.Course_ID = faculty.Course_ID INNER JOIN department ON department.Department_ID = faculty.Department_ID WHERE faculty.Status = 'Pending';"
    mycursor.execute(query)
    pending_faculty=mycursor.fetchall()
    query="SELECT faculty.Faculty_ID, CONCAT(faculty.First_Name, ' ', COALESCE(faculty.Middle_Name, ''), ' ', faculty.Last_Name) AS Name, faculty.Date_of_Joining, faculty.Designation, faculty.Mail, faculty.Official_Mail, courses.Course_Name, department.Department_Name FROM faculty INNER JOIN courses ON courses.Course_ID = faculty.Course_ID INNER JOIN department ON department.Department_ID = faculty.Department_ID WHERE faculty.Status = 'Active';"
    mycursor.execute(query)
    active_faculty=mycursor.fetchall()
    return render_template('manage_faculty.html', pending=pending_faculty, active=active_faculty)


@app.route('/admin/faculty/view_faculty/<int:faculty_id>')
def view_faculty(faculty_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "SELECT faculty.Faculty_ID, CONCAT(faculty.First_Name,' ', faculty.Middle_Name, ' ', faculty.Last_Name) AS Name, faculty.Date_of_Joining, faculty.Designation, faculty.Mail, faculty.Official_Mail, faculty.Course_ID, courses.Course_Name,faculty.Department_ID,department.Department_Name,faculty.Status FROM faculty INNER JOIN courses ON courses.Course_ID =faculty.Course_ID INNER JOIN department ON department.Department_ID=faculty.Department_ID WHERE faculty.Faculty_ID=%s;"
    mycursor.execute(query, (faculty_id,))
    faculty = mycursor.fetchall()[0]
    query = "SELECT Phone FROM faculty_phone_no WHERE Faculty_ID=%s"
    mycursor.execute(query, (faculty_id,))
    phones = mycursor.fetchall()
    return render_template('view_faculty.html', faculty=faculty, phones=phones)


@app.route('/admin/faculty/approve_faculty/<int:faculty_id>')
def approve_faculty(faculty_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    print("I am here")
    query = "UPDATE faculty SET Status='Active' WHERE Faculty_ID=%s"
    mycursor.execute(query, (faculty_id,))
    mydb.commit()
    return redirect(url_for('adminFaculty'))


@app.route('/admin/faculty/reject_faculty/<int:faculty_id>')
def reject_faculty(faculty_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "DELETE FROM faculty WHERE Faculty_ID=%s"
    mycursor.execute(query, (faculty_id,))
    mydb.commit()

    return redirect(url_for('adminFaculty'))

@app.route('/admin/faculty/delete_faculty/<int:faculty_id>')
def delete_faculty(faculty_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "DELETE FROM faculty WHERE Faculty_ID=%s"
    mycursor.execute(query, (faculty_id,))
    mydb.commit()

    return redirect(url_for('adminFaculty'))

@app.route('/admin/departments')
def adminDepartments():
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "SELECT department.Department_ID, department.Department_Name, department.Head_of_Department AS HOD_ID, CONCAT(hod.First_Name, ' ', COALESCE(hod.Middle_Name, ''), ' ', hod.Last_Name) AS HOD_Name, COUNT(faculty.Faculty_ID) AS FacultyCount FROM department INNER JOIN faculty ON faculty.Department_ID = department.Department_ID LEFT JOIN faculty AS hod ON department.Head_of_Department = hod.Faculty_ID WHERE faculty.Status != 'Pending' GROUP BY department.Department_ID, department.Department_Name, department.Head_of_Department, hod.First_Name, hod.Middle_Name, hod.Last_Name;"
    mycursor.execute(query)
    active_departments = mycursor.fetchall()
    query = "SELECT * FROM `department` WHERE Department_ID NOT IN (SELECT department.Department_ID FROM department INNER JOIN faculty ON faculty.Department_ID = department.Department_ID WHERE faculty.Status != 'Pending' GROUP BY department.Department_ID, department.Department_Name, department.Head_of_Department);"
    mycursor.execute(query)
    inactive_departments = mycursor.fetchall()
    return render_template('manage_department.html', active_departments=active_departments, inactive_departments=inactive_departments)


@app.route('/admin/departments/add_department', methods=['POST'])
def add_department():
    if 'user' not in session:
        return redirect(url_for('login'))
    department_id = request.form.get('department_id')
    department_name = request.form.get('department_name')
    head_of_department = request.form.get('head_of_department')
    mycursor.execute("SELECT * FROM department WHERE Department_ID=%s", (department_id,))
    if mycursor.fetchone():
        return "Department ID already exists"
    query = "INSERT INTO `department`(`Department_ID`, `Department_Name`, `Head_of_Department`) VALUES (%s, %s, %s)"
    values = (department_id, department_name, head_of_department)
    mycursor.execute(query, values)
    mydb.commit()
    print("Department added")
    return redirect(url_for('adminDepartments'))

@app.route('/admin/departments/update/<string:department_id>', methods=['GET', 'POST'])
def update_department(department_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    new_department_id = request.form.get("department_id")
    new_department_name = request.form.get("department_name")
    if new_department_id != department_id:
        query = "SELECT * FROM department WHERE Department_ID=%s"
        mycursor.execute(query, (new_department_id,))
        department = mycursor.fetchone()
        if department:
            return "Can't update department id as it already exists"
        else:
            query = "UPDATE department SET Department_ID=%s, Department_Name=%s WHERE Department_ID=%s"
            values = (new_department_id, new_department_name,  department_id)
            mycursor.execute(query, values)
            mydb.commit()
    else:
        query = "UPDATE department SET Department_Name=%s WHERE Department_ID=%s"
        values = (new_department_name,  department_id)
        mycursor.execute(query, values)
        mydb.commit()
    return redirect(url_for('adminDepartments'))
        
@app.route('/admin/departments/delete/<string:department_id>', methods=['POST'])
def delete_department(department_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "DELETE FROM `department` WHERE Department_ID=%s"
    mycursor.execute(query, (department_id,))
    mydb.commit()
    return redirect(url_for('adminDepartments'))



@app.route('/admin/view_department/<string:department_id>', methods=['GET', 'POST'])
def view_department(department_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    query="SELECT department.Department_ID, department.Department_Name, department.Head_of_Department AS HOD_ID, CONCAT(hod.First_Name, ' ', COALESCE(hod.Middle_Name, ''), ' ', hod.Last_Name) AS HOD_Name, COUNT(faculty.Faculty_ID) AS Faculty_Count FROM department INNER JOIN faculty ON department.Department_ID = faculty.Department_ID LEFT JOIN faculty AS hod ON department.Head_of_Department = hod.Faculty_ID WHERE department.Department_ID = %s GROUP BY department.Department_ID, department.Department_Name, department.Head_of_Department, hod.First_Name, hod.Middle_Name, hod.Last_Name;"
    mycursor.execute(query, (department_id,))
    try:
        department = mycursor.fetchall()[0]
    except :
        department=mycursor.fetchone()
    query = "SELECT Faculty_ID, CONCAT(First_Name, ' ', COALESCE(Middle_Name, ''), ' ', Last_Name) AS Name, Designation, Mail, Official_Mail FROM faculty WHERE Department_ID=%s"
    mycursor.execute(query, (department_id,))
    faculties= mycursor.fetchall()
    return render_template('view_department.html', department=department, faculties=faculties)


@app.route('/admin/view_department/<string:department_id>/appoint_HOD', methods=['GET', 'POST'])
def appoint_HOD(department_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        faculty_id = request.form.get('hod_id')
        query = "UPDATE department SET Head_of_Department=%s WHERE Department_ID=%s"
        mycursor.execute(query, (faculty_id, department_id))
        mydb.commit()
        return redirect(url_for('view_department', department_id=department_id))
    return redirect(url_for('view_department', department_id=department_id))


@app.route('/admin/view_department/<string:department_id>/update_faculty/<int:faculty_id>', methods=['GET', 'POST'])
def update_faculty_(department_id, faculty_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    new_faculty_id = int(request.form.get(f"faculty_id_{faculty_id}"))
    new_faculty_name = request.form.get(f"faculty_name_{faculty_id}")
    new_faculty_designation = request.form.get(f"faculty_designation_{faculty_id}")
    new_faculty_mail = request.form.get(f"faculty_mail_{faculty_id}")
    new_faculty_official_mail = request.form.get(f"faculty_official_mail_{faculty_id}")
    new_faculty_name=new_faculty_name.strip().split(' ')
    if(len(new_faculty_name)==1):
        FirstName=new_faculty_name[0]
        LastName=''
        MiddleName=''
    elif(len(new_faculty_name)==2):
        FirstName=new_faculty_name[0]
        LastName=new_faculty_name[1]
        MiddleName=''
    else:
        FirstName=new_faculty_name[0]
        MiddleName=' '.join(new_faculty_name[1:-1])
        LastName=new_faculty_name[-1]
    if(new_faculty_id!=faculty_id):
        query="SELECT * FROM faculty WHERE Faculty_ID=%s"
        mycursor.execute(query,(new_faculty_id,))
        faculty=mycursor.fetchone()
        if faculty:
            return "can't update faculty id as it already exists"
        else:
            query="UPDATE faculty SET  Faculty_ID=%s,First_Name=%s, Middle_Name=%s, Last_Name=%s, Designation=%s, Mail=%s, Official_Mail=%s WHERE Faculty_ID=%s"
            values=(new_faculty_id,FirstName,MiddleName,LastName,new_faculty_designation,new_faculty_mail,new_faculty_official_mail,faculty_id)
            mycursor.execute(query,values)
            mydb.commit()
    else:
        query="UPDATE faculty SET  First_Name=%s, Middle_Name=%s, Last_Name=%s, Designation=%s, Mail=%s, Official_Mail=%s WHERE Faculty_ID=%s"
        values=(FirstName,MiddleName,LastName,new_faculty_designation,new_faculty_mail,new_faculty_official_mail,faculty_id)
        mycursor.execute(query,values)
        mydb.commit()

    return redirect(url_for('adminDepartments'))
@app.route('/admin/view_department/<string:department_id>/delete_faculty/<int:faculty_id>', methods=['GET', 'POST'])
def delete_faculty_(department_id, faculty_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    # Delete the specified faculty
    query = "DELETE FROM faculty WHERE Faculty_ID=%s"
    mycursor.execute(query, (faculty_id,))
    mydb.commit()

    # Check if there are any faculty left in the department
    check_query = "SELECT COUNT(*) FROM faculty WHERE Department_ID=%s"
    mycursor.execute(check_query, (department_id,))
    count = mycursor.fetchone()[0]  # Fetch the count value

    if count == 0:
        # If no faculty are left, redirect to adminDepartments
        return redirect(url_for('adminDepartments'))

    # Otherwise, redirect back to the view_department page
    return redirect(url_for('view_department', department_id=department_id))

@app.route('/admin/fees/delete/<int:fee_id>')
def delete_fee(fee_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "DELETE FROM fees WHERE Fee_ID=%s"
    mycursor.execute(query, (fee_id,))
    mydb.commit()
    return redirect(url_for('adminFees'))

@app.route('/admin/fees/update/<int:fee_id>', methods=['POST'])
def update_fee(fee_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        amount = request.form.get(f'amount_{fee_id}')
        issued_date = request.form.get(f'issued_date_{fee_id}')
        fee_type = request.form.get(f'type_{fee_id}')
        payment_date = request.form.get(f'payment_date_{fee_id}')
        status = request.form.get(f'status_{fee_id}')
        if status not in ['Pending', 'Paid']:
            return "Invalid status value"
        payment_id = request.form.get(f'payment_id_{fee_id}')

        print(amount, issued_date, fee_type, payment_date, status, payment_id)
        query = """
            UPDATE fees 
            SET  Amount=%s, Issued_Date=%s, Type=%s, Payment_Date=%s, Status=%s, Payment_ID=%s 
            WHERE Fee_ID=%s
        """
        values = (amount, issued_date, fee_type, payment_date, status, payment_id, fee_id)
        mycursor.execute(query, values)
        mydb.commit()
        return redirect(url_for('adminFees'))
    

@app.route('/admin/fees/filter/', methods=['POST'])
def filter_fees():
    if 'user' not in session:
        return redirect(url_for('login'))
    filters = {}
    if request.form.get('fee_id_check'):
        filters['Fee_ID'] = request.form.get('fee_id')
    if request.form.get('student_id_check'):
        filters['Student_ID'] = request.form.get('student_id')
    if request.form.get('exam_id_check'):
        filters['Exam_ID'] = request.form.get('exam_id')
    if request.form.get('course_id_check'):
        filters['Course_ID'] = request.form.get('course_id')
    if request.form.get('amount_check'):
        filters['Amount'] = request.form.get('amount')
    if request.form.get('issued_date_check'):
        filters['Issued_Date'] = request.form.get('issued_date')
    if request.form.get('type_check'):
        filters['Type'] = request.form.get('type')
    if request.form.get('payment_date_check'):
        filters['Payment_Date'] = request.form.get('payment_date')
    if request.form.get('status_check'):
        filters['Status'] = request.form.get('status')
    if request.form.get('payment_id_check'):
        filters['Payment_ID'] = request.form.get('payment_id')

    query = "SELECT * FROM fees WHERE "
    if not filters:
        return redirect(url_for('adminFees'))
    query += " AND ".join([f"{key}=%s" for key in filters.keys()])
    mycursor.execute(query, tuple(filters.values()))
    fees = mycursor.fetchall()
    return render_template('manage_fees.html', fees=fees)
    



@app.route('/admin/fees')
def adminFees():
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "SELECT * FROM fees"
    mycursor.execute(query)
    fees = mycursor.fetchall()
    return render_template('manage_fees.html', fees=fees)
@app.route('/admin/exams')
def adminExams():
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "SELECT exams.Exam_ID, exams.Course_ID, exams.Exam_Date, exams.Exam_Duration, exams.Exam_Type, exams.Venue, exams.Status,courses.Course_Name,courses.Credits FROM exams INNER JOIN courses ON exams.Course_ID=courses.Course_ID WHERE exams.Exam_Date>=CURRENT_DATE ;"
    mycursor.execute(query)
    upcoming_exams = mycursor.fetchall()
    query = "SELECT exams.Exam_ID, exams.Course_ID, exams.Exam_Date, exams.Exam_Duration, exams.Exam_Type, exams.Venue, exams.Status,courses.Course_Name,courses.Credits FROM exams INNER JOIN courses ON exams.Course_ID=courses.Course_ID WHERE exams.Exam_Date<CURRENT_DATE AND exams.Status!='Locked';"
    mycursor.execute(query)
    recent_Unevaluated_exams = mycursor.fetchall()
    query = "SELECT exams.Exam_ID, exams.Course_ID, exams.Exam_Date, exams.Exam_Duration, exams.Exam_Type, exams.Venue, exams.Status,courses.Course_Name,courses.Credits FROM exams INNER JOIN courses ON exams.Course_ID=courses.Course_ID WHERE exams.Exam_Date<CURRENT_DATE AND exams.Status='Locked';"
    mycursor.execute(query)
    recent_Evaluated_exams = mycursor.fetchall()
    return render_template('manage_exams.html', upcoming_exams=upcoming_exams, recent_Unevaluated_exams=recent_Unevaluated_exams, recent_Evaluated_exams=recent_Evaluated_exams)

@app.route('/admin/exams/update_exam/<int:exam_id>/', methods=['POST'])
def update_exam_admin(exam_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    new_exam_id = int(request.form.get(f'exam_id_{exam_id}'))
    new_exam_date = request.form.get(f'exam_date_{exam_id}')
    new_exam_duration = request.form.get(f'exam_duration_{exam_id}')
    new_exam_type = request.form.get(f'exam_type_{exam_id}')
    new_venue = request.form.get(f'venue_{exam_id}')
    course_id = request.form.get(f'course_id_{exam_id}')

    if new_exam_id != exam_id:
        if exam_exists(new_exam_id):
            return "Can't update exam id as it already exists"
        if exam_type_exists(course_id, new_exam_type, new_exam_id):
            return "Exam Type already exists"
        update_exam(new_exam_id, new_exam_date, new_exam_duration, new_exam_type, new_venue, exam_id)
    else:
        if exam_type_exists(course_id, new_exam_type, exam_id):
            return "Exam Type already exists"
        update_exam(None, new_exam_date, new_exam_duration, new_exam_type, new_venue, exam_id)

    return redirect(url_for('adminExams'))

def exam_exists(exam_id):
    query = "SELECT * FROM exams WHERE Exam_ID=%s"
    mycursor.execute(query, (exam_id,))
    return mycursor.fetchone() is not None

def exam_type_exists(course_id, exam_type, exam_id):
    query = "SELECT COUNT(*) FROM exams WHERE Course_ID=%s AND Exam_Type=%s AND Exam_ID!=%s"
    mycursor.execute(query, (course_id, exam_type, exam_id))
    return mycursor.fetchone()[0] > 0

def update_exam(new_exam_id, new_exam_date, new_exam_duration, new_exam_type, new_venue, exam_id):
    if new_exam_id:
        query = "UPDATE exams SET Exam_ID=%s, Exam_Date=%s, Exam_Duration=%s, Exam_Type=%s, Venue=%s WHERE Exam_ID=%s"
        values = (new_exam_id, new_exam_date, new_exam_duration, new_exam_type, new_venue, exam_id)
    else:
        query = "UPDATE exams SET Exam_Date=%s, Exam_Duration=%s, Exam_Type=%s, Venue=%s WHERE Exam_ID=%s"
        values = (new_exam_date, new_exam_duration, new_exam_type, new_venue, exam_id)
    mycursor.execute(query, values)
    mydb.commit()


@app.route('/admin/exams/delete_exam/<int:exam_id>/')
def delete_exam_admin(exam_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "DELETE FROM exams WHERE Exam_ID=%s"
    mycursor.execute(query, (exam_id,))
    mydb.commit()
    return redirect(url_for('adminExams'))

@app.route('/admin/results/<int:exam_id>/view', methods=['GET', 'POST'])
def view_results_admin(exam_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "SELECT results.Result_ID,results.Student_ID,CONCAT(students.First_Name,' ',students.Middle_Name,' ',students.Last_Name) AS Name,results.Marks_Obtained,results.Grade from results INNER JOIN students ON results.Student_ID=students.Student_ID INNER JOIN courses on results.Course_ID=courses.Course_ID WHERE results.Exam_ID=%s;"
    mycursor.execute(query, (exam_id,))
    results = mycursor.fetchall()
    query="SELECT DISTINCT courses.Course_Name, courses.Credits FROM courses INNER JOIN results ON results.Course_ID=courses.Course_ID WHERE results.Exam_ID=%s;"
    mycursor.execute(query,(exam_id,))  
    course=mycursor.fetchall()[0]
    return render_template('view_result_admin.html', results=results, exam_id=exam_id,course=course)

@app.route('/admin/results/')
def adminResults():
    if 'user' not in session:
        return redirect(url_for('login'))
    query = "SELECT exams.Exam_ID, exams.Course_ID, exams.Exam_Date, exams.Exam_Duration, exams.Exam_Type, exams.Venue, exams.Status,courses.Course_Name,courses.Credits FROM exams INNER JOIN courses ON exams.Course_ID=courses.Course_ID WHERE exams.Exam_Date<CURRENT_DATE AND exams.Status!='Locked';"
    mycursor.execute(query)
    Unevaluated_Result = mycursor.fetchall()
    query = "SELECT exams.Exam_ID, exams.Course_ID, exams.Exam_Date, exams.Exam_Duration, exams.Exam_Type, exams.Venue, exams.Status,courses.Course_Name,courses.Credits FROM exams INNER JOIN courses ON exams.Course_ID=courses.Course_ID WHERE exams.Exam_Date<CURRENT_DATE AND exams.Status='Locked';"
    mycursor.execute(query)
    Evautated_Result = mycursor.fetchall()
    return render_template('manage_results.html', Evautated_Result=Evautated_Result, Unevaluated_Result=Unevaluated_Result)

@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect(url_for('login'))
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