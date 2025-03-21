import mysql.connector

def create_database_and_tables():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        cursor = connection.cursor()

        # Create database if it does not exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS `University Management System`;")
        cursor.execute("USE `University Management System`;")

        # Create tables if they do not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            Student_ID INT AUTO_INCREMENT PRIMARY KEY,
            First_Name VARCHAR(255) NOT NULL,
            Middle_Name VARCHAR(255),
            Last_Name VARCHAR(255) NOT NULL,
            Street VARCHAR(255) NOT NULL,
            District VARCHAR(255) NOT NULL,
            State VARCHAR(255) NOT NULL DEFAULT 'Nepal',
            Country VARCHAR(255) NOT NULL,
            Gender ENUM('Male', 'Female', 'Others') NOT NULL,
            Date_of_Birth DATE NOT NULL,
            Email VARCHAR(255) UNIQUE NOT NULL CHECK (Email LIKE '%@%'),
            College_Email VARCHAR(255) UNIQUE NOT NULL CHECK (College_Email LIKE '%@thapar.edu'),
            `Password` VARCHAR(255) NOT NULL CHECK (LENGTH(`Password`) >= 8),
            Enrollment_Year YEAR DEFAULT YEAR(CURRENT_DATE),
            Graduation_Year YEAR GENERATED ALWAYS AS (Enrollment_Year + 4) VIRTUAL,
            Status ENUM('Pending', 'Enrolled', 'Graduated', 'Restricted') NOT NULL DEFAULT 'Pending'
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            Course_ID VARCHAR(13) PRIMARY KEY,
            Course_Name VARCHAR(55) NOT NULL UNIQUE,
            Semester ENUM('1', '2', '3', '4', '5', '6', '7', '8') NOT NULL,
            Credits FLOAT NOT NULL,
            Price FLOAT NOT NULL DEFAULT 0
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_phone_no (
            Student_ID INT NOT NULL,
            Phone VARCHAR(14) NOT NULL,
            CONSTRAINT PRIMARY KEY (Student_ID, Phone),
            CONSTRAINT FK_Student FOREIGN KEY (Student_ID) REFERENCES students(Student_ID) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS enrollment (
            Student_ID INT NOT NULL,
            Course_ID VARCHAR(13) NOT NULL,
            Enrolled_IN DATE,
            FOREIGN KEY (Student_ID) REFERENCES students(Student_ID) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (Course_ID) REFERENCES courses(Course_ID) ON DELETE CASCADE ON UPDATE CASCADE,
            PRIMARY KEY (Student_ID, Course_ID)
        );
        """)


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            Exam_ID INT PRIMARY KEY AUTO_INCREMENT,
            Course_ID VARCHAR(13),
            Exam_Date DATE DEFAULT CURRENT_DATE NOT NULL,
            Exam_Duration FLOAT NOT NULL,
            Exam_Type ENUM ('Mid Semester Test', 'End Semester Test', 'Quiz-1', 'Quiz-2', 'Lab Evaluation I', 'Lab Evaluation II', 'Others') NOT NULL,
            Venue VARCHAR(61) NOT NULL,
            Status ENUM('Unevaluated','Evaluated','Locked') NOT NULL,
            CONSTRAINT UNIQUE(Course_ID, Exam_Type),
            FOREIGN KEY (Course_ID) REFERENCES courses(Course_ID) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fees (
            Fee_ID INT PRIMARY KEY AUTO_INCREMENT,
            Student_ID INT,
            Exam_ID INT,
            Course_ID VARCHAR(13),
            Amount FLOAT NOT NULL,
            Issued_Date DATE NOT NULL DEFAULT CURRENT_DATE,
            Type ENUM("Registration Fees","Course Registration","Exam Fee") NOT NULL,
            Payment_Date DATE,
            Status ENUM('Pending','Paid') DEFAULT 'Pending',
            Payment_ID VARCHAR(13),
            FOREIGN KEY (Student_ID) REFERENCES students(Student_ID) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (Exam_ID) REFERENCES exams(Exam_ID) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (Course_ID) REFERENCES courses(Course_ID) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS takes_exams (
            Student_ID INT NOT NULL,
            Exam_ID INT NOT NULL,
            Status ENUM('Unevaluated','Evaluated','Locked') DEFAULT 'Unevaluated',
            FOREIGN KEY (Student_ID) REFERENCES students(Student_ID) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (Exam_ID) REFERENCES exams(Exam_ID) ON DELETE CASCADE ON UPDATE CASCADE,
            PRIMARY KEY (Student_ID, Exam_ID)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS department (
            Department_ID VARCHAR(7) PRIMARY KEY,
            Department_Name VARCHAR(255) NOT NULL,
            Head_of_Department INT,
            CONSTRAINT UNIQUE (Department_Name, Department_ID)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            Faculty_ID INT PRIMARY KEY AUTO_INCREMENT,
            First_Name VARCHAR(255) NOT NULL,
            Middle_Name VARCHAR(255),
            Last_Name VARCHAR(255) NOT NULL,
            Date_of_Joining DATE NOT NULL DEFAULT CURRENT_DATE,
            Designation VARCHAR(32) NOT NULL,
            Mail VARCHAR(32) NOT NULL,
            Official_Mail VARCHAR(32) NOT NULL,
            Password VARCHAR(255) NOT NULL,
            Course_ID VARCHAR(13) NOT NULL,
            Department_ID VARCHAR(7) NOT NULL,
            Status ENUM('Pending', 'Active') DEFAULT 'Pending',
            FOREIGN KEY (Course_ID) REFERENCES courses(Course_ID) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (Department_ID) REFERENCES department(Department_ID) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        cursor.execute("""
        ALTER TABLE department
        ADD CONSTRAINT FK_Head_of_Department
        FOREIGN KEY (Head_of_Department) REFERENCES faculty(Faculty_ID)
        ON DELETE SET NULL
        ON UPDATE CASCADE;
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty_phone_no (
            Faculty_ID INT NOT NULL,
            Phone VARCHAR(14) NOT NULL,
            CONSTRAINT PRIMARY KEY (Faculty_ID, Phone),
            CONSTRAINT FK_Faculty FOREIGN KEY (Faculty_ID) REFERENCES faculty(Faculty_ID) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            Result_ID INT PRIMARY KEY AUTO_INCREMENT,
            Exam_ID INT NOT NULL,
            Student_ID INT NOT NULL,
            Course_ID VARCHAR(13) NOT NULL,
            Marks_Obtained FLOAT,
            Grade ENUM('A', 'A-', 'B', 'B-', 'C', 'C-', 'D', 'E'),
            Status ENUM('Unevaluated','Evaluated','Locked') DEFAULT 'Unevaluated',
            FOREIGN KEY (Exam_ID) REFERENCES exams(Exam_ID) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (Student_ID) REFERENCES students(Student_ID) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (Course_ID) REFERENCES courses(Course_ID) ON DELETE CASCADE ON UPDATE CASCADE,
            UNIQUE (Exam_ID, Student_ID, Course_ID)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            Admin_ID INT PRIMARY KEY AUTO_INCREMENT,
            User_Name VARCHAR(255) NOT NULL,
            Email VARCHAR(255) NOT NULL UNIQUE,
            Password VARCHAR(255) NOT NULL
        );
        """)




        # Insert initial data into admin table
        cursor.execute("""
        INSERT INTO admin (User_Name, Email, Password) VALUES
        ('admin', 'admin@thapar.edu', 'admin@tiet');
        """)

        # Insert initial data into courses table
        cursor.execute("""
        INSERT INTO courses (Course_ID, Course_Name, Semester, Credits) VALUES
        ('UCB008', 'APPLIED CHEMISTRY', 1, 4.5),
        ('UTA003', 'COMPUTER PROGRAMMING', 1, 4.0),
        ('UES013', 'ELECTRICAL & ELECTRONICS ENGINEERING', 1, 4.5),
        ('UEN002', 'ENERGY AND ENVIRONMENT', 1, 3.0),
        ('UMA010', 'MATHEMATICS – I', 1, 3.5),
        ('UES009', 'MECHANICS', 1, 2.5),
        ('UPH004', 'APPLIED PHYSICS', 2, 4.5),
        ('UTA018', 'OBJECT ORIENTED PROGRAMMING', 2, 4.0),
        ('UTA026', 'MANUFACTURING PROCESS', 2, 3.0),
        ('UTA015', 'ENGINEERING DRAWING', 2, 4.0),
        ('UHU003', 'PROFESSIONAL COMMUNICATION', 2, 3.0),
        ('UMA004', 'MATHEMATICS – II', 2, 3.5),
        ('UCS303', 'OPERATING SYSTEMS', 3, 4.0),
        ('UCS405', 'DISCRETE MATHEMATICAL STRUCTURES', 3, 3.5),
        ('UCS301', 'DATA STRUCTURES', 3, 4.0),
        ('UCS510', 'COMPUTER ARCHITECTURE AND ORGANIZATION', 3, 3.0),
        ('UMA011', 'NUMERICAL ANALYSIS', 3, 4.0),
        ('UCS411', 'ARTIFICIAL INTELLIGENCE', 4, 4.0),
        ('UCS415', 'DESIGN AND ANALYSIS OF ALGORITHMS', 4, 4.0),
        ('UCS310', 'DATABASE MANAGEMENT SYSTEMS', 4, 4.0),
        ('UCS503', 'SOFTWARE ENGINEERING', 4, 4.0),
        ('UCS414', 'COMPUTER NETWORKS', 4, 3.0),
        ('UMA035', 'OPTIMIZATION TECHNIQUES', 4, 4.0),
        ('UML501', 'MACHINE LEARNING', 5, 4.0),
        ('UCS410', 'PROBABILITY AND STATISTICS', 5, 4.0),
        ('UCS531', 'CLOUD COMPUTING', 5, 3.0),
        ('UCS413', 'NETWORK PROGRAMMING', 5, 3.0),
        ('PE501', 'ELECTIVE-I', 5, 3.0),
        ('GE501', 'GENERIC ELECTIVE', 5, 2.0),
        ('UCS701', 'THEORY OF COMPUTATION', 6, 3.5),
        ('UCS505', 'COMPUTER GRAPHICS', 6, 4.0),
        ('UCS619', 'QUANTUM COMPUTING', 6, 4.0),
        ('PE601', 'ELECTIVE-II', 6, 3.0),
        ('PE602', 'ELECTIVE-III', 6, 3.0),
        ('UCS797', 'CAPSTONE PROJECT (STARTS)', 6, 0.0),
        ('UCS802', 'COMPILER CONSTRUCTION', 7, 4.0),
        ('UHU005', 'HUMANITIES FOR ENGINEERS', 7, 3.0),
        ('UCS712', 'COGNITIVE COMPUTING', 7, 2.0),
        ('PE701', 'ELECTIVE-IV', 7, 3.0),
        ('UCS898', 'PROJECT SEMESTER', 8, 15.0),
        ('UCS813', 'SOCIAL NETWORK ANALYSIS', 8, 3.0),
        ('UCS806', 'ETHICAL HACKING', 8, 4.0),
        ('UCS899', 'PROJECT', 8, 8.0),
        ('UCS900', 'START-UP SEMESTER', 8, 15.0);
        """)

        connection.commit()
        print("Database and tables created successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_database_and_tables()