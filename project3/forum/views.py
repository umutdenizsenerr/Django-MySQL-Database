from cProfile import run
import email
from queue import Empty
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .forms import *
from .db_utils import run_statement
import hashlib

def index(req):
    #Logout the user if logged 
    if req.session:
        req.session.flush()
    
    isFailed=req.GET.get("fail",False) #Check the value of the GET parameter "fail"
    
    loginForm=UserLoginForm() #Use Django Form object to create a blank form for the HTML page




    return render(req,'loginIndex.html',{"login_form":loginForm,"action_fail":isFailed})


def login(req):
    #Retrieve data from the request body
    username=req.POST["username"]
    password=req.POST["password"]

    result=run_statement(f"SELECT * FROM Database_Managers WHERE username='{username}' and password='{password}';") #Run the query in DB

    if result: #If a result is retrieved
        req.session["username"]=username #Record username into the current session
        return HttpResponseRedirect('../forum/home') #Redirect user to home page
    else:
        return HttpResponseRedirect('../forum?fail=true')

def login_instructors(req):
    #Retrieve data from the request body
    username=req.POST["username"]
    password=req.POST["password"]

    result=run_statement(f"SELECT * FROM Instructors, Users WHERE Instructors.instructor_username = Users.username and Users.username='{username}' and password='{password}';") #Run the query in DB

    if result: #If a result is retrieved
        req.session["username"]=username #Record username into the current session
        return HttpResponseRedirect('../forum/home') #Redirect user to home page
    else:
        return HttpResponseRedirect('../forum?fail=true')

def login_students(req):
    #Retrieve data from the request body
    username=req.POST["username"]
    password=req.POST["password"]

    result=run_statement(f"SELECT * FROM Students, Users WHERE Students.students_username = Users.username and Users.username='{username}' and password='{password}';") #Run the query in DB

    if result: #If a result is retrieved
        req.session["username"]=username #Record username into the current session
        return HttpResponseRedirect('../forum/home') #Redirect user to home page
    else:
        return HttpResponseRedirect('../forum?fail=true')


def homePage(req):
    students = run_statement(f"SELECT Students.students_username AS username, Users.name, Users.surname, Users.email, Users.department_id, SUM(Courses.credits) AS completed_credits, SUM(Courses.credits*Grades.grade)/SUM(Courses.credits) AS GPA FROM Grades JOIN Courses ON Grades.course_id = Courses.course_id JOIN Students ON Students.students_id = Grades.student_id JOIN Users ON Students.students_username = Users.username GROUP BY student_id ORDER BY completed_credits ASC")
    instructors = run_statement(f"SELECT Instructors.instructor_username, Users.name, Users.surname, Users.email, Users.department_id, Instructors.title FROM Instructors, Users WHERE Instructors.instructor_username = Users.username;;") 
    username=req.session["username"] #Retrieve the username of the logged-in user
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
    all_courses = run_statement(f"SELECT Courses.course_id, Courses.name,Classrooms.classroom_id, Courses.slot, Courses.quota, (SELECT GROUP_CONCAT(Prerequisites.pre_course_id) FROM Prerequisites WHERE Prerequisites.primary_course_id = Courses.course_id) AS prerequisites FROM Courses, Departments, Classrooms, Users, Delivered_in WHERE Courses.instructor_username = Users.username and Departments.department_id = Users.department_id and Delivered_in.course_id = Courses.course_id and Classrooms.classroom_id = Delivered_in.classroom_id and Courses.instructor_username ='{username}' ORDER BY Courses.course_id ASC;")
    isStudent = run_statement(f"SELECT * FROM Students WHERE students_username='{username}';") 
    isInstructor = run_statement(f"SELECT * FROM Instructors WHERE instructor_username='{username}';") 
    isDepartmentManager=run_statement(f"SELECT * FROM Database_Managers WHERE username='{username}';") #Run the query in DB
    givenCourses = run_statement(f"SELECT Courses.course_id, Courses.name,Users.surname,Users.department_id, Courses.credits,Classrooms.classroom_id, Courses.slot, Courses.quota, (SELECT GROUP_CONCAT(Prerequisites.pre_course_id)  FROM Prerequisites WHERE Prerequisites.primary_course_id = Courses.course_id) AS prerequisites FROM Courses, Departments, Classrooms, Users, Delivered_in WHERE Courses.instructor_username = Users.username and Departments.department_id = Users.department_id and Delivered_in.course_id = Courses.course_id and Classrooms.classroom_id = Delivered_in.classroom_id and Courses.instructor_username = Users.username;")
    takenCourses = ""
    if isStudent:
        student_id = run_statement(f"SELECT Students.students_id FROM Students WHERE Students.students_username = '{username}'")
        takenCourses = run_statement(f"SELECT newtable.course_id, Courses.name ,newtable.grade FROM (SELECT * FROM Grades UNION ALL SELECT Added_Courses.student_id, Added_Courses.course_id, null as grade FROM Added_Courses) as newtable, Courses WHERE newtable.student_id = '{student_id[0][0]}' and newtable.course_id = Courses.course_id")

    return render(req,'userHome.html',{"action_fail":isFailed,"username":username,  "isDepartmentManager": isDepartmentManager, "students": students, "instructors": instructors, "isInstructor": isInstructor, "all_courses": all_courses, "isStudent": isStudent, "givenCourses": givenCourses, "takenCourses": takenCourses})

