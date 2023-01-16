import mysql.connector
import environ

env = environ.Env()
environ.Env.read_env()

connection = mysql.connector.connect(
  host=env("MYSQL_HOST"),
  user=env("MYSQL_USER"),
  password=env("MYSQL_PASSWORD"),
  database=env("MYSQL_DATABASE"),
  auth_plugin='mysql_native_password'
)

cursor= connection.cursor()
#Create tables

cursor.execute("""
CREATE TABLE IF NOT EXISTS Database_Managers (
  `username` VARCHAR(15) NOT NULL,
  `password` TEXT NOT NULL,
  PRIMARY KEY (`username`)
  )
CHECKSUM = 1
MAX_ROWS = 4;
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS User (
username varchar(200) PRIMARY KEY,
password TEXT NOT NULL
);""")



cursor.execute("""
CREATE TABLE IF NOT EXISTS Departments (
  `department_id` VARCHAR(5) NOT NULL,
  `department_name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`department_id`),
  UNIQUE INDEX `department_id_UNIQUE` (`department_id` ASC) VISIBLE,
  UNIQUE INDEX `department_name_UNIQUE` (`department_name` ASC) VISIBLE);""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Users (
  username VARCHAR(15) NOT NULL,
  password TEXT NOT NULL,
  name VARCHAR(45) NOT NULL,
  surname VARCHAR(45) NOT NULL,
  email VARCHAR(45) NOT NULL,
  department_id VARCHAR(45) NOT NULL,
  PRIMARY KEY (`username`),
  INDEX department_id_idx (department_id ASC) VISIBLE,
  CONSTRAINT department_id
    FOREIGN KEY (department_id)
    REFERENCES Departments(department_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE);""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Students(
  students_id INT NOT NULL,
  students_username VARCHAR(15) NOT NULL,
  total_credits INT DEFAULT '0',
  GPA FLOAT DEFAULT '0.0',
  PRIMARY KEY (students_id),
  UNIQUE INDEX students_id_UNIQUE (students_id ASC) VISIBLE,
  UNIQUE INDEX username_UNIQUE (students_username ASC) VISIBLE,
  CONSTRAINT
    FOREIGN KEY (students_username)
    REFERENCES Users(username)
    ON DELETE CASCADE
    ON UPDATE CASCADE)""")
    
cursor.execute("""
CREATE TABLE IF NOT EXISTS Instructors (
  `instructor_username` VARCHAR(15) NOT NULL,
  `title` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`instructor_username`),
  CONSTRAINT `username1`
    FOREIGN KEY (`instructor_username`)
    REFERENCES `mydb`.`Users` (`username`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Classrooms(
  `classroom_id` VARCHAR(15) NOT NULL,
  `campus` VARCHAR(45) NOT NULL,
  `classroom_capacity` INT NOT NULL,
  PRIMARY KEY (`classroom_id`))""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Courses(
  `course_id` VARCHAR(15) NOT NULL,
  `name` VARCHAR(45) NULL,
  `instructor_username` VARCHAR(15) NOT NULL,
  `credits` INT NULL,
  `quota` INT NULL,
  `slot` INT NULL,
  PRIMARY KEY (`course_id`),
  FOREIGN KEY(`instructor_username`) REFERENCES `mydb`.`Instructors` (`instructor_username`) ON DELETE CASCADE ON UPDATE CASCADE,
  UNIQUE INDEX `course_id_UNIQUE` (`course_id` ASC) VISIBLE,
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE,
  INDEX `slot_idx` (`slot` ASC) VISIBLE)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Delivered_in(
  `classroom_id` VARCHAR(15) NOT NULL,
  `slot` INT NOT NULL,
  `course_id` VARCHAR(15) NOT NULL,
  UNIQUE INDEX `course_id_idx` (`course_id` ASC) VISIBLE,
  CONSTRAINT `course_id`
    FOREIGN KEY (`course_id`)
    REFERENCES `mydb`.`Courses` (`course_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    CONSTRAINT PK_Delivered_in
		PRIMARY KEY (`classroom_id`, `slot`),
  CONSTRAINT `classroom_id`
    FOREIGN KEY (`classroom_id`)
    REFERENCES `mydb`.`Classrooms` (`classroom_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS Added_Courses(
  `student_id` INT NOT NULL,
  `course_id` VARCHAR(45) NOT NULL,
  INDEX `student_id_idx` (`student_id` ASC) VISIBLE,
  INDEX `course_id_idx` (`course_id` ASC) VISIBLE,
    FOREIGN KEY (`student_id`)
    REFERENCES `mydb`.`Students` (`students_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

    FOREIGN KEY (`course_id`)
    REFERENCES `mydb`.`Courses` (`course_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    
    CONSTRAINT PK_Added_Courses PRIMARY KEY (`student_id`, `course_id`))""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Prerequisites(
  `primary_course_id` VARCHAR(15) NOT NULL,
  `pre_course_id` VARCHAR(15) NOT NULL,
  INDEX `course_id_idx` (`primary_course_id` ASC, `pre_course_id` ASC) VISIBLE,
  CONSTRAINT `pri_course_id`
    FOREIGN KEY (primary_course_id)
    REFERENCES `mydb`.`Courses` (`course_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `prev_course_id`
    FOREIGN KEY(`pre_course_id`)
    REFERENCES `mydb`.`Courses` (`course_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT PK_Prereq PRIMARY KEY(`primary_course_id`, `pre_course_id`)
    )""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Grades(
  `student_id` INT NOT NULL,
  `course_id` VARCHAR(15) NOT NULL,
  `grade` FLOAT NOT NULL,
  
  INDEX `course_id_idx` (`course_id` ASC) VISIBLE,
  CONSTRAINT PK_Grades PRIMARY KEY (`student_id`, `course_id`),
  CONSTRAINT `a_student_id`
    FOREIGN KEY (`student_id`)
    REFERENCES `mydb`.`Students` (`students_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `a_course_id`
    FOREIGN KEY (`course_id`)
    REFERENCES `mydb`.`Courses` (`course_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)""")









cursor.execute("""DROP PROCEDURE CreateStudent;""")
cursor.execute("""DROP PROCEDURE CreateInstructor;""")
cursor.execute("""DROP PROCEDURE CreateUser;""")
cursor.execute("""DROP PROCEDURE DeleteStudent;""")
cursor.execute("""DROP PROCEDURE updateTitle;""")
cursor.execute("""DROP PROCEDURE viewGrades;""")
cursor.execute("""DROP PROCEDURE viewCourses;""")
cursor.execute("""DROP PROCEDURE viewGradeAverage;""")
cursor.execute("""DROP PROCEDURE viewAvailableClassrooms;""")
cursor.execute("""DROP PROCEDURE addCourses;""")
cursor.execute("""DROP PROCEDURE addPrerequisite;""")
cursor.execute("""DROP PROCEDURE viewStudentsTakenCourse;""")
cursor.execute("""DROP PROCEDURE updateCourseName;""")
cursor.execute("""DROP PROCEDURE giveGrade;""")
cursor.execute("""DROP PROCEDURE s_addCourse;""")
cursor.execute("""DROP PROCEDURE filterCourses;""")
cursor.execute("""DROP TRIGGER DeliveredInInsert;""")
cursor.execute("""DROP TRIGGER ArrangeCredits;""")

cursor.execute(""" 
CREATE TRIGGER DeliveredInInsert
BEFORE INSERT ON Delivered_in
FOR EACH ROW
BEGIN
    IF (SELECT Distinct Courses.quota FROM Courses, Delivered_in WHERE Courses.course_id = new.course_id) > 
    (SELECT Distinct Classrooms.classroom_capacity FROM Classrooms, Delivered_in
    WHERE new.classroom_id = Classrooms.classroom_id) 
    THEN SIGNAL SQLSTATE '45000';
    END IF;
END;
""")
cursor.execute("""
Create Trigger ArrangeCredits 
AFTER INSERT ON Grades
FOR EACH ROW
UPDATE Students
SET total_credits = total_credits + (SELECT Distinct Courses.credits FROM Grades, Courses WHERE new.course_id = Courses.course_id), GPA = (((total_credits- (SELECT Distinct Courses.credits FROM Grades, Courses WHERE new.course_id = Courses.course_id)) * GPA) + new.grade* (SELECT Distinct Courses.credits FROM Grades, Courses WHERE new.course_id = Courses.course_id))/total_credits
WHERE new.student_id = Students.students_id;
""")

cursor.execute("""
CREATE PROCEDURE CreateUser(IN username VARCHAR(15), IN password TEXT, IN name VARCHAR(45), IN surname VARCHAR(45), IN email VARCHAR(45), IN department_id VARCHAR(45))
BEGIN
INSERT INTO Users VALUES (username, password, name, surname, email, department_id);
END;
""")

cursor.execute("""
CREATE PROCEDURE CreateStudent(IN students_id INT, IN students_username VARCHAR(15))
BEGIN
INSERT INTO Students(students_id, students_username) VALUES (students_id, students_username);
END;
""")
cursor.execute("""
CREATE PROCEDURE CreateInstructor(IN instructor_username VARCHAR(15),IN title VARCHAR(45))
BEGIN
INSERT INTO Instructors VALUES (instructor_username, title);
END;
""")

cursor.execute("""
CREATE PROCEDURE DeleteStudent(IN students_id INT)
BEGIN
DELETE Users, Students
FROM Users
INNER JOIN Students ON Users.username = Students.students_username
WHERE Students.students_id = students_id;
END;
""")

cursor.execute("""
CREATE PROCEDURE updateTitle(IN instructor_username VARCHAR(15), IN title VARCHAR(45))
BEGIN
UPDATE Instructors 
SET 
    Instructors.title = title
WHERE
    Instructors.instructor_username = instructor_username;
END;
""")

cursor.execute("""
CREATE PROCEDURE viewGrades(IN students_id INT)
BEGIN
SELECT Courses.course_id, Courses.name, Grades.grade
FROM Grades, Courses
WHERE Courses.course_id = Grades.course_id and Grades.student_id = students_id;
END;
""")

cursor.execute("""
CREATE PROCEDURE viewCourses(IN instructor_username VARCHAR(15))
BEGIN
SELECT Courses.course_id, Courses.name, Classrooms.classroom_id, Classrooms.campus, Delivered_in.slot
FROM Courses, Classrooms, Delivered_in
WHERE Courses.course_id = Delivered_in.course_id and Classrooms.classroom_id = Delivered_in.classroom_id and Courses.instructor_username = instructor_username;
END;
""")

cursor.execute("""
CREATE PROCEDURE viewGradeAverage(IN course_id VARCHAR(15))
BEGIN
SELECT Grades.course_id, Courses.name,  SUM(Grades.grade)/COUNT(Courses.course_id) AS Grades_Average
FROM Grades
JOIN Courses ON Grades.course_id = Courses.course_id and Courses.course_id = course_id
GROUP BY Courses.course_id;
END;
""")


cursor.execute("""
CREATE PROCEDURE viewAvailableClassrooms(IN slot INT)
BEGIN
SELECT Distinct Classrooms.classroom_id, Classrooms.campus, Classrooms.classroom_capacity FROM Classrooms, Delivered_in 
WHERE Classrooms.classroom_id = Delivered_in.classroom_id and Delivered_in.slot != slot;
END;
""")

cursor.execute("""
CREATE PROCEDURE addCourses(IN course_id VARCHAR(15), IN course_name VARCHAR(45),IN instructors_username VARCHAR(15),IN credits INT, IN classroom_id VARCHAR(15), IN slot INT, IN quota INT, IN department_id VARCHAR(15))
BEGIN
INSERT INTO Courses VALUES (course_id, course_name, instructors_username, credits, quota, slot);
INSERT INTO Delivered_in VALUES (classroom_id, slot, course_id);
END;
""")

cursor.execute("""
CREATE PROCEDURE addPrerequisite(IN primary_course_id VARCHAR(15), IN prev_course_id VARCHAR(15))
BEGIN
INSERT INTO Prerequisites VALUES (primary_course_id, prev_course_id);
END;
""")

cursor.execute("""
CREATE PROCEDURE viewStudentsTakenCourse(IN course_id VARCHAR(15),IN _username VARCHAR(15))
BEGIN
SELECT Students.students_username, Students.students_id, Users.email, Users.name, Users.surname
FROM Students, Users, Courses, Added_Courses
WHERE Added_Courses.course_id = course_id and Courses.instructor_username = _username and 
Courses.course_id = Added_Courses.course_id and
Added_Courses.student_id = Students.students_id and Users.username = Students.students_username;
END;
""")

cursor.execute("""
CREATE PROCEDURE updateCourseName(IN course_id VARCHAR(15),IN course_name VARCHAR(45), IN _username VARCHAR(15))
BEGIN
UPDATE Courses 
SET 
    Courses.name = course_name
WHERE
    Courses.instructor_username = _username and Courses.course_id = course_id;
END;
""")

cursor.execute("""
CREATE PROCEDURE giveGrade(IN course_id VARCHAR(15),IN student_id INT, IN grade FLOAT)
BEGIN
INSERT INTO Grades VALUES (student_id, course_id, grade);
END;
""")

cursor.execute("""
CREATE PROCEDURE s_addCourse(IN _course_id VARCHAR(15), IN _student_id INT)
BEGIN
INSERT INTO Added_Courses(student_id, course_id) VALUES (_student_id, _course_id);
END;
""")

cursor.execute(""" 
CREATE PROCEDURE filterCourses(IN _department_id TEXT, IN _campus VARCHAR(15), IN _minimum_credits INT, IN _maximum_credits INT)
BEGIN
SELECT Courses.course_id FROM Courses, Users, Delivered_in, Classrooms
WHERE Courses.instructor_username = Users.username and
Users.department_id = _department_id and 
Courses.course_id = Delivered_in.course_id and
Delivered_in.classroom_id = Classrooms.classroom_id and
Classrooms.campus = _campus and
Courses.credits>=_minimum_credits and Courses.credits<=_maximum_credits;
END;
""")


connection.commit()