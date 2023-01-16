from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home',views.homePage,name="homePage"),
    path('login',views.login,name="login"),
    path('loginStudents',views.login_students,name="loginStudents"),
    path('loginInstructors',views.login_instructors,name="loginInstructors"),

    path('createStudent',views.createStudent,name="createStudent"),
    path('createInstructor',views.createInstructor,name="createInstructor"),

    path('deleteStudent',views.deleteStudent,name="deleteStudent"),
    path('updateTitle',views.updateTitle,name="updateTitle"),
    path('viewGrades',views.viewGrades, name="viewGrades"),
    path('viewCourses',views.viewCourses, name="viewCourses"),
    path('viewGradeAverage',views.viewGradeAverage, name="viewGradeAverage"),
    path('viewAvailableClassrooms', views.viewAvailableClassrooms, name="viewAvailableClassrooms"),
    path('addCourses', views.addCourses, name="addCourses"),
    path('addPrerequisite', views.addPrerequisite, name="addPrerequisite"),
    path('viewStudentsTakenCourse', views.viewStudentsTakenCourse, name="viewStudentsTakenCourse"),
    path('updateCourseName', views.updateCourseName, name="updateCourseName"),
    path('giveGrade', views.giveGrade, name="giveGrade"),
    path('s_addCourse', views.s_addCourse, name="s_addCourse"),
    path('searched_courses', views.searched_courses, name="searched_courses"),
    path('filterCourses', views.filterCourses, name="filterCourses"),






]