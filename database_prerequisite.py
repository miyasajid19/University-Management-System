import mysql.connector
import pymysql
connection = None
timeout = 10
def drop_database():
    try:
        global connection
        connection = pymysql.connect(
            charset="utf8mb4",
            connect_timeout=timeout,
            cursorclass=pymysql.cursors.DictCursor,
            host="mysql-182df993-miyasajid19.h.aivencloud.com",
            password="AVNS_ximKhtxOsk6on29jNTf",
            port=19571,
            user="avnadmin",
            write_timeout=timeout,
        )
        cursor = connection.cursor()
        cursor.execute("DROP DATABASE IF EXISTS `University Management System`;")
        connection.commit()
        print("Database dropped successfully.")
    except pymysql.Error as err:
        print(f"Error: {err}")
    finally:
        if connection:
            cursor.close()
            connection.close()
def create_database():
    try:
        global connection
        connection = pymysql.connect(
            charset="utf8mb4",
            connect_timeout=timeout,
            cursorclass=pymysql.cursors.DictCursor,
            host="mysql-182df993-miyasajid19.h.aivencloud.com",
            password="AVNS_ximKhtxOsk6on29jNTf",
            read_timeout=timeout,
            port=19571,
            user="avnadmin",
            write_timeout=timeout,
            )
        cursor = connection.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS `University Management System`;")
        cursor.execute("USE `University Management System`;")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            Admin_ID INT PRIMARY KEY AUTO_INCREMENT,
            User_Name VARCHAR(255) NOT NULL,
            Email VARCHAR(255) NOT NULL UNIQUE,
            Password VARCHAR(255) NOT NULL
        );
        """)
        connection.commit()

        cursor.execute("""
        INSERT INTO admin (User_Name, Email, Password) VALUES
        ('admin', 'admin@thapar.edu', 'admin@tiet');
        """)
        connection.commit()
        cursor.execute("SELECT * FROM admin;")
        result = cursor.fetchall()
        print("Admin table created and initial data inserted successfully.")
        for row in result:
            print(row)
    except pymysql.Error as err:
        print(f"Error: {err}")
    finally:
        if connection:
            cursor.close()
            connection.close()

def create_tables():
    try:
        connection = pymysql.connect(
        charset="utf8mb4",
        connect_timeout=timeout,
        cursorclass=pymysql.cursors.DictCursor,
        db="University Management System",
        host="mysql-182df993-miyasajid19.h.aivencloud.com",
        password="AVNS_ximKhtxOsk6on29jNTf",
        read_timeout=timeout,
        port=19571,
        user="avnadmin",
        write_timeout=timeout,
        )
        cursor = connection.cursor()

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
            Password VARCHAR(255) NOT NULL CHECK (LENGTH(Password) >= 8),
            Enrollment_Year YEAR NOT NULL,
            Graduation_Year YEAR NOT NULL DEFAULT (Enrollment_Year + 4),
            Status ENUM('Pending', 'Enrolled', 'Graduated', 'Restricted') NOT NULL DEFAULT 'Pending'
        );
        """)
        print("Students table created successfully.")
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
        print("Student phone number table created successfully.")
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
        print("Enrollment table created successfully.")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            Exam_ID INT PRIMARY KEY AUTO_INCREMENT,
            Course_ID VARCHAR(13),
            Exam_Date DATE NOT NULL,
            Exam_Duration FLOAT NOT NULL,
            Exam_Type ENUM ('Mid Semester Test', 'End Semester Test', 'Quiz-1', 'Quiz-2', 'Lab Evaluation I', 'Lab Evaluation II', 'Others') NOT NULL,
            Venue VARCHAR(61) NOT NULL,
            Status ENUM('Unevaluated','Evaluated','Locked') NOT NULL,
            CONSTRAINT UNIQUE(Course_ID, Exam_Type),
            FOREIGN KEY (Course_ID) REFERENCES courses(Course_ID) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)
        print("Exams table created successfully.")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fees (
            Fee_ID INT PRIMARY KEY AUTO_INCREMENT,
            Student_ID INT,
            Exam_ID INT,
            Course_ID VARCHAR(13),
            Amount FLOAT NOT NULL,
            Issued_Date DATE NOT NULL DEFAULT (CURRENT_DATE),
            Type ENUM('Registration Fees','Course Registration','Exam Fee') NOT NULL,
            Payment_Date DATE,
            Status ENUM('Pending','Paid') DEFAULT 'Pending',
            Payment_ID VARCHAR(13),
            FOREIGN KEY (Student_ID) REFERENCES students(Student_ID) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (Exam_ID) REFERENCES exams(Exam_ID) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (Course_ID) REFERENCES courses(Course_ID) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)
        print("Fees table created successfully.")
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
        print("Takes exams table created successfully.")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS department (
            Department_ID VARCHAR(7) PRIMARY KEY,
            Department_Name VARCHAR(255) NOT NULL,
            Head_of_Department INT,
            UNIQUE (Department_Name)
        );
        """)
        print("Department table created successfully.")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            Faculty_ID INT PRIMARY KEY AUTO_INCREMENT,
            First_Name VARCHAR(255) NOT NULL,
            Middle_Name VARCHAR(255),
            Last_Name VARCHAR(255) NOT NULL,
            Date_of_Joining DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
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
        print("Faculty table created successfully.")
        cursor.execute("""
        ALTER TABLE department
        ADD CONSTRAINT FK_Head_of_Department
        FOREIGN KEY (Head_of_Department) REFERENCES faculty(Faculty_ID)
        ON DELETE SET NULL
        ON UPDATE CASCADE;
        """)
        print("Foreign key constraint for Head_of_Department added successfully.")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty_phone_no (
            Faculty_ID INT NOT NULL,
            Phone VARCHAR(14) NOT NULL,
            CONSTRAINT PRIMARY KEY (Faculty_ID, Phone),
            CONSTRAINT FK_Faculty FOREIGN KEY (Faculty_ID) REFERENCES faculty(Faculty_ID) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)
        print("Faculty phone number table created successfully.")
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
        print("Results table created successfully.")
        connection.commit()
        print("Tables created successfully.")
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("Tables in the database:")
        for index, table in enumerate(tables):
            print(table['Tables_in_University Management System'], index+1)
        cursor.execute("SELECT * FROM admin;")
        print("\n\n\n\nAdmin table data:")
        result = cursor.fetchall()
        print("Admin table data:")
        for row in result:
            print(row)
        print("\n"*5)
    except pymysql.Error as err:
        print(f"Error: {err}")
    finally:
        if connection:
            cursor.close()
            connection.close()

def insert_initial_data():
    try:
        connection = pymysql.connect(
            charset="utf8mb4",
            connect_timeout=timeout,
            cursorclass=pymysql.cursors.DictCursor,
            db="University Management System",
            host="mysql-182df993-miyasajid19.h.aivencloud.com",
            password="AVNS_ximKhtxOsk6on29jNTf",
            read_timeout=timeout,
            port=19571,
            user="avnadmin",
            write_timeout=timeout,
            )
        cursor = connection.cursor()
        
        # Insert department data first
        cursor.execute("""
        INSERT INTO department (Department_ID, Department_Name, Head_of_Department) VALUES
        ('CSE', 'Computer Science and Engineering', NULL),
        ('ECE', 'Electronics and Communication Engineering', NULL),
        ('ME', 'Mechanical Engineering', NULL),
        ('CE', 'Civil Engineering', NULL),
        ('EE', 'Electrical Engineering', NULL);
        """)

        # Now insert courses data
        cursor.execute("""
        INSERT INTO courses (Course_ID, Course_Name, Semester, Credits, Price) VALUES
        ('UCB1234', 'ADVANCED CHEMISTRY', 1, 4.5, 1200),
        ('UTA5678', 'ADVANCED PROGRAMMING', 1, 4.0, 1500),
        ('UES9101', 'ELECTRICAL ENGINEERING', 1, 4.5, 1300),
        ('UEN2345', 'ENVIRONMENTAL SCIENCE', 1, 3.0, 1100),
        ('UMA6789', 'MATHEMATICS – III', 1, 3.5, 1400),
        ('UES3456', 'ENGINEERING MECHANICS', 1, 2.5, 1000),
        ('UPH7890', 'PHYSICS', 2, 4.5, 1200),
        ('UTA1234', 'DATA STRUCTURES', 2, 4.0, 1500),
        ('UTA5677', 'MANUFACTURING TECHNOLOGY', 2, 3.0, 1300),
        ('UTA9101', 'ENGINEERING GRAPHICS', 2, 4.0, 1400),
        ('UHU2345', 'COMMUNICATION SKILLS', 2, 3.0, 1100),
        ('UMA6790', 'MATHEMATICS – IV', 2, 3.5, 1200),
        ('UCS3456', 'OPERATING SYSTEMS', 3, 4.0, 1500),
        ('UCS7890', 'DISCRETE MATHEMATICS', 3, 3.5, 1300),
        ('UCS123', 'ALGORITHMS', 3, 4.0, 1400),
        ('UCS678', 'COMPUTER ARCHITECTURE', 3, 3.0, 1200),
        ('UMA9101', 'NUMERICAL METHODS', 3, 4.0, 1500),
        ('UCS2345', 'ARTIFICIAL INTELLIGENCE', 4, 4.0, 1600),
        ('UCS6789', 'DATABASE SYSTEMS', 4, 4.0, 1500),
        ('UCS3457', 'SOFTWARE ENGINEERING', 4, 4.0, 1400),
        ('UCS7891', 'NETWORKS', 4, 3.0, 1300),
        ('UMA1234', 'OPTIMIZATION', 4, 4.0, 1200),
        ('UML5678', 'MACHINE LEARNING', 5, 4.0, 1600),
        ('UCS9101', 'PROBABILITY AND STATISTICS', 5, 4.0, 1500),
        ('UCS2346', 'CLOUD COMPUTING', 5, 3.0, 1400),
        ('UCS6780', 'NETWORK PROGRAMMING', 5, 3.0, 1300),
        ('PE1234', 'ELECTIVE-I', 5, 3.0, 1200),
        ('GE5678', 'GENERIC ELECTIVE', 5, 2.0, 1100),
        ('UCS9102', 'THEORY OF COMPUTATION', 6, 3.5, 1500),
        ('UCS2347', 'COMPUTER GRAPHICS', 6, 4.0, 1600),
        ('UCS6791', 'QUANTUM COMPUTING', 6, 4.0, 1500),
        ('PE3456', 'ELECTIVE-II', 6, 3.0, 1400),
        ('PE7890', 'ELECTIVE-III', 6, 3.0, 1300),
        ('UCS1234', 'CAPSTONE PROJECT', 6, 0.0, 1200),
        ('UCS5678', 'COMPILER DESIGN', 7, 4.0, 1600),
        ('UHU9101', 'ENGINEERING ETHICS', 7, 3.0, 1500),
        ('UCS013', 'COGNITIVE COMPUTING', 7, 2.0, 1400),
        ('PE6789', 'ELECTIVE-IV', 7, 3.0, 1300),
        ('UCS345', 'PROJECT SEMESTER', 8, 15.0, 2000),
        ('UCS7892', 'SOCIAL NETWORK ANALYSIS', 8, 3.0, 1500),
        ('UCS432', 'CYBER SECURITY', 8, 4.0, 1600),
        ('UCS786', 'FINAL PROJECT', 8, 8.0, 1800),
        ('UCS9103', 'START-UP SEMESTER', 8, 15.0, 2000);
        """)

        connection.commit()
        print("Initial data inserted successfully.")
    except pymysql.Error as err:
        print(f"Error: {err}")
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    # Execute the functions
    drop_database()
    create_database()
    create_tables()
    insert_initial_data()
