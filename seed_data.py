"""
=============================================================
  BIDYATek – Full Database Seed Script
  Run from the project root with venv active:

      python manage.py shell < seed_data.py
  OR:
      python manage.py shell
      >>> exec(open('seed_data.py').read())

  What this creates:
    ✔ Tenant-safe (runs inside the active schema)
    ✔ Academic year, session
    ✔ Classes, groups, sections, shifts, versions
    ✔ ClassConfig  (class + group + section + shift combos)
    ✔ Subjects, SubjectConfig, Mark_type (CQ/MCQ/Practical)
    ✔ Mark_config  (per class, per subject, per mark type)
    ✔ Periods, PeriodConfig
    ✔ Departments, Roles
    ✔ 10 Teachers (staff users + StaffProfile + SalaryConfig)
    ✔ 40 Students (user + StudentProfile) spread across classes
    ✔ 10 Parents (user + ParentProfile)
    ✔ SubjectAssign  (which subjects belong to which class)
    ✔ TeacherSubjectAssign
    ✔ 3 Exam names  (1st Term / 2nd Term / Annual)
    ✔ Grade rules   (A+ … F)
    ✔ Subject_mark  (CQ + MCQ + Practical for every student)
    ✔ StudentResult (auto-calculated via signals)
    ✔ FeeHead, Feetype, Fee_month, Fee_package, Fees_name
    ✔ Fees  →  paid / unpaid / partial  for all students
    ✔ PartialPayment records for partial-status fees
    ✔ Accounting: LedgerCategory + Ledger stubs
    ✔ Notice board entries
    ✔ MainBalance seed
=============================================================
"""

import os, django, random, datetime
from decimal import Decimal

# ── Disable signals that need full infra (e.g. MainBalance receiver)
# We'll seed MainBalance manually.
from django.db.models.signals import post_save, pre_delete
from crucial.models import (
    Expenseitemlist, Withdraw, IncomeitemList
)
post_save.disconnect(sender=Expenseitemlist, dispatch_uid=None)
post_save.disconnect(sender=Withdraw,        dispatch_uid=None)
post_save.disconnect(sender=IncomeitemList,  dispatch_uid=None)

print("=" * 60)
print("  BIDYATek Seed Script Starting …")
print("=" * 60)

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
from django.contrib.auth.hashers import make_password

def p(msg): print(f"  ✔  {msg}")

YEAR = "2025"
rng  = random.Random(42)          # fixed seed → reproducible

# ─────────────────────────────────────────────────────────────
# 1. ACCOUNTING LEDGER CATEGORIES  (needed before FeeHead signal)
# ─────────────────────────────────────────────────────────────
from accounting.models import LedgerCategory, Ledger, MainBalance

cat_data = [
    ("Asset",     "AST", "Asset accounts"),
    ("Liability", "LIA", "Liability accounts"),
    ("Equity",    "EQT", "Equity accounts"),
    ("Income",    "INC", "Income accounts"),
    ("Expense",   "EXP", "Expense accounts"),
]
ledger_cats = {}
for name, code, desc in cat_data:
    obj, _ = LedgerCategory.objects.get_or_create(
        name=name,
        defaults={"code": code, "description": desc}
    )
    ledger_cats[name] = obj
p("LedgerCategories")

# Base ledgers
ledger_seeds = [
    ("INC-001", "Tuition Fee Income",   "Income",  "Credit"),
    ("INC-002", "Admission Fee Income", "Income",  "Credit"),
    ("INC-003", "Exam Fee Income",      "Income",  "Credit"),
    ("INC-004", "Late Fee Income",      "Income",  "Credit"),
    ("AST-001", "Cash in Hand",         "Asset",   "Debit"),
    ("AST-002", "Bank Account",         "Asset",   "Debit"),
    ("EXP-001", "Staff Salary",         "Expense", "Debit"),
    ("EXP-002", "Utilities",            "Expense", "Debit"),
    ("LIA-001", "Student Fee Payable",  "Liability","Credit"),
]
ledgers = {}
for code, name, cat, bal in ledger_seeds:
    obj, _ = Ledger.objects.get_or_create(
        code=code,
        defaults={
            "name": name,
            "category": ledger_cats[cat],
            "balance_type": bal,
            "opening_balance": 0,
            "is_active": True,
        }
    )
    ledgers[code] = obj
p("Base Ledgers")

cash_ledger_obj = ledgers["AST-001"]  # "Cash in Hand" — Asset ledger
MainBalance.objects.get_or_create(
    cash_ledger=cash_ledger_obj,
    defaults={"balance": Decimal("0.00")}
)
p("MainBalance")

# ─────────────────────────────────────────────────────────────
# 2. ACADEMIC YEAR & SESSION
# ─────────────────────────────────────────────────────────────
from core.models import (
    Admission_Year, AcademicSession,
    StudentClass, StudentSection, StudentShift, StuGroup,
    Subject, Period,
    ClassGroupConfig, ClassConfig, PeriodConfig,
    SubjectConfig, SubjectAssign,
    Mark_type, Mark_config,
)

acad_year, _ = Admission_Year.objects.get_or_create(name=YEAR)
acad_session, _ = AcademicSession.objects.get_or_create(
    start_year=YEAR, end_year=str(int(YEAR)+1)
)
p(f"Academic Year {YEAR}  |  Session {YEAR}-{int(YEAR)+1}")

# ─────────────────────────────────────────────────────────────
# 3. CLASSES, SECTIONS, SHIFTS, GROUPS
# ─────────────────────────────────────────────────────────────
class_names   = ["Class 6", "Class 7", "Class 8", "Class 9", "Class 10"]
section_names = ["A", "B"]
shift_names   = ["Morning", "Day"]
group_names   = ["Science", "Arts", "Commerce"]

classes  = {n: StudentClass.objects.get_or_create(name=n)[0]  for n in class_names}
sections = {n: StudentSection.objects.get_or_create(name=n)[0] for n in section_names}
shifts   = {n: StudentShift.objects.get_or_create(name=n)[0]   for n in shift_names}
groups   = {n: StuGroup.objects.get_or_create(name=n)[0]       for n in group_names}
p("Classes / Sections / Shifts / Groups")

# ─────────────────────────────────────────────────────────────
# 4. SUBJECTS
# ─────────────────────────────────────────────────────────────
subject_names = [
    "Bangla", "English", "Mathematics", "Science",
    "Social Science", "Religion", "ICT",
    "Physics", "Chemistry", "Biology",
    "Higher Mathematics", "Geography", "History",
    "Economics", "Accounting", "Business Studies",
]
subjects = {n: Subject.objects.get_or_create(name=n)[0] for n in subject_names}
p(f"{len(subjects)} Subjects")

# ─────────────────────────────────────────────────────────────
# 5. MARK TYPES  (CQ / MCQ / Practical)
# ─────────────────────────────────────────────────────────────
mark_types = {
    n: Mark_type.objects.get_or_create(name=n)[0]
    for n in ["CQ", "MCQ", "Practical"]
}
p("Mark Types: CQ, MCQ, Practical")

# ─────────────────────────────────────────────────────────────
# 6. CLASS-GROUP CONFIGS  +  CLASS CONFIGS
# ─────────────────────────────────────────────────────────────
# We create:
#   Class 6-8  → no group  → Section A/B  → Morning shift
#   Class 9-10 → Science / Arts / Commerce → Section A → Morning
class_group_configs = {}  # key: (class_name, group_name_or_None)
class_configs       = {}  # key: (class_name, group_name_or_None, section, shift)

def get_cgc(cls_name, grp_name=None):
    key = (cls_name, grp_name)
    if key not in class_group_configs:
        obj, _ = ClassGroupConfig.objects.get_or_create(
            class_id=classes[cls_name],
            group_id=groups[grp_name] if grp_name else None,
        )
        class_group_configs[key] = obj
    return class_group_configs[key]

def get_cc(cls_name, grp_name, sec_name, shift_name):
    key = (cls_name, grp_name, sec_name, shift_name)
    if key not in class_configs:
        cgc = get_cgc(cls_name, grp_name)
        obj, _ = ClassConfig.objects.get_or_create(
            class_group_id=cgc,
            section_id=sections[sec_name],
            shift_id=shifts[shift_name],
        )
        class_configs[key] = obj
    return class_configs[key]

# Lower classes: no group
for cname in ["Class 6", "Class 7", "Class 8"]:
    for sec in ["A", "B"]:
        get_cc(cname, None, sec, "Morning")

# Upper classes: with groups
for cname in ["Class 9", "Class 10"]:
    for grp in ["Science", "Arts", "Commerce"]:
        get_cc(cname, grp, "A", "Morning")

p(f"{len(class_configs)} ClassConfigs")

# ─────────────────────────────────────────────────────────────
# 7. SUBJECT ASSIGNMENT PER CLASS-GROUP
# ─────────────────────────────────────────────────────────────
# Common subjects for all classes
common_subs = ["Bangla", "English", "Mathematics", "Religion", "ICT", "Social Science"]
science_subs  = ["Physics", "Chemistry", "Biology", "Higher Mathematics"]
arts_subs     = ["Geography", "History"]
commerce_subs = ["Economics", "Accounting", "Business Studies"]

def assign_subjects_to_cgc(cgc, sub_names):
    sa, _ = SubjectAssign.objects.get_or_create(class_id=cgc)
    for sn in sub_names:
        sa.subjects.add(subjects[sn])
    return sa

for cname in ["Class 6", "Class 7", "Class 8"]:
    cgc = get_cgc(cname, None)
    assign_subjects_to_cgc(cgc, common_subs + ["Science"])

for cname in ["Class 9", "Class 10"]:
    assign_subjects_to_cgc(get_cgc(cname, "Science"),  common_subs + science_subs)
    assign_subjects_to_cgc(get_cgc(cname, "Arts"),     common_subs + arts_subs)
    assign_subjects_to_cgc(get_cgc(cname, "Commerce"), common_subs + commerce_subs)

p("SubjectAssign done")

# ─────────────────────────────────────────────────────────────
# 8. SUBJECT CONFIG  (serial, marks, type)
# ─────────────────────────────────────────────────────────────
# Mark distribution: CQ=70, MCQ=30 for regular; Practical=25, CQ=50, MCQ=25 for science
def get_sub_list(cgc):
    try:
        return list(SubjectAssign.objects.get(class_id=cgc).subjects.all())
    except SubjectAssign.DoesNotExist:
        return []

all_cgcs = list(ClassGroupConfig.objects.all())
sc_map = {}  # (cgc_id, subject_id) → SubjectConfig

for cgc in all_cgcs:
    subs = get_sub_list(cgc)
    practical_subs = {"Physics", "Chemistry", "Biology", "ICT"}
    for idx, sub in enumerate(subs, start=1):
        total_mark = 100
        sc, _ = SubjectConfig.objects.get_or_create(
            class_id=cgc,
            subject_id=sub,
            defaults={
                "subject_Serial": idx,
                "subject_marge": 0,
                "subject_type": "COMPULSARY",
                "mark": total_mark,
            }
        )
        sc_map[(cgc.id, sub.id)] = sc

p(f"{len(sc_map)} SubjectConfigs")

# ─────────────────────────────────────────────────────────────
# 9. MARK CONFIG  (CQ / MCQ / Practical per subject)
# ─────────────────────────────────────────────────────────────
# Distribution: CQ=70 pass=28, MCQ=30 pass=12  (total=100, pass=40)
# Practical subjects: CQ=50 pass=20, MCQ=25 pass=10, Practical=25 pass=10
practical_sub_names = {"Physics", "Chemistry", "Biology", "ICT"}

mc_map = {}  # (cgc_id, sc_id, mt_name) → Mark_config

for cgc in all_cgcs:
    subs = get_sub_list(cgc)
    for sub in subs:
        sc = sc_map.get((cgc.id, sub.id))
        if not sc:
            continue
        is_prac = sub.name in practical_sub_names

        configs = [
            ("CQ",       50 if is_prac else 70,  20 if is_prac else 28),
            ("MCQ",      25 if is_prac else 30,  10 if is_prac else 12),
            ("Practical",25 if is_prac else 0,   10 if is_prac else 0),
        ]
        for mt_name, mark, pass_mark in configs:
            if mark == 0:
                continue
            mc, _ = Mark_config.objects.get_or_create(
                class_id=cgc,
                subject_conf_id=sc,
                mark_type_id=mark_types[mt_name],
                defaults={
                    "mark": mark,
                    "pass_mark": pass_mark,
                    "academic_year": acad_year,
                }
            )
            mc_map[(cgc.id, sc.id, mt_name)] = mc

p(f"{len(mc_map)} Mark_configs (CQ/MCQ/Practical)")

# ─────────────────────────────────────────────────────────────
# 10. PERIODS & PERIOD CONFIGS
# ─────────────────────────────────────────────────────────────
period_names = [f"Period {i}" for i in range(1, 9)]
period_objs  = {n: Period.objects.get_or_create(name=n)[0] for n in period_names}

period_times = [
    ("08:00", "08:45"),
    ("08:45", "09:30"),
    ("09:30", "10:15"),
    ("10:15", "10:30"),   # break
    ("10:30", "11:15"),
    ("11:15", "12:00"),
    ("12:00", "12:45"),
    ("12:45", "13:30"),
]

# Assign period configs to first ClassConfig of each class (just as a representative)
for cc in list(class_configs.values())[:4]:
    for idx, (pname, (st, et)) in enumerate(zip(period_names, period_times)):
        is_break = (idx == 3)
        PeriodConfig.objects.get_or_create(
            class_id=cc,
            period_id=period_objs[pname],
            defaults={
                "start_time": st,
                "end_time": et,
                "break_time": is_break,
            }
        )

p("PeriodConfigs")

# ─────────────────────────────────────────────────────────────
# 11. DEPARTMENTS & ROLE TYPES
# ─────────────────────────────────────────────────────────────
from user.models import Department, RoleType

depts = {n: Department.objects.get_or_create(name=n)[0] for n in
         ["Science Dept", "Humanities Dept", "Commerce Dept", "Administration"]}
roles = {n: RoleType.objects.get_or_create(name=n)[0] for n in
         ["Teacher", "Admin", "Librarian", "Accountant"]}
p("Departments & Roles")

# ─────────────────────────────────────────────────────────────
# 12. SUPERUSER  (admin)
# ─────────────────────────────────────────────────────────────
from shared.models import CustomUser

if not CustomUser.objects.filter(username="admin").exists():
    admin = CustomUser.objects.create_superuser(
        username="admin",
        password="admin1234",
        name="School Admin",
        email="admin@bidyatek.com",
    )
    p("Superuser  admin / admin1234")
else:
    admin = CustomUser.objects.get(username="admin")
    p("Superuser already exists")

# ─────────────────────────────────────────────────────────────
# 13. TEACHERS
# ─────────────────────────────────────────────────────────────
from user.models import Staff, StaffProfile
from crucial.models import SalaryConfiguration

teacher_data = [
    ("T001", "Md. Rafiqul Islam",    "Male",   "Science Dept",   "Teacher", "Physics",    28000),
    ("T002", "Fatema Begum",         "Female", "Science Dept",   "Teacher", "Chemistry",  26000),
    ("T003", "Md. Kamal Hossain",    "Male",   "Science Dept",   "Teacher", "Biology",    25000),
    ("T004", "Nasrin Akter",         "Female", "Humanities Dept","Teacher", "Bangla",     24000),
    ("T005", "Md. Jahangir Alam",    "Male",   "Humanities Dept","Teacher", "English",    27000),
    ("T006", "Roksana Khatun",       "Female", "Humanities Dept","Teacher", "History",    23000),
    ("T007", "Md. Shafiqul Haque",   "Male",   "Commerce Dept",  "Teacher", "Accounting", 25000),
    ("T008", "Dilara Parvin",        "Female", "Commerce Dept",  "Teacher", "Economics",  24000),
    ("T009", "Md. Aminul Islam",     "Male",   "Administration", "Admin",   "ICT",        30000),
    ("T010", "Sanjida Sultana",      "Female", "Science Dept",   "Teacher", "Mathematics",26000),
]

teachers = []   # list of StaffProfile
for tid, name, gender, dept, role, subj, basic in teacher_data:
    uname = f"teacher_{tid.lower()}"
    if not CustomUser.objects.filter(username=uname).exists():
        u = Staff(
            username=uname,
            name=name,
            gender=gender,
            email=f"{uname}@bidyatek.com",
            status="Active",
            user_id=int(tid[1:]) + 1000,
        )
        u.set_password("teacher1234")
        u.save()
    else:
        u = CustomUser.objects.get(username=uname)

    sp, _ = StaffProfile.objects.get_or_create(
        staff_field=u,
        defaults={
            "staff_id_no": tid,
            "designation": role,
            "department": depts[dept],
            "role": roles[role],
            "employee_type": "Permanent",
            "job_nature": "Fulltime",
            "joining_date": datetime.date(2020, 1, 15),
            "subject": subj,
        }
    )
    SalaryConfiguration.objects.get_or_create(
        employee=sp,
        defaults={"basic_salary": basic, "created_by": admin}
    )
    teachers.append(sp)

p(f"{len(teachers)} Teachers created")

# ─────────────────────────────────────────────────────────────
# 14. PARENTS
# ─────────────────────────────────────────────────────────────
from user.models import Parent, ParentProfile

parent_data = [
    ("P001", "Md. Abdul Karim",  "Male",   "01711-000001"),
    ("P002", "Md. Rahim Uddin",  "Male",   "01711-000002"),
    ("P003", "Md. Salam Mia",    "Male",   "01711-000003"),
    ("P004", "Md. Jamal Uddin",  "Male",   "01711-000004"),
    ("P005", "Md. Nabi Hossain", "Male",   "01711-000005"),
    ("P006", "Md. Bachchu Mia",  "Male",   "01711-000006"),
    ("P007", "Md. Amir Hossain", "Male",   "01711-000007"),
    ("P008", "Md. Selim Reza",   "Male",   "01711-000008"),
    ("P009", "Md. Faruk Ahmed",  "Male",   "01711-000009"),
    ("P010", "Md. Mofizur Rahman","Male",  "01711-000010"),
]

parents_list = []
for pid, name, gender, phone in parent_data:
    uname = f"parent_{pid.lower()}"
    if not CustomUser.objects.filter(username=uname).exists():
        u = Parent(
            username=uname,
            name=name,
            gender=gender,
            phone_number=phone,
            status="Active",
            user_id=int(pid[1:]) + 2000,
        )
        u.set_password("parent1234")
        u.save()
    else:
        u = CustomUser.objects.get(username=uname)

    pp, _ = ParentProfile.objects.get_or_create(
        parent_field=u,
        defaults={
            "father_name": name,
            "father_mobile_no": phone,
            "f_occupation": "Business",
        }
    )
    parents_list.append(pp.parent_field)

p(f"{len(parents_list)} Parents created")

# ─────────────────────────────────────────────────────────────
# 15. STUDENTS  (40 students spread across classes)
# ─────────────────────────────────────────────────────────────
from user.models import Student, StudentProfile

# Map class configs to use for students
# Lower classes: no group
student_class_targets = [
    ("Class 6",  None,       "A", "Morning"),
    ("Class 6",  None,       "B", "Morning"),
    ("Class 7",  None,       "A", "Morning"),
    ("Class 7",  None,       "B", "Morning"),
    ("Class 8",  None,       "A", "Morning"),
    ("Class 9",  "Science",  "A", "Morning"),
    ("Class 9",  "Arts",     "A", "Morning"),
    ("Class 9",  "Commerce", "A", "Morning"),
    ("Class 10", "Science",  "A", "Morning"),
    ("Class 10", "Arts",     "A", "Morning"),
]

first_names_m = ["Rahim", "Karim", "Jamal", "Amir", "Selim",
                 "Faruk", "Mofiz", "Bachchu", "Nabi", "Salam",
                 "Rubel", "Milon", "Sumon", "Ratan", "Babu"]
first_names_f = ["Fatema", "Nasrin", "Roksana", "Dilara", "Sanjida",
                 "Mitu", "Piu", "Tania", "Mim", "Ritu"]
last_names = ["Islam", "Hossain", "Begum", "Akter", "Khatun",
              "Rahman", "Ahmed", "Uddin", "Mia", "Parvin"]

student_profiles = []
s_idx = 0

for grp_idx, (cname, gname, sec, shift) in enumerate(student_class_targets):
    cc_key = (cname, gname, sec, shift)
    cc = class_configs.get(cc_key)
    if not cc:
        continue
    parent = parents_list[grp_idx % len(parents_list)]

    for local_i in range(4):   # 4 students per class-group = 40 total
        s_idx += 1
        gender = "Male" if s_idx % 3 != 0 else "Female"
        fname  = rng.choice(first_names_m if gender == "Male" else first_names_f)
        lname  = rng.choice(last_names)
        full_name = f"{fname} {lname}"
        uname  = f"student{s_idx:03d}"
        roll   = (grp_idx * 10) + local_i + 1

        if not CustomUser.objects.filter(username=uname).exists():
            u = Student(
                username=uname,
                name=full_name,
                gender=gender,
                phone_number=f"017{s_idx:08d}",
                email=f"{uname}@bidyatek.com",
                status="Active",
                dob=datetime.date(2008 + (s_idx % 4), rng.randint(1, 12), rng.randint(1, 28)),
                religion="Islam",
                blood_group=rng.choice(["A+", "B+", "O+", "AB+"]),
                user_id=s_idx + 3000,
            )
            u.set_password("student1234")
            u.save()
        else:
            u = CustomUser.objects.get(username=uname)

        sp, _ = StudentProfile.objects.get_or_create(
            student_field=u,
            defaults={
                "class_id": cc,
                "admission_year_id": acad_year,
                "academic_session_year": acad_session,
                "roll_no": roll,
                "version": "Bangla",
                "admission_date": datetime.date(int(YEAR), 1, 10),
                "nationality": "Bangladeshi",
                "district": "Dhaka",
                "parent_id": parent,
            }
        )
        student_profiles.append(sp)

p(f"{len(student_profiles)} Students created")

# ─────────────────────────────────────────────────────────────
# 16. TEACHER-SUBJECT ASSIGN
# ─────────────────────────────────────────────────────────────
from crucial.models import TeacherSubjectAssign

teacher_sub_map = {
    "Physics":      (teachers[0], ["Physics"]),
    "Chemistry":    (teachers[1], ["Chemistry"]),
    "Biology":      (teachers[2], ["Biology"]),
    "Bangla":       (teachers[3], ["Bangla"]),
    "English":      (teachers[4], ["English"]),
    "History":      (teachers[5], ["History", "Social Science"]),
    "Accounting":   (teachers[6], ["Accounting", "Business Studies"]),
    "Economics":    (teachers[7], ["Economics"]),
    "ICT":          (teachers[8], ["ICT"]),
    "Mathematics":  (teachers[9], ["Mathematics", "Higher Mathematics"]),
}

for key, (teacher, sub_names) in teacher_sub_map.items():
    tsa, _ = TeacherSubjectAssign.objects.get_or_create(
        teacher_id=teacher,
        defaults={"academic_year": acad_year}
    )
    for sn in sub_names:
        if sn in subjects:
            tsa.subject_assigns.add(subjects[sn])
    for cc in list(class_configs.values()):
        tsa.class_assigns.add(cc)

p("TeacherSubjectAssign done")

# ─────────────────────────────────────────────────────────────
# 17. EXAM NAMES
# ─────────────────────────────────────────────────────────────
from exam.models import Examname, Graderule, ClassExam, Subject_mark, StudentResult

exam_data = [
    ("1st Term Exam",  datetime.date(int(YEAR), 3, 1),  datetime.date(int(YEAR), 3, 15)),
    ("2nd Term Exam",  datetime.date(int(YEAR), 7, 1),  datetime.date(int(YEAR), 7, 15)),
    ("Annual Exam",    datetime.date(int(YEAR), 11, 1), datetime.date(int(YEAR), 11, 20)),
]

exams = []
for ename, sd, ed in exam_data:
    ex, _ = Examname.objects.get_or_create(
        name=ename,
        academic_year=acad_year,
        defaults={"start_date": sd, "end_date": ed}
    )
    exams.append(ex)
    for sc in classes.values():
        ClassExam.objects.get_or_create(
            exam_name=ex, class_name=sc,
            defaults={"start_date": sd, "end_date": ed}
        )

p(f"{len(exams)} Exams + ClassExam entries")

# ─────────────────────────────────────────────────────────────
# 18. GRADE RULES
# ─────────────────────────────────────────────────────────────
grade_rules = [
    ("A+", 5.0, 80, 100, "Excellent"),
    ("A",  4.0, 70,  79, "Very Good"),
    ("A-", 3.5, 60,  69, "Good"),
    ("B",  3.0, 50,  59, "Satisfactory"),
    ("C",  2.0, 40,  49, "Average"),
    ("D",  1.0, 33,  39, "Below Average"),
    ("F",  0.0,  0,  32, "Failed"),
]
for gname, gpa, mn, mx, rem in grade_rules:
    Graderule.objects.get_or_create(
        grade_name=gname,
        academic_year=acad_year,
        defaults={"gpa": gpa, "min_mark": mn, "max_mark": mx, "remarks": rem}
    )
p("Grade Rules")

# ─────────────────────────────────────────────────────────────
# 19. SUBJECT MARKS  (CQ + MCQ + Practical per student per exam)
# ─────────────────────────────────────────────────────────────
# We temporarily disconnect the signal that auto-calculates StudentResult
# so we can insert marks in bulk; we'll trigger it manually at the end.
from django.db.models.signals import post_save as _ps
from exam.models import update_student_result_on_mark_save

_ps.disconnect(update_student_result_on_mark_save, sender=Subject_mark)

mark_count = 0

for student in student_profiles:
    cc = student.class_id
    if not cc:
        continue
    cgc = cc.class_group_id

    # Get all SubjectConfigs for this student's class-group
    sub_configs = SubjectConfig.objects.filter(class_id=cgc)

    for exam in exams:
        for sc in sub_configs:
            # Determine which mark_configs exist for this sc
            mcs = Mark_config.objects.filter(subject_conf_id=sc, class_id=cgc)
            for mc in mcs:
                # Vary marks: some students high, some medium, some fail one subject
                max_m = mc.mark
                pass_m = mc.pass_mark

                # Student index drives performance tier
                stu_idx = student_profiles.index(student)
                tier = stu_idx % 5   # 0=excellent, 1=good, 2=avg, 3=pass, 4=fail one

                if tier == 0:
                    mark_val = rng.uniform(max_m * 0.82, max_m * 0.98)
                elif tier == 1:
                    mark_val = rng.uniform(max_m * 0.70, max_m * 0.81)
                elif tier == 2:
                    mark_val = rng.uniform(max_m * 0.55, max_m * 0.69)
                elif tier == 3:
                    mark_val = rng.uniform(pass_m, max_m * 0.54)
                else:
                    # Fail one subject deliberately (only for first subject in first exam)
                    if sc.subject_Serial == 1 and exam == exams[0]:
                        mark_val = rng.uniform(0, pass_m - 1)
                    else:
                        mark_val = rng.uniform(pass_m, max_m * 0.60)

                mark_val = round(min(max(mark_val, 0), max_m), 2)

                Subject_mark.objects.get_or_create(
                    examname_id=exam,
                    student_id=student,
                    mark_id=mc,
                    defaults={
                        "mark": mark_val,
                        "academic_year": acad_year,
                        "check_mark": True,
                    }
                )
                mark_count += 1

p(f"{mark_count} Subject_marks inserted")

# Reconnect signal then bulk-calculate StudentResult
_ps.connect(update_student_result_on_mark_save, sender=Subject_mark)

result_count = 0
for student in student_profiles:
    for exam in exams:
        sr, _ = StudentResult.objects.get_or_create(
            student=student,
            exam=exam,
            defaults={"academic_year": acad_year}
        )
        sr.calculate_result()
        sr.save()
        result_count += 1

p(f"{result_count} StudentResults calculated")

# ─────────────────────────────────────────────────────────────
# 20. FEES SETUP
# ─────────────────────────────────────────────────────────────
from crucial.models import (
    FeeHead, Feetype, Fee_month, Fee_package,
    Fees_name, Fees, PartialPayment,
)

# FeeHeads
fee_heads_data = ["Tuition Fee", "Admission Fee", "Exam Fee", "Library Fee", "Sports Fee"]
fee_heads = {}
for fh_name in fee_heads_data:
    fh, _ = FeeHead.objects.get_or_create(name=fh_name)
    fee_heads[fh_name] = fh

p("FeeHeads")

# Fee months
months = ["January","February","March","April","May","June",
          "July","August","September","October","November","December"]
fee_months = {m: Fee_month.objects.get_or_create(name=m)[0] for m in months}
p("Fee_months")

# Feetype: one per FeeHead
fee_types = {}
for fh_name, fh_obj in fee_heads.items():
    schedule = "Monthly" if fh_name == "Tuition Fee" else "Annually"
    ft, _ = Feetype.objects.get_or_create(
        fee_head=fh_obj,
        fee_Schedule=schedule,
        defaults={
            "status": "Active",
            "late_fee_percentage": Decimal("5.00"),
            "description": fh_name,
            "created_by": admin,
        }
    )
    fee_types[fh_name] = ft
p("Feetype")

# Fee_package: amount per ClassGroupConfig per Feetype
fee_amounts = {
    "Tuition Fee":   {("Class 6",""):500,  ("Class 7",""):550,  ("Class 8",""):600,
                      ("Class 9","Science"):700, ("Class 9","Arts"):650,
                      ("Class 9","Commerce"):650, ("Class 10","Science"):750,
                      ("Class 10","Arts"):700, ("Class 10","Commerce"):700},
    "Admission Fee": 2000,
    "Exam Fee":      1000,
    "Library Fee":   300,
    "Sports Fee":    200,
}

fee_packages = {}
for cgc in all_cgcs:
    cn = cgc.class_id.name
    gn = cgc.group_id.name if cgc.group_id else ""
    for fh_name, ft in fee_types.items():
        amounts = fee_amounts[fh_name]
        if isinstance(amounts, dict):
            amt = amounts.get((cn, gn), 500)
        else:
            amt = amounts
        fp, _ = Fee_package.objects.get_or_create(
            student_class=cgc,
            fees_type=ft,
            academic_year=acad_year,
            defaults={"amount": Decimal(str(amt)), "created_by": admin}
        )
        fee_packages[(cgc.id, fh_name)] = fp
p("Fee_packages")

# Fees_name: one entry per month (for Monthly), or one annual entry
fees_names = {}
for cgc in all_cgcs:
    for fh_name, ft in fee_types.items():
        fp = fee_packages.get((cgc.id, fh_name))
        if not fp:
            continue
        if ft.fee_Schedule == "Monthly":
            for mname, fm in fee_months.items():
                fn, _ = Fees_name.objects.get_or_create(
                    fees_title=f"{mname} - {fh_name} - {cgc}",
                    defaults={
                        "fees_type": ft,
                        "fee_amount_id": fp,
                        "month": fm,
                        "status": "Active",
                        "startdate": datetime.date(int(YEAR), months.index(mname)+1, 1),
                        "enddate":   datetime.date(int(YEAR), months.index(mname)+1, 15),
                        "academic_year": acad_year,
                        "created_by": admin,
                    }
                )
                fees_names[(cgc.id, fh_name, mname)] = fn
        else:
            fm = fee_months["January"]
            fn, _ = Fees_name.objects.get_or_create(
                fees_title=f"Annual - {fh_name} - {cgc}",
                defaults={
                    "fees_type": ft,
                    "fee_amount_id": fp,
                    "month": fm,
                    "status": "Active",
                    "startdate": datetime.date(int(YEAR), 1, 1),
                    "enddate":   datetime.date(int(YEAR), 12, 31),
                    "academic_year": acad_year,
                    "created_by": admin,
                }
            )
            fees_names[(cgc.id, fh_name, "Annual")] = fn
p("Fees_name entries")

# ─────────────────────────────────────────────────────────────
# 21. FEES RECORDS  (paid / unpaid / partial per student)
# ─────────────────────────────────────────────────────────────
# Tier based on student index (mod 3):
#   0 → fully paid  (all months)
#   1 → fully unpaid
#   2 → partial  (paid half the months / half amount)

fee_count = 0
partial_count = 0

for stu_idx, student in enumerate(student_profiles):
    cc = student.class_id
    if not cc:
        continue
    cgc = cc.class_group_id
    tier = stu_idx % 3   # 0=paid, 1=unpaid, 2=partial
    fm_jan = fee_months["January"]

    for fh_name, ft in fee_types.items():
        if ft.fee_Schedule == "Monthly":
            target_months = months  # all 12
        else:
            target_months = ["Annual"]

        fp = fee_packages.get((cgc.id, fh_name))
        if not fp:
            continue

        for mkey in target_months:
            fn = fees_names.get((cgc.id, fh_name, mkey))
            if not fn:
                continue

            amount = fp.amount
            fm_obj = fee_months.get(mkey, fm_jan)

            # Determine initial status
            if tier == 0:
                status = "paid"
            elif tier == 1:
                status = "unpaid"
            else:
                # partial: pay only first 6 months fully, rest partial
                mi = months.index(mkey) if mkey in months else 0
                if mi < 6:
                    status = "paid"
                else:
                    status = "partial"

            fee, created = Fees.objects.get_or_create(
                student_id=student,
                feetype_id=fn,
                month_id=fm_obj,
                academic_year=acad_year,
                defaults={
                    "amount": amount,
                    "discount_amount": Decimal("0.00"),
                    "late_amount": Decimal("0.00"),
                    "status": status,
                    "payment_method": "cash",
                    "is_enable": True,
                    "created_by": admin,
                }
            )

            if created:
                fee_count += 1
                if status == "paid":
                    PartialPayment.objects.create(
                        fee=fee,
                        amount=amount,
                        created_by=admin,
                    )
                elif status == "partial":
                    paid_partial = round(amount / 2, 2)
                    PartialPayment.objects.create(
                        fee=fee,
                        amount=paid_partial,
                        created_by=admin,
                    )
                    partial_count += 1

p(f"{fee_count} Fee records  |  {partial_count} Partial payments")

# ─────────────────────────────────────────────────────────────
# 22. NOTICE BOARD
# ─────────────────────────────────────────────────────────────
from crucial.models import Notice

notices = [
    ("Annual Sports Day Notice",
     "The Annual Sports Day will be held on 15 March 2025. All students must participate.",
     datetime.date(int(YEAR), 2, 20), datetime.date(int(YEAR), 3, 20)),
    ("Exam Schedule Published",
     "The 1st Term Exam schedule has been published. Please collect from the office.",
     datetime.date(int(YEAR), 2, 25), datetime.date(int(YEAR), 3, 15)),
    ("Fee Submission Reminder",
     "Students are reminded to submit their monthly fees by the 10th of each month.",
     datetime.date(int(YEAR), 3, 1),  datetime.date(int(YEAR), 12, 31)),
    ("School Closed – Eid Holiday",
     "School will remain closed from 30 March to 5 April on the occasion of Eid-ul-Fitr.",
     datetime.date(int(YEAR), 3, 25), datetime.date(int(YEAR), 4, 6)),
    ("New Academic Session Begins",
     "Welcome to the new academic session 2025-26. Classes begin on 1 January 2025.",
     datetime.date(int(YEAR), 1, 1),  datetime.date(int(YEAR), 1, 31)),
]

for title, desc, date_, exp in notices:
    Notice.objects.get_or_create(
        notice_title=title,
        defaults={
            "date": date_,
            "notice_description": desc,
            "expire_date": exp,
            "academic_year": acad_year,
            "created_by": admin,
        }
    )
p(f"{len(notices)} Notices")

# ─────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("  SEED COMPLETE — Summary")
print("=" * 60)
print(f"  Academic Year  : {YEAR}")
print(f"  Classes        : {len(class_names)}  ({', '.join(class_names)})")
print(f"  Sections       : {len(section_names)}  ({', '.join(section_names)})")
print(f"  Shifts         : {len(shift_names)}")
print(f"  Groups         : {len(group_names)}")
print(f"  Subjects       : {len(subjects)}")
print(f"  Mark Types     : CQ, MCQ, Practical")
print(f"  Teachers       : {len(teachers)}")
print(f"  Students       : {len(student_profiles)}")
print(f"  Parents        : {len(parents_list)}")
print(f"  Exams          : {len(exams)}")
print(f"  Subject Marks  : {mark_count}")
print(f"  Student Results: {result_count}")
print(f"  Fee Records    : {fee_count}")
print(f"  Partial Payments: {partial_count}")
print(f"  Notices        : {len(notices)}")
print()
print("  LOGIN CREDENTIALS")
print("  ─────────────────────────────────────")
print("  Admin   :  admin        / admin1234")
print("  Teacher :  teacher_t001 / teacher1234")
print("  Student :  student001   / student1234")
print("  Parent  :  parent_p001  / parent1234")
print("=" * 60)