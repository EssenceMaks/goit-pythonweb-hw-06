import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Group, Student, Teacher, Subject, Grade

DB_URL = 'postgresql+psycopg2://postgres:303010@localhost:5432/postgres'

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()
fake = Faker()

# 1. Groups
group_names = ['A-1', 'B-1', 'C-1']
groups = [Group(name=name) for name in group_names]
session.add_all(groups)
session.commit()

# 2. Teachers
teachers = [Teacher(fullname=fake.name()) for _ in range(random.randint(3, 5))]
session.add_all(teachers)
session.commit()

# 3. Subjects
subject_names = ['Math', 'Physics', 'History', 'Chemistry', 'Biology', 'Literature', 'English', 'PE']
subjects = []
for name in random.sample(subject_names, random.randint(5, 8)):
    teacher = random.choice(teachers)
    subjects.append(Subject(name=name, teacher=teacher))
session.add_all(subjects)
session.commit()

# 4. Students
students = []
for _ in range(random.randint(30, 50)):
    group = random.choice(groups)
    students.append(Student(fullname=fake.name(), group=group))
session.add_all(students)
session.commit()

# 5. Grades
grades = []
for student in students:
    for subject in subjects:
        for _ in range(random.randint(10, 20)):
            grade = round(random.uniform(60, 100), 2)
            days_ago = random.randint(1, 365)
            date_received = datetime.now() - timedelta(days=days_ago)
            grades.append(Grade(student=student, subject=subject, grade=grade, date_received=date_received.date()))
session.add_all(grades)
session.commit()

print('Seed completed!')
session.close()