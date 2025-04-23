import os
import sys
import argparse
import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Group, Student, Teacher, Subject, Grade
from my_select import (
    select_1, select_2, select_3, select_4, select_5, select_6, select_7, select_8, select_9, select_10
)
from dotenv import load_dotenv

# Завантаження змінних середовища (якщо є .env)
load_dotenv()

DB_URL = os.getenv('DB_URL', 'postgresql+psycopg2://postgres:yourpassword@localhost:5432/postgres')
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

MODEL_MAP = {
    'Teacher': Teacher,
    'Student': Student,
    'Group': Group,
    'Subject': Subject,
}

# --- СИДУВАННЯ ДАНИХ ---
def seed_data():
    session = Session()
    fake = Faker()
    # Діалог із користувачем
    print("\n--- Сидування бази даних ---")
    print("1. Додати нові дані (без дублікатів)")
    print("2. Перезаписати все (очистити та створити заново)")
    print("3. Скасувати")
    choice = input("Оберіть дію (1/2/3): ").strip()
    if choice == '3' or choice.lower() == 'q':
        print("Сидування скасовано.")
        session.close()
        return
    # У півтора рази більше даних
    n_groups = int(3 * 1.5)
    n_teachers = int(5 * 1.5)
    n_subjects = int(8 * 1.5)
    n_students = int(50 * 1.5)
    n_grades = int(20 * 1.5)
    group_names = [f"{chr(65+i)}-1" for i in range(n_groups)]
    subject_names = ['Math', 'Physics', 'History', 'Chemistry', 'Biology', 'Literature', 'English', 'PE', 'Art', 'Music', 'Geography', 'IT'][:n_subjects]
    # --- Перезапис ---
    if choice == '2':
        session.query(Grade).delete()
        session.query(Student).delete()
        session.query(Subject).delete()
        session.query(Teacher).delete()
        session.query(Group).delete()
        session.commit()
    # --- Групи ---
    groups = []
    for name in group_names:
        group = session.query(Group).filter_by(name=name).first()
        if not group:
            group = Group(name=name)
            session.add(group)
            session.flush()
        groups.append(group)
    session.commit()
    # --- Викладачі ---
    teachers = []
    for _ in range(n_teachers):
        fullname = fake.unique.name()
        teacher = session.query(Teacher).filter_by(fullname=fullname).first()
        if not teacher:
            teacher = Teacher(fullname=fullname)
            session.add(teacher)
            session.flush()
        teachers.append(teacher)
    session.commit()
    # --- Предмети ---
    subjects = []
    for name in subject_names:
        teacher = random.choice(teachers)
        subject = session.query(Subject).filter_by(name=name).first()
        if not subject:
            subject = Subject(name=name, teacher=teacher)
            session.add(subject)
            session.flush()
        subjects.append(subject)
    session.commit()
    # --- Студенти ---
    students = []
    for _ in range(n_students):
        fullname = fake.unique.name()
        group = random.choice(groups)
        student = session.query(Student).filter_by(fullname=fullname).first()
        if not student:
            student = Student(fullname=fullname, group=group)
            session.add(student)
            session.flush()
        students.append(student)
    session.commit()
    # --- Оцінки ---
    grades = []
    for student in students:
        for subject in subjects:
            existing_dates = set()
            for _ in range(n_grades):
                grade = round(random.uniform(60, 100), 2)
                days_ago = random.randint(1, 365)
                date_received = (datetime.now() - timedelta(days=days_ago)).date()
                key = (student.id, subject.id, date_received)
                if key in existing_dates:
                    continue
                existing = session.query(Grade).filter_by(student_id=student.id, subject_id=subject.id, date_received=date_received).first()
                if not existing:
                    g = Grade(student=student, subject=subject, grade=grade, date_received=date_received)
                    session.add(g)
                    grades.append(g)
                    existing_dates.add(key)
    session.commit()
    print('Сидування завершено!')
    session.close()

# --- TUI & CLI ---
try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False

MENU_MAIN = [
    "CRUD шаблони (argparse)",
    "Select-запити",
    "Перегляд складу",
    "Поле введення команди",
    "Вихід"
]
MODELS_UI = [
    ("Викладачі", Teacher, "fullname"),
    ("Групи", Group, "name"),
    ("Студенти", Student, "fullname"),
    ("Предмети", Subject, "name"),
]
ACTIONS = ["Створити", "Список", "Оновити", "Видалити"]
SELECTS = [
    ("Топ-5 студентів за середнім балом", select_1, None, None),
    ("Студенти з найвищим середнім по предмету", select_2, Subject, "name"),
    ("Середній бал у групі по предмету", select_3, Subject, "name"),
    ("Середній бал по всіх групах", select_4, None, None),
    ("Курси, які читає викладач", select_5, Teacher, "fullname"),
    ("Список студентів у групі", select_6, Group, "name"),
    ("Оцінки студентів у групі по предмету", select_7, (Group, Subject), ("name", "name")),
    ("Середній бал викладача", select_8, Teacher, "fullname"),
    ("Курси, які відвідує студент", select_9, Student, "fullname"),
    ("Оцінки студента по предмету", select_10, (Student, Subject), ("fullname", "name")),
]
BROWSE = ["Групи", "Викладачі", "Студенти"]
COMMAND_TEMPLATES = [
    'python seed.py -a create -m Student -n "NAME"',
    'python seed.py -a update -m Teacher -n "NAME"',
    'python seed.py -a remove -m Group --id 1',
    'python seed.py -a list -m Subject',
    'або ваша команда'
]

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu(title, items, selected):
    clear()
    print(f"\n  {title}\n" + "=" * (len(title) + 2))
    for i, item in enumerate(items):
        prefix = "→ " if i == selected else "  "
        print(f"{prefix}{item}")
    print("\nСтрілки або W — вгору, S — вниз, Enter — обрати, Esc — назад/вихід або введіть номер пункту")

def input_text(prompt):
    print(f"\n{prompt}")
    return input("> ")

def menu_select(items, title="Меню"):
    selected = 0
    while True:
        print_menu(title, items, selected)
        if HAS_MSVCRT:
            key = msvcrt.getch()
            if key == b'\xe0':
                arrow = msvcrt.getch()
                if arrow == b'P':
                    selected = (selected + 1) % len(items)
                elif arrow == b'H':
                    selected = (selected - 1) % len(items)
            elif key == b'\r':
                return selected
            elif key == b'\x1b':
                return None
            elif key.isdigit():
                idx = int(key)
                if 0 <= idx < len(items):
                    return idx
            elif key.decode(errors='ignore').lower() in ['w', 'ц']:
                selected = (selected - 1) % len(items)
            elif key.decode(errors='ignore').lower() in ['s', 'ы', 'і']:
                selected = (selected + 1) % len(items)
        else:
            inp = input().strip().lower()
            if inp == '':
                return selected
            if inp == 'esc':
                return None
            if inp in ['w', 'ц']:
                selected = (selected - 1) % len(items)
            elif inp in ['s', 'ы', 'і']:
                selected = (selected + 1) % len(items)
            elif inp.isdigit():
                idx = int(inp) - 1
                if 0 <= idx < len(items):
                    return idx

def crud_flow():
    argparse_map = {
        "Створити": lambda m, v: f"python seed.py -a create -m {m} -n \"{v}\"",
        "Список":   lambda m, v: f"python seed.py -a list -m {m}",
        "Оновити": lambda m, v: f"python seed.py -a update -m {m} --id {v[0]} -n \"{v[1]}\"",
        "Видалити": lambda m, v: f"python seed.py -a remove -m {m} --id {v}",
    }
    while True:
        idx_model = menu_select([m[0] for m in MODELS_UI], "CRUD: Оберіть сутність")
        if idx_model is None:
            return
        model_name, model_cls, attr_name = MODELS_UI[idx_model]
        idx_action = menu_select(ACTIONS, f"{model_name}: дія")
        if idx_action is None:
            continue
        action = ACTIONS[idx_action]
        session = Session()
        try:
            if action == "Список":
                print(f"\nСписок {model_name}:")
                objs = session.query(model_cls).all()
                for obj in objs:
                    print(f"{obj.id}: {getattr(obj, attr_name)}")
                print(f"\nШаблон команди: {argparse_map['Список'](model_name[:-1], None)}")
                input("\nНажміть Enter для повернення...")
            elif action == "Створити":
                name = input_text(f"Введіть ім'я для {model_name[:-1]}:")
                print(f"\nШаблон команди: {argparse_map['Створити'](model_name[:-1], name)}")
                confirm = input("Виконати? (Enter — так, будь-який символ — ні): ")
                if confirm.strip() != "":
                    continue
                obj = model_cls(**{attr_name: name})
                session.add(obj)
                session.commit()
                print(f"Створено: {obj}")
                input("\nНажміть Enter для повернення...")
            elif action in ["Оновити", "Видалити"]:
                objs = session.query(model_cls).all()
                if not objs:
                    print("Немає об'єктів для вибору.")
                    input("\nНажміть Enter для повернення...")
                    continue
                items = [f"{obj.id}: {getattr(obj, attr_name)}" for obj in objs]
                idx = menu_select(items, f"Оберіть {model_name[:-1]}")
                if idx is None:
                    continue
                obj = objs[idx]
                if action == "Оновити":
                    new_val = input_text(f"Нове ім'я для {model_name[:-1]}:")
                    print(f"\nШаблон команди: {argparse_map['Оновити'](model_name[:-1], (obj.id, new_val))}")
                    confirm = input("Виконати? (Enter — так, будь-який символ — ні): ")
                    if confirm.strip() != "":
                        continue
                    setattr(obj, attr_name, new_val)
                    session.commit()
                    print(f"Оновлено: {obj}")
                    input("\nНажміть Enter для повернення...")
                elif action == "Видалити":
                    print(f"\nШаблон команди: {argparse_map['Видалити'](model_name[:-1], obj.id)}")
                    confirm = input("Видалити? (Enter — так, будь-який символ — ні): ")
                    if confirm.strip() != "":
                        continue
                    session.delete(obj)
                    session.commit()
                    print(f"Видалено: {obj}")
                    input("\nНажміть Enter для повернення...")
        finally:
            session.close()

def select_flow():
    while True:
        idx = menu_select([s[0] for s in SELECTS], "Select-запити")
        if idx is None:
            return
        title, func, models, attrs = SELECTS[idx]
        session = Session()
        try:
            if models is None:
                result = func()
            elif isinstance(models, tuple):
                params = []
                for i, m in enumerate(models):
                    objs = session.query(m).all()
                    if not objs:
                        print(f"Немає об'єктів для вибору {m.__name__}")
                        input("\nНажміть Enter для повернення...")
                        return
                    attr = attrs[i]
                    items = [f"{obj.id}: {getattr(obj, attr)}" for obj in objs]
                    idx_obj = menu_select(items, f"Оберіть {m.__name__}")
                    if idx_obj is None:
                        return
                    params.append(objs[idx_obj].id)
                result = func(*params)
            else:
                objs = session.query(models).all()
                if not objs:
                    print(f"Немає об'єктів для вибору {models.__name__}")
                    input("\nНажміть Enter для повернення...")
                    return
                attr = attrs
                items = [f"{obj.id}: {getattr(obj, attr)}" for obj in objs]
                idx_obj = menu_select(items, f"Оберіть {models.__name__}")
                if idx_obj is None:
                    return
                result = func(objs[idx_obj].id)
            print("\nРезультат:")
            # --- Виправлення: якщо результат не ітерований, обернути в список ---
            if result is None:
                print("Немає даних")
            elif isinstance(result, (str, int, float)):
                print(result)
            elif not hasattr(result, '__iter__') or isinstance(result, dict):
                print(result)
            elif isinstance(result, tuple):
                print(*result)
            else:
                for row in result:
                    print(row)
            input("\nНажміть Enter для повернення...")
        finally:
            session.close()

def browse_flow():
    session = Session()
    try:
        idx = menu_select(BROWSE, "Перегляд складу")
        if idx is None:
            return
        if idx == 0:
            objs = session.query(Group).all()
            for g in objs:
                print(f"{g.id}: {g.name}")
        elif idx == 1:
            objs = session.query(Teacher).all()
            for t in objs:
                print(f"{t.id}: {t.fullname}")
        elif idx == 2:
            objs = session.query(Student).all()
            for s in objs:
                print(f"{s.id}: {s.fullname}")
        input("\nНажміть Enter для повернення...")
    finally:
        session.close()

def command_input_flow():
    while True:
        clear()
        print("\n--- Поле введення команди ---\n")
        print("Приклади шаблонів:")
        for t in COMMAND_TEMPLATES:
            print(f"  {t}")
        print("\nВведіть свою команду або Enter для повернення:")
        cmd = input('> ').strip()
        if not cmd:
            return
        print(f"\nВиконати команду: {cmd}")
        confirm = input("Enter — виконати, будь-який символ — скасувати: ")
        if confirm.strip() != "":
            continue
        os.system(cmd)
        input("\nНажміть Enter для повернення...")

def cli_crud():
    parser = argparse.ArgumentParser(description="CLI для CRUD операцій з БД")
    parser.add_argument('-a', '--action', choices=['create', 'list', 'update', 'remove', 'seed'], required=True)
    parser.add_argument('-m', '--model', choices=MODEL_MAP.keys())
    parser.add_argument('-n', '--name', help="Імя або Назва")
    parser.add_argument('--id', type=int, help="ID обєкта")
    args = parser.parse_args()
    if args.action == 'seed':
        seed_data()
        return
    session = Session()
    Model = MODEL_MAP.get(args.model)
    try:
        if args.action == 'create':
            if not args.name:
                print('Необхідно вказати --name/-n для створення')
                return
            field = 'fullname' if args.model in ['Teacher', 'Student'] else 'name'
            obj = Model(**{field: args.name})
            session.add(obj)
            session.commit()
            print(f'Створено: {obj}')
        elif args.action == 'list':
            objs = session.query(Model).all()
            for obj in objs:
                if hasattr(obj, 'fullname'):
                    print(f"{obj.id}: {obj.fullname}")
                elif hasattr(obj, 'name'):
                    print(f"{obj.id}: {obj.name}")
                else:
                    print(obj)
        elif args.action == 'update':
            if not args.id or not args.name:
                print('Необхідно вказати --id і --name для оновлення')
                return
            obj = session.query(Model).get(args.id)
            if not obj:
                print(f'Обєкт з id={args.id} не знайдений')
                return
            field = 'fullname' if args.model in ['Teacher', 'Student'] else 'name'
            setattr(obj, field, args.name)
            session.commit()
            print(f'Оновлено: {obj}')
        elif args.action == 'remove':
            if not args.id:
                print('Необхідно вказати --id для видалення')
                return
            obj = session.query(Model).get(args.id)
            if not obj:
                print(f'Обєкт з id={args.id} не знайдений')
                return
            session.delete(obj)
            session.commit()
            print(f'Видалено: {obj}')
    finally:
        session.close()

def main():
    while True:
        idx = menu_select(MENU_MAIN, "Головне меню")
        if idx is None or idx == len(MENU_MAIN) - 1:
            print("Вихід...")
            break
        elif idx == 0:
            crud_flow()
        elif idx == 1:
            select_flow()
        elif idx == 2:
            browse_flow()
        elif idx == 3:
            command_input_flow()

if __name__ == "__main__":
    if len(sys.argv) > 1 and (sys.argv[1].startswith('-a') or sys.argv[1].startswith('--action')):
        cli_crud()
    else:
        main()