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
    query="SELECT faculty.Faculty_ID, CONCAT(faculty.First_Name,' ',faculty.Middle_Name,' ',faculty.Last_Name) AS Name, faculty.Date_of_Joining, faculty.Designation, faculty.Mail, faculty.Official_Mail, faculty.Password, courses.Course_Name ,department.Department_Name, department.Department_ID FROM faculty INNER JOIN   courses on courses.Course_ID = faculty.Course_ID INNER JOIN department on department.Department_ID =faculty.Department_ID WHERE faculty.Faculty_ID=%s;" 
    mycursor.execute(query,(session['user'][0],))
    faculty=mycursor.fetchall()[0]
    query="select phone from faculty_phone_no where Faculty_ID=%s"
    mycursor.execute(query,(session['user'][0],))
    phones=mycursor.fetchall()
    return render_template('facultyDashboard.html',faculty=faculty,phones=phones)


@app.route('/faculty/update/<string:phones>', methods=['POST'])
def update_faculty(phones):
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
    query="INSERT IGNORE INTO takes_exams (Student_ID, Exam_ID) SELECT enrollment.Student_ID, exams.Exam_ID FROM enrollment INNER JOIN exams ON exams.Course_ID = enrollment.Course_ID;"
    mycursor.execute(query)
    mydb.commit()
    return "Exam Added Successfully"

@app.route('/faculty/exams')
def facultyExams():
    query = "SELECT * FROM exams WHERE Exam_Date>=CURRENT_DATE AND Course_ID=%s;"
    mycursor.execute(query, (session['user'][9],))
    upcoming_exams = mycursor.fetchall()
    query = "SELECT * FROM exams WHERE Exam_Date<CURRENT_DATE AND Course_ID=%s;"
    mycursor.execute(query, (session['user'][9],))
    recent_exams = mycursor.fetchall()
    return render_template('exams.html', upcoming_exams=upcoming_exams, recent_exams=recent_exams)

@app.route('/faculty/results/<int:exam_id>/evaluate', methods=['GET', 'POST'])
def evaluate(exam_id):
    query = "SELECT Student_ID,concat(First_Name,' ',Middle_Name,' ',Last_Name) FROM students WHERE Student_ID in (SELECT takes_exams.Student_ID from takes_exams INNER JOIN exams on exams.Exam_ID=takes_exams.Exam_ID WHERE exams.Exam_ID=%s) AND Student_ID NOT IN (SELECT results.Student_ID from results INNER join exams on results.Exam_ID=exams.Exam_ID);"
    mycursor.execute(query, (exam_id,))
    students_to_be_evaluted = mycursor.fetchall()
    query = "SELECT students.Student_ID, CONCAT(students.First_Name, ' ', students.Middle_Name, ' ', students.Last_Name) AS Full_Name, results.Marks_Obtained, results.Grade FROM students INNER JOIN results ON results.Student_ID = students.Student_ID WHERE students.Student_ID IN ( SELECT takes_exams.Student_ID FROM takes_exams INNER JOIN exams ON exams.Exam_ID = takes_exams.Exam_ID WHERE exams.Exam_ID = %s ) AND students.Student_ID IN ( SELECT results.Student_ID FROM results INNER JOIN exams ON results.Exam_ID = exams.Exam_ID );"
    mycursor.execute(query, (exam_id,))
    students_evaluted = mycursor.fetchall()
    return render_template('result_evaluation.html', students_to_be_evaluted=students_to_be_evaluted, students_evaluted=students_evaluted, exam_id=exam_id)



@app.route('/faculty/results/<int:exam_id>/evaluate/<int:student_id>', methods=['POST'])
def evaluate_student(exam_id, student_id):
    if (request.method=='POST'):
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
        
        query = "UPDATE results SET Grade=%s WHERE Exam_ID=%s AND Student_ID=%s"
        mycursor.execute(query, (grade, exam_id, student_id))
    
    mydb.commit()
    return redirect(url_for('evaluate', exam_id=exam_id))

@app.route('/faculty/results/<int:exam_id>/lock', methods=['POST'])
def lock(exam_id):
    query = "UPDATE exams SET Status='Evaluated' WHERE Exam_ID=%s"
    mycursor.execute(query, (exam_id,))
    mydb.commit()
    return redirect(url_for('facultyResults'))


@app.route('/faculty/results/<int:exam_id>/delete/<int:student_id>', methods=['POST'])
def delete_student_result(exam_id, student_id):
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
    query = "SELECT results.Result_ID,results.Student_ID,CONCAT(students.First_Name,' ',students.Middle_Name,' ',students.Last_Name) AS Name,results.Marks_Obtained,results.Grade from results INNER JOIN students ON results.Student_ID=students.Student_ID INNER JOIN courses on results.Course_ID=courses.Course_ID WHERE results.Exam_ID=%s;"
    mycursor.execute(query, (exam_id,))
    results = mycursor.fetchall()
    query="SELECT DISTINCT courses.Course_Name, courses.Credits FROM courses INNER JOIN results ON results.Course_ID=courses.Course_ID WHERE results.Exam_ID=%s;"
    mycursor.execute(query,(exam_id,))  
    course=mycursor.fetchall()[0]
    return render_template('view_result.html', results=results, exam_id=exam_id,course=course)



@app.route('/faculty/results')
def facultyResults():
    query = "SELECT * FROM exams WHERE Course_ID=%s and Status='Unevaluated';"
    mycursor.execute(query, (session['user'][9],))
    Exams_toEvaluate = mycursor.fetchall()

    query = "SELECT * FROM exams WHERE Course_ID=%s and Status='Evaluated';"
    mycursor.execute(query, (session['user'][9],))
    Evaluated = mycursor.fetchall()

    # query = "SELECT * FROM results WHERE Course_ID=%s';"
    # mycursor.execute(query, (session['user'][9],))
    # results = mycursor.fetchall()
    print("i am here")
    return render_template('results.html', results=None, Exams_toEvaluate=Exams_toEvaluate, Evaluated=Evaluated)

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