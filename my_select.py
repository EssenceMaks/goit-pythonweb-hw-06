from sqlalchemy import func, desc, Numeric
from sqlalchemy.orm import sessionmaker
from models import Student, Teacher, Group, Subject, Grade
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Завантаження змінних середовища (якщо є .env)
load_dotenv()

DB_URL = os.getenv('DB_URL', 'postgresql+psycopg2://postgres:yourpassword@localhost:5432/postgres')
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

def select_1():
    # 5 студентів із найбільшим середнім балом з усіх предметів
    session = Session()
    result = (
        session.query(Student.fullname, func.round(func.avg(Grade.grade).cast(Numeric), 2).label('avg_grade'))
        .join(Grade)
        .group_by(Student.id)
        .order_by(desc('avg_grade'))
        .limit(5)
        .all()
    )
    session.close()
    return result

def select_2(subject_id):
    # Студент із найвищим середнім балом з певного предмета
    session = Session()
    result = (
        session.query(Student.fullname, func.round(func.avg(Grade.grade).cast(Numeric), 2).label('avg_grade'))
        .join(Grade)
        .filter(Grade.subject_id == subject_id)
        .group_by(Student.id)
        .order_by(desc('avg_grade'))
        .first()
    )
    session.close()
    return result

def select_3(subject_id):
    # Середній бал у групах з певного предмета
    session = Session()
    result = (
        session.query(
            Group.name,
            func.round(func.avg(Grade.grade).cast(Numeric), 2).label('avg_grade')
        )
        .join(Student, Student.group_id == Group.id)
        .join(Grade, Grade.student_id == Student.id)
        .filter(Grade.subject_id == subject_id)
        .group_by(Group.id)
        .all()
    )
    session.close()
    return result

def select_4():
    # Середній бал на потоці (по всій таблиці оцінок)
    session = Session()
    result = session.query(func.round(func.avg(Grade.grade).cast(Numeric), 2)).scalar()
    session.close()
    return result

def select_5(teacher_id):
    # Які курси читає певний викладач
    session = Session()
    result = (
        session.query(Subject.name)
        .filter(Subject.teacher_id == teacher_id)
        .all()
    )
    session.close()
    return result

def select_6(group_id):
    # Список студентів у певній групі
    session = Session()
    result = (
        session.query(Student.fullname)
        .filter(Student.group_id == group_id)
        .all()
    )
    session.close()
    return result

def select_7(group_id, subject_id):
    # Оцінки студентів у окремій групі з певного предмета
    session = Session()
    result = (
        session.query(Student.fullname, Grade.grade)
        .join(Grade)
        .filter(Student.group_id == group_id, Grade.subject_id == subject_id)
        .all()
    )
    session.close()
    return result

def select_8(teacher_id):
    # Середній бал, який ставить певний викладач зі своїх предметів
    session = Session()
    result = (
        session.query(func.round(func.avg(Grade.grade).cast(Numeric), 2))
        .join(Subject, Grade.subject_id == Subject.id)
        .filter(Subject.teacher_id == teacher_id)
        .scalar()
    )
    session.close()
    return result

def select_9(student_id):
    # Курси, які відвідує певний студент
    session = Session()
    result = (
        session.query(Subject.name)
        .join(Grade, Grade.subject_id == Subject.id)
        .filter(Grade.student_id == student_id)
        .distinct()
        .all()
    )
    session.close()
    return result

def select_10(student_id, subject_id):
    # Оценки студента по предмету
    session = Session()
    result = (
        session.query(Grade.grade, Grade.date_received)
        .filter(Grade.student_id == student_id, Grade.subject_id == subject_id)
        .order_by(Grade.date_received)
        .all()
    )
    session.close()
    return result