def addDatabase_Manager(name , password):
    hashed_password = hashlib.sha256('{password}'.encode('utf-8')).hexdigest()
    run_statement(f"INSERT INTO Database_Managers VALUES ('{name}', '{hashed_password}');")

def createStudent(req):
    #Retrieve data from the request body
    db_username = req.session["username"]
    result=run_statement(f"SELECT * FROM Database_Managers WHERE username='{db_username}'") #Run the query in DB

    if result:
        username=req.POST["username"]
        password=req.POST["password"]
        name=req.POST["name"]
        surname=req.POST["surname"]
        email=req.POST["email"]
        department_id=req.POST["department_id"]
        students_id=req.POST["students_id"]
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        try:
            run_statement(f"CALL CreateUser('{username}','{hashed_password}','{name}','{surname}','{email}','{department_id}')")
            run_statement(f"CALL CreateStudent('{students_id}','{username}')")

            return HttpResponseRedirect("../forum/home")
        except Exception as e:
            print(str(e))
            return HttpResponseRedirect('../forum/home?fail=true')
    else: 
        return HttpResponseRedirect('../forum/home?fail=true')

def createInstructor(req):
    #Retrieve data from the request body
    db_username = req.session["username"]
    result=run_statement(f"SELECT * FROM Database_Managers WHERE username='{db_username}'") #Run the query in DB

    if result:
        username=req.POST["username"]
        password=req.POST["password"]
        name=req.POST["name"]
        surname=req.POST["surname"]
        email=req.POST["email"]
        department_id=req.POST["department_id"]
        title=req.POST["title"]
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        
        if title == "Assistant Professor" or title == "Associate Professor" or title == "Professor":
            try:
                run_statement(f"CALL CreateUser('{username}','{hashed_password}','{name}','{surname}','{email}','{department_id}')")
                run_statement(f"CALL CreateInstructor('{username}','{title}')")
                return HttpResponseRedirect("../forum/home")
            except Exception as e:
                print(str(e))
                return HttpResponseRedirect('../forum/home?fail=true')
        else:
            return HttpResponseRedirect('../forum/home?fail=true')

    else: 
        return HttpResponseRedirect('../forum/home?fail=true')

def deleteStudent(req):
    db_username = req.session["username"]
    result=run_statement(f"SELECT * FROM Database_Managers WHERE username='{db_username}'") #Run the query in DB
    if result:
        students_id=req.POST["students_id"]
        try:
            run_statement(f"CALL DeleteStudent('{students_id}')")
            return HttpResponseRedirect("../forum/home")
        except Exception as e:
            print(str(e))
            return HttpResponseRedirect('../forum/home?fail=true')
    else:
            return HttpResponseRedirect('../forum/home?fail=true')

def updateTitle(req):
    instructor_username = req.POST["instructor_username"]
    title = req.POST["title"]
    if title == "Assistant Professor" or title == "Associate Professor" or title == "Professor":
        try:
            run_statement(f"CALL updateTitle('{instructor_username}', '{title}')")
            return HttpResponseRedirect("../forum/home")
        except Exception as e:
            print(str(e))
            return HttpResponseRedirect('../forum/home?fail=true')
    else:
        return HttpResponseRedirect('../forum/home?fail=true')

def viewGrades(req):
    
    students_id = req.POST["students_id"]
    try:
        grades = run_statement(f"CALL viewGrades('{students_id}')")
        students = run_statement(f"SELECT Students.students_username AS username, Users.name, Users.surname, Users.email, Users.department_id, SUM(Courses.credits) AS completed_credits, SUM(Courses.credits*Grades.grade)/SUM(Courses.credits) AS GPA FROM Grades JOIN Courses ON Grades.course_id = Courses.course_id JOIN Students ON Students.students_id = Grades.student_id JOIN Users ON Students.students_username = Users.username GROUP BY student_id ORDER BY completed_credits ASC")
        instructors = run_statement(f"SELECT Instructors.instructor_username, Users.name, Users.surname, Users.email, Users.department_id, Instructors.title FROM Instructors, Users WHERE Instructors.instructor_username = Users.username;;") 
        username=req.session["username"] #Retrieve the username of the logged-in user
        isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False

    
        isDepartmentManager=run_statement(f"SELECT * FROM Database_Managers WHERE username='{username}';") #Run the query in DB
        return render(req,'userHome.html',{"action_fail":isFailed,"username":username,  "isDepartmentManager": isDepartmentManager, "students": students, "instructors": instructors, "grades": grades})

    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../forum/home?fail=true')

def viewCourses(req):
    
    instructor_username = req.POST["instructor_username"]
    try:
        courses = run_statement(f"CALL viewCourses('{instructor_username}')")
        students = run_statement(f"SELECT Students.students_username AS username, Users.name, Users.surname, Users.email, Users.department_id, SUM(Courses.credits) AS completed_credits, SUM(Courses.credits*Grades.grade)/SUM(Courses.credits) AS GPA FROM Grades JOIN Courses ON Grades.course_id = Courses.course_id JOIN Students ON Students.students_id = Grades.student_id JOIN Users ON Students.students_username = Users.username GROUP BY student_id ORDER BY completed_credits ASC")
        instructors = run_statement(f"SELECT Instructors.instructor_username, Users.name, Users.surname, Users.email, Users.department_id, Instructors.title FROM Instructors, Users WHERE Instructors.instructor_username = Users.username;;") 
        username=req.session["username"] #Retrieve the username of the logged-in user
        isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False

    
        isDepartmentManager=run_statement(f"SELECT * FROM Database_Managers WHERE username='{username}';") #Run the query in DB
        return render(req,'userHome.html',{"action_fail":isFailed,"username":username,  "isDepartmentManager": isDepartmentManager, "students": students, "instructors": instructors, "courses": courses})

    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../forum/home?fail=true')

def viewGradeAverage(req):
    course_id = req.POST["course_id"]
    try:
        courses_grade_avg = run_statement(f"CALL viewGradeAverage('{course_id}')")
        students = run_statement(f"SELECT Students.students_username AS username, Users.name, Users.surname, Users.email, Users.department_id, SUM(Courses.credits) AS completed_credits, SUM(Courses.credits*Grades.grade)/SUM(Courses.credits) AS GPA FROM Grades JOIN Courses ON Grades.course_id = Courses.course_id JOIN Students ON Students.students_id = Grades.student_id JOIN Users ON Students.students_username = Users.username GROUP BY student_id ORDER BY completed_credits ASC")
        instructors = run_statement(f"SELECT Instructors.instructor_username, Users.name, Users.surname, Users.email, Users.department_id, Instructors.title FROM Instructors, Users WHERE Instructors.instructor_username = Users.username;;") 
        username=req.session["username"] #Retrieve the username of the logged-in user
        isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False

    
        isDepartmentManager=run_statement(f"SELECT * FROM Database_Managers WHERE username='{username}';") #Run the query in DB
        return render(req,'userHome.html',{"action_fail":isFailed,"username":username,  "isDepartmentManager": isDepartmentManager, "students": students, "instructors": instructors, "courses_grade_avg": courses_grade_avg})

    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../forum/home?fail=true')

def viewAvailableClassrooms(req):
    slot = req.POST["slot"]
    try:
        availableClassrooms = run_statement(f"CALL viewAvailableClassrooms('{slot}')")
        students = run_statement(f"SELECT Students.students_username AS username, Users.name, Users.surname, Users.email, Users.department_id, SUM(Courses.credits) AS completed_credits, SUM(Courses.credits*Grades.grade)/SUM(Courses.credits) AS GPA FROM Grades JOIN Courses ON Grades.course_id = Courses.course_id JOIN Students ON Students.students_id = Grades.student_id JOIN Users ON Students.students_username = Users.username GROUP BY student_id ORDER BY completed_credits ASC")
        instructors = run_statement(f"SELECT Instructors.instructor_username, Users.name, Users.surname, Users.email, Users.department_id, Instructors.title FROM Instructors, Users WHERE Instructors.instructor_username = Users.username;;") 
        
        username=req.session["username"] #Retrieve the username of the logged-in user
        isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False

        isInstructor = run_statement(f"SELECT * FROM Instructors WHERE instructor_username='{username}';") 
        isDepartmentManager=run_statement(f"SELECT * FROM Database_Managers WHERE username='{username}';") 

        return render(req,'userHome.html',{"action_fail":isFailed,"username":username,  "isDepartmentManager": isDepartmentManager, "students": students, "instructors": instructors,  "isInstructor": isInstructor, "availableClassrooms": availableClassrooms})

    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../forum/home?fail=true')

def addCourses(req):
    course_id = req.POST["course_id"]
    course_name = req.POST["course_name"]
    credits = req.POST["credits"]
    classroom_id = req.POST["classroom_id"]
    slot = req.POST["slot"]
    quota = req.POST["quota"]
    username=req.session["username"] #Retrieve the username of the logged-in user
    department_id = run_statement(f"SELECT Users.department_id FROM Instructors, Users WHERE Instructors.instructor_username = '{username}' and Instructors.instructor_username = Users.username ")
    try:
        run_statement(f"CALL addCourses('{course_id}', '{course_name}', '{username}','{credits}', '{classroom_id}', '{slot}', '{quota}', '{department_id[0][0]}')")
        return HttpResponseRedirect("../forum/home")
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../forum/home?fail=true')

def addPrerequisite(req):
    primary_course_id = req.POST["primary_course_id"]
    prev_course_id = req.POST["prev_course_id"]
    if primary_course_id > prev_course_id:
        try: 
            run_statement(f"CALL addPrerequisite('{primary_course_id}', '{prev_course_id}')")

            return HttpResponseRedirect("../forum/home")

        except Exception as e:
                print(str(e))
                return HttpResponseRedirect('../forum/home?fail=true')
    else:
        return HttpResponseRedirect('../forum/home?fail=true')

def viewStudentsTakenCourse(req):
    course_id = req.POST["course_id"]
    try:
        username=req.session["username"] #Retrieve the username of the logged-in user
        students_taken_course = run_statement(f"CALL viewStudentsTakenCourse('{course_id}', '{username}')")
        students = run_statement(f"SELECT Students.students_username AS username, Users.name, Users.surname, Users.email, Users.department_id, SUM(Courses.credits) AS completed_credits, SUM(Courses.credits*Grades.grade)/SUM(Courses.credits) AS GPA FROM Grades JOIN Courses ON Grades.course_id = Courses.course_id JOIN Students ON Students.students_id = Grades.student_id JOIN Users ON Students.students_username = Users.username GROUP BY student_id ORDER BY completed_credits ASC")
        instructors = run_statement(f"SELECT Instructors.instructor_username, Users.name, Users.surname, Users.email, Users.department_id, Instructors.title FROM Instructors, Users WHERE Instructors.instructor_username = Users.username;;") 
        
        isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
        all_courses = run_statement(f"SELECT Courses.course_id, Courses.name,Classrooms.classroom_id, Courses.slot, Courses.quota, (SELECT GROUP_CONCAT(Prerequisites.pre_course_id) FROM Prerequisites WHERE Prerequisites.primary_course_id = Courses.course_id) AS prerequisites FROM Courses, Departments, Classrooms, Users, Delivered_in WHERE Courses.instructor_username = Users.username and Departments.department_id = Users.department_id and Delivered_in.course_id = Courses.course_id and Classrooms.classroom_id = Delivered_in.classroom_id and Courses.instructor_username ='{username}' ORDER BY Courses.course_id ASC;")

        isInstructor = run_statement(f"SELECT * FROM Instructors WHERE instructor_username='{username}';") 
        isDepartmentManager=run_statement(f"SELECT * FROM Database_Managers WHERE username='{username}';") 

        return render(req,'userHome.html',{"action_fail":isFailed,"username":username,  "isDepartmentManager": isDepartmentManager, "students": students, "instructors": instructors,  "isInstructor": isInstructor, "students_taken_course": students_taken_course, "all_courses": all_courses})

    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../forum/home?fail=true')

def updateCourseName(req):
    username=req.session["username"]
    course_id = req.POST["course_id"]
    course_name = req.POST["course_name"]
    try:
        run_statement(f"CALL updateCourseName('{course_id}', '{course_name}', '{username}')")
        return HttpResponseRedirect("../forum/home")
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../forum/home?fail=true')

def giveGrade(req):
    username=req.session["username"]
    course_id = req.POST["course_id"]
    student_id = req.POST["student_id"]
    grade = req.POST["grade"]
    student_check = run_statement(f"SELECT * FROM Added_Courses, Courses WHERE Added_Courses.course_id = '{course_id}' and Added_Courses.course_id = Courses.course_id and Courses.instructor_username = '{username}' and Added_Courses.student_id = '{student_id}';") 
    if student_check:
        try:
            run_statement(f"CALL giveGrade('{course_id}', '{student_id}', '{grade}')")
            return HttpResponseRedirect("../forum/home")
        except Exception as e:
            print(str(e))
            return HttpResponseRedirect('../forum/home?fail=true')
    else:
        return HttpResponseRedirect('../forum/home?fail=true')

def s_addCourse(req):
    username=req.session["username"]
    course_id = req.POST["course_id"]
    #isAdded = run_statement(f"SELECT * FROM Added_Courses, Students WHERE Added_Courses.course_id = '{course_id}' and Added_Courses.student_id = Students.students_id and Students.students_username = '{username}';") 
    isGraded = run_statement(f"SELECT * FROM Grades, Students WHERE Grades.course_id = '{course_id}' and Grades.student_id = Students.students_id and  Students.students_username = '{username}'; ")
    prerequisites = run_statement(f"SELECT Prerequisites.pre_course_id FROM Prerequisites WHERE Prerequisites.primary_course_id = '{course_id}'")
    prerequisites_condition = True
    nof_student_taken = run_statement(f"SELECT COUNT(Added_Courses.course_id) FROM Added_Courses WHERE Added_Courses.course_id='{course_id}';")
    quota = run_statement(f"SELECT Courses.quota FROM Courses WHERE Courses.course_id = '{course_id}';")
    quota_restriction = quota[0][0]>nof_student_taken[0][0]
    student_id = run_statement(f"SELECT Students.students_id FROM Students WHERE Students.students_username = '{username}';")
    for element in prerequisites:
        prerequisites_satisfies = run_statement(f"SELECT * FROM Grades, Students WHERE Grades.course_id = '{element[0]}' and Grades.student_id = Students.students_id and  Students.students_username = '{username}'; ")
        if len(prerequisites_satisfies) == 0:
            prerequisites_condition = False

    if prerequisites_condition and not isGraded and quota_restriction:
        try:
            run_statement(f"CALL s_addCourse('{course_id}', '{student_id[0][0]}')")
            return HttpResponseRedirect("../forum/home")
        except Exception as e:
            print(str(e))
            return HttpResponseRedirect('../forum/home?fail=true')
    
    else: 
        return HttpResponseRedirect('../forum/home?fail=true')

def searched_courses(req):
    course_name = req.POST["searched"]
    try:
        username=req.session["username"] #Retrieve the username of the logged-in user
        #students_taken_course = run_statement(f"CALL viewStudentsTakenCourse('{course_id}', '{username}')")
        students = run_statement(f"SELECT Students.students_username AS username, Users.name, Users.surname, Users.email, Users.department_id, SUM(Courses.credits) AS completed_credits, SUM(Courses.credits*Grades.grade)/SUM(Courses.credits) AS GPA FROM Grades JOIN Courses ON Grades.course_id = Courses.course_id JOIN Students ON Students.students_id = Grades.student_id JOIN Users ON Students.students_username = Users.username GROUP BY student_id ORDER BY completed_credits ASC")
        instructors = run_statement(f"SELECT Instructors.instructor_username, Users.name, Users.surname, Users.email, Users.department_id, Instructors.title FROM Instructors, Users WHERE Instructors.instructor_username = Users.username;;") 
        searched_courses = run_statement(f"SELECT Courses.course_id, Courses.name, Users.surname, Users.department_id, Courses.credits, Delivered_in.classroom_id, Courses.slot, Courses.quota,(SELECT GROUP_CONCAT(Prerequisites.pre_course_id) FROM Prerequisites WHERE Prerequisites.primary_course_id = Courses.course_id) AS prerequisites FROM Courses, Users, Delivered_in WHERE Courses.name LIKE '%{course_name}%' and Users.username = Courses.instructor_username and Delivered_in.course_id = Courses.course_id ")
        isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
        all_courses = run_statement(f"SELECT Courses.course_id, Courses.name,Classrooms.classroom_id, Courses.slot, Courses.quota, (SELECT GROUP_CONCAT(Prerequisites.pre_course_id) FROM Prerequisites WHERE Prerequisites.primary_course_id = Courses.course_id) AS prerequisites FROM Courses, Departments, Classrooms, Users, Delivered_in WHERE Courses.instructor_username = Users.username and Departments.department_id = Users.department_id and Delivered_in.course_id = Courses.course_id and Classrooms.classroom_id = Delivered_in.classroom_id and Courses.instructor_username ='{username}' ORDER BY Courses.course_id ASC;")
        isStudent = run_statement(f"SELECT * FROM Students WHERE students_username='{username}';") 

        isInstructor = run_statement(f"SELECT * FROM Instructors WHERE instructor_username='{username}';") 
        isDepartmentManager=run_statement(f"SELECT * FROM Database_Managers WHERE username='{username}';") 
        student_id = run_statement(f"SELECT Students.students_id FROM Students WHERE Students.students_username = '{username}'")
        takenCourses = run_statement(f"SELECT newtable.course_id, Courses.name ,newtable.grade FROM (SELECT * FROM Grades UNION ALL SELECT Added_Courses.student_id, Added_Courses.course_id, null as grade FROM Added_Courses) as newtable, Courses WHERE newtable.student_id = '{student_id[0][0]}' and newtable.course_id = Courses.course_id")
        return render(req,'userHome.html',{"action_fail":isFailed,"username":username,  "isDepartmentManager": isDepartmentManager, "students": students, "instructors": instructors,  "isInstructor": isInstructor,  "all_courses": all_courses, "searched_courses": searched_courses, "isStudent": isStudent, "takenCourses": takenCourses})
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../forum/home?fail=true')

def filterCourses(req):
    department_id = req.POST["department_id"]
    campus = req.POST["campus"]
    minimum_credits = req.POST["minimum_credits"]
    maximum_credits = req.POST["maximum_credits"]
    try:
        username=req.session["username"] #Retrieve the username of the logged-in user
        students = run_statement(f"SELECT Students.students_username AS username, Users.name, Users.surname, Users.email, Users.department_id, SUM(Courses.credits) AS completed_credits, SUM(Courses.credits*Grades.grade)/SUM(Courses.credits) AS GPA FROM Grades JOIN Courses ON Grades.course_id = Courses.course_id JOIN Students ON Students.students_id = Grades.student_id JOIN Users ON Students.students_username = Users.username GROUP BY student_id ORDER BY completed_credits ASC")
        instructors = run_statement(f"SELECT Instructors.instructor_username, Users.name, Users.surname, Users.email, Users.department_id, Instructors.title FROM Instructors, Users WHERE Instructors.instructor_username = Users.username;;") 
        isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
        all_courses = run_statement(f"SELECT Courses.course_id, Courses.name,Classrooms.classroom_id, Courses.slot, Courses.quota, (SELECT GROUP_CONCAT(Prerequisites.pre_course_id) FROM Prerequisites WHERE Prerequisites.primary_course_id = Courses.course_id) AS prerequisites FROM Courses, Departments, Classrooms, Users, Delivered_in WHERE Courses.instructor_username = Users.username and Departments.department_id = Users.department_id and Delivered_in.course_id = Courses.course_id and Classrooms.classroom_id = Delivered_in.classroom_id and Courses.instructor_username ='{username}' ORDER BY Courses.course_id ASC;")
        isStudent = run_statement(f"SELECT * FROM Students WHERE students_username='{username}';") 
        isInstructor = run_statement(f"SELECT * FROM Instructors WHERE instructor_username='{username}';") 
        isDepartmentManager=run_statement(f"SELECT * FROM Database_Managers WHERE username='{username}';") 
        filterCourses = run_statement(f"CALL filterCourses('{department_id}', '{campus}', '{minimum_credits}', '{maximum_credits}')")
        student_id = run_statement(f"SELECT Students.students_id FROM Students WHERE Students.students_username = '{username}'")
        takenCourses = run_statement(f"SELECT newtable.course_id, Courses.name , newtable.gradeFROM (SELECT * FROM Grades UNION ALL SELECT Added_Courses.student_id, Added_Courses.course_id, null as grade FROM Added_Courses) as newtable, Courses WHERE newtable.student_id = '{student_id[0][0]}' and newtable.course_id = Courses.course_id")
        return render(req,'userHome.html',{"action_fail":isFailed,"username":username,  "isDepartmentManager": isDepartmentManager, "students": students, "instructors": instructors,  "isInstructor": isInstructor,  "all_courses": all_courses,  "isStudent": isStudent, "filterCourses": filterCourses, "takenCourses": takenCourses})
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../forum/home?fail=true')

