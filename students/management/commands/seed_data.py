"""
management/commands/seed_data.py
─────────────────────────────────────────────────────────────────
Run: python manage.py seed_data
Creates demo data so you can test the API immediately after setup.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta


class Command(BaseCommand):
    help = "Seed the database with realistic demo data for Eduverse Africa MVP"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING("🌱 Seeding Eduverse Africa demo data…"))

        school = self._create_school()
        self._create_users(school)
        self._create_academic_structure(school)
        self._create_students(school)
        self._create_fee_structure(school)
        self._create_library(school)
        self._create_leave_types(school)
        self._create_notices(school)

        self.stdout.write(self.style.SUCCESS("✅ Seed complete! Login at /admin with admin / admin123"))

    def _create_school(self):
        from tenants.models import School
        school, _ = School.objects.get_or_create(
            subdomain="demo",
            defaults={
                "name": "Greenfield International School",
                "address": "123 School Lane, Nairobi",
                "phone": "+254700000000",
                "email": "info@greenfield.ac.ke",
                "country": "Kenya",
                "currency": "KES",
                "plan": "premium",
            }
        )
        self.stdout.write(f"  🏫 Created school: {school.name}")
        return school

    def _create_users(self, school):
        from accounts.models import User
        users = [
            dict(username="admin",      first_name="School", last_name="Admin",   role="school_admin", email="admin@school.ac.ke",     password="admin123"),
            dict(username="teacher1",   first_name="Mary",   last_name="Kamau",   role="teacher",      email="mary@school.ac.ke",       password="teacher123"),
            dict(username="teacher2",   first_name="James",  last_name="Odhiambo",role="teacher",      email="james@school.ac.ke",      password="teacher123"),
            dict(username="accountant", first_name="Grace",  last_name="Mwangi",  role="accountant",   email="grace@school.ac.ke",      password="account123"),
            dict(username="librarian",  first_name="Peter",  last_name="Otieno",  role="librarian",    email="peter@school.ac.ke",      password="library123"),
            dict(username="hr",         first_name="Ann",    last_name="Wanjiku",  role="hr_admin",     email="ann@school.ac.ke",        password="hr123456"),
            dict(username="parent1",    first_name="John",   last_name="Njoroge",  role="parent",       email="john.njoroge@gmail.com",  password="parent123"),
            dict(username="parent2",    first_name="Alice",  last_name="Achieng", role="parent",       email="alice.achieng@gmail.com", password="parent123"),
        ]
        for u in users:
            password = u.pop("password")
            obj, created = User.objects.get_or_create(username=u["username"], defaults={**u, "school": school})
            if created:
                obj.set_password(password)
                obj.is_staff = (u["role"] in ("school_admin",))
                obj.is_superuser = (u["username"] == "admin")
                obj.save()
                self.stdout.write(f"  👤 Created user: {obj.username}")

    def _create_academic_structure(self, school):
        from students.models import AcademicYear, Grade, ClassRoom, Subject
        from accounts.models import User

        year, _ = AcademicYear.objects.get_or_create(
            school=school, name="2024-2025",
            defaults={"start_date": date(2024, 1, 8), "end_date": date(2024, 11, 29), "is_current": True},
        )

        grades_data = [
            ("Grade 1", 1), ("Grade 2", 2), ("Grade 3", 3),
            ("Grade 4", 4), ("Grade 5", 5), ("Grade 6", 6),
            ("Grade 7", 7), ("Grade 8", 8), ("Grade 9", 9),
        ]
        grades = {}
        for name, order in grades_data:
            g, _ = Grade.objects.get_or_create(school=school, name=name, defaults={"order": order})
            grades[name] = g

        teacher1 = User.objects.get(username="teacher1")
        teacher2 = User.objects.get(username="teacher2")

        ClassRoom.objects.get_or_create(
            school=school, grade=grades["Grade 7"], section="A", academic_year=year,
            defaults={"class_teacher": teacher1, "capacity": 40},
        )
        ClassRoom.objects.get_or_create(
            school=school, grade=grades["Grade 8"], section="A", academic_year=year,
            defaults={"class_teacher": teacher2, "capacity": 40},
        )

        subjects_data = [
            ("Mathematics",    "MATH7",  "Grade 7"),
            ("English",        "ENG7",   "Grade 7"),
            ("Science",        "SCI7",   "Grade 7"),
            ("Social Studies", "SS7",    "Grade 7"),
            ("Kiswahili",      "KIS7",   "Grade 7"),
            ("Mathematics",    "MATH8",  "Grade 8"),
            ("English",        "ENG8",   "Grade 8"),
            ("Science",        "SCI8",   "Grade 8"),
        ]
        for name, code, grade_name in subjects_data:
            Subject.objects.get_or_create(
                school=school, code=code,
                defaults={"name": name, "grade": grades[grade_name]},
            )
        self.stdout.write("  📚 Academic structure created")

    def _create_students(self, school):
        from students.models import Student, ClassRoom, StaffProfile, AcademicYear
        from accounts.models import User

        year      = AcademicYear.objects.get(school=school, name="2024-2025")
        classroom = ClassRoom.objects.filter(school=school, grade__name="Grade 7").first()
        parent1   = User.objects.get(username="parent1")
        parent2   = User.objects.get(username="parent2")

        students_data = [
            dict(admission_number="ADM-001", first_name="Brian",    last_name="Njoroge",  date_of_birth=date(2012, 3, 14), gender="M", parent_user=parent1, parent_name="John Njoroge",  parent_phone="+254712345678"),
            dict(admission_number="ADM-002", first_name="Faith",    last_name="Njoroge",  date_of_birth=date(2013, 7, 22), gender="F", parent_user=parent1, parent_name="John Njoroge",  parent_phone="+254712345678"),
            dict(admission_number="ADM-003", first_name="Cynthia",  last_name="Achieng",  date_of_birth=date(2012, 11, 5), gender="F", parent_user=parent2, parent_name="Alice Achieng", parent_phone="+254723456789"),
            dict(admission_number="ADM-004", first_name="Emmanuel", last_name="Mwangi",   date_of_birth=date(2012, 1, 30), gender="M", parent_user=None,    parent_name="Grace Mwangi",  parent_phone="+254734567890"),
            dict(admission_number="ADM-005", first_name="Sharon",   last_name="Otieno",   date_of_birth=date(2013, 5, 18), gender="F", parent_user=None,    parent_name="Peter Otieno",  parent_phone="+254745678901"),
        ]
        for s_data in students_data:
            Student.objects.get_or_create(
                school=school, admission_number=s_data["admission_number"],
                defaults={**s_data, "current_class": classroom, "admission_date": date(2024, 1, 8)},
            )

        teacher1 = User.objects.get(username="teacher1")
        teacher2 = User.objects.get(username="teacher2")
        from students.models import Subject
        for user, emp_id, subjects in [
            (teacher1, "EMP-001", ["MATH7", "SCI7"]),
            (teacher2, "EMP-002", ["MATH8", "ENG8"]),
        ]:
            profile, _ = StaffProfile.objects.get_or_create(
                school=school, user=user,
                defaults={
                    "employee_id":  emp_id,
                    "department":   "academic",
                    "designation":  "Teacher",
                    "date_joined":  date(2023, 1, 9),
                    "base_salary":  50000,
                },
            )
            for code in subjects:
                try:
                    subj = Subject.objects.get(school=school, code=code)
                    profile.subjects_taught.add(subj)
                except Subject.DoesNotExist:
                    pass

        self.stdout.write("  👩‍🎓 Students & staff profiles created")

    def _create_fee_structure(self, school):
        from fees.models import FeeHead, FeeStructure
        from students.models import AcademicYear, Grade

        year = AcademicYear.objects.get(school=school, name="2024-2025")
        heads_data = [
            ("Tuition Fee", True), ("Activity Fee", False),
            ("Uniform Fee", False), ("Exam Fee", False),
        ]
        heads = {}
        for name, recurring in heads_data:
            h, _ = FeeHead.objects.get_or_create(school=school, name=name, defaults={"is_recurring": recurring})
            heads[name] = h

        for grade in Grade.objects.filter(school=school, name__in=["Grade 7", "Grade 8"]):
            for head_name, amount in [("Tuition Fee", 3500), ("Activity Fee", 500), ("Exam Fee", 1000)]:
                FeeStructure.objects.get_or_create(
                    school=school, academic_year=year, grade=grade, fee_head=heads[head_name],
                    defaults={"amount": amount},
                )
        self.stdout.write("  💰 Fee structure created")

    def _create_library(self, school):
        from library.models import Book

        books_data = [
            ("LIB-001", "Mathematics Grade 7", "KIE",          "textbook",    5),
            ("LIB-002", "English Grammar",      "Oxford Press", "textbook",    3),
            ("LIB-003", "Things Fall Apart",    "Chinua Achebe","fiction",     4),
            ("LIB-004", "Animal Farm",          "G. Orwell",    "fiction",     2),
            ("LIB-005", "Kenya Geography",      "KIE",          "textbook",    6),
        ]
        for book_id, title, author, category, copies in books_data:
            Book.objects.get_or_create(
                school=school, book_id=book_id,
                defaults={"title": title, "author": author, "category": category,
                          "total_copies": copies, "available_copies": copies},
            )
        self.stdout.write("  📖 Library books created")

    def _create_leave_types(self, school):
        from hr.models import LeaveType

        for name, days, paid in [
            ("Casual Leave", 12, True), ("Sick Leave", 10, True),
            ("Unpaid Leave", 30, False), ("Maternity Leave", 90, True),
        ]:
            LeaveType.objects.get_or_create(school=school, name=name, defaults={"max_days_per_year": days, "is_paid": paid})
        self.stdout.write("  🏖️  Leave types created")

    def _create_notices(self, school):
        from portal.models import Notice
        from accounts.models import User

        admin = User.objects.get(username="admin")
        notices_data = [
            ("Welcome Back — Term 2!",  "School reopens on Monday 8th January. All students must be in full uniform.", "high"),
            ("Parent-Teacher Meeting",  "The PTA meeting is scheduled for Friday 19th January at 3:00 PM.", "normal"),
            ("Library Rules Reminder",  "All borrowed books must be returned within 14 days. Fines apply for overdue books.", "low"),
        ]
        for title, body, priority in notices_data:
            Notice.objects.get_or_create(
                school=school, title=title,
                defaults={"body": body, "priority": priority, "is_published": True, "published_by": admin},
            )
        self.stdout.write("  📢 Notices created")
