import logging
import os
from celery import shared_task
from django_tenants.utils import schema_context
from user.models import Parent, ParentProfile, Student, StudentProfile
from core.models import ClassConfig, ClassGroupConfig, AcademicSession, Admission_Year
from tablib import Dataset
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
import random
from shared.models import CustomUser

# Ensure the log file exists
log_file_path = '/home/BIDYATek/FSv01/debug.log'

if not os.path.exists(log_file_path):
    open(log_file_path, 'w').close()  # Create the file if it doesn't exist

# Configure logging to append to the file
logging.basicConfig(
    filename=log_file_path,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_unique_number():
    attempts = 0
    while attempts < 10:
        unique_number = random.randint(10**10, 10**11 - 1)
        if not CustomUser.objects.filter(user_id=unique_number).exists():
            return unique_number
        attempts += 1
    raise Exception("Failed to generate a unique user_id after 10 attempts")

@shared_task
def process_student_import(schema_name, file_path):
    """
    Celery task to process student data import within a given tenant schema.
    Logs errors to a file for unmatched ClassConfig and roll_no that fails to save.
    """
    with schema_context(schema_name):
        dataset = Dataset()
        with open(file_path, 'rb') as file:
            imported_data = dataset.load(file.read(), format='xlsx')

        student_profiles_to_create = []

        for data in imported_data:
            try:
                # Extract data from the row
                name = data[2]
                if not name:
                    continue  # Skip this row due to missing name

                phone_number = str(data[18]) if data[18] else None
                if phone_number and not phone_number.startswith("0"):
                    phone_number = "0" + phone_number

                random_value = generate_unique_number()
                password_value = phone_number if phone_number else random_value
                hashed_password = make_password(password_value)

                # Ensure Parent Exists
                parent_user_instance, created = Parent.objects.get_or_create(
                    phone_number=phone_number,
                    defaults={
                        "username": password_value,
                        "name": data[17],
                        "user_id": random_value,
                        "password": hashed_password
                    }
                )

                # Ensure ParentProfile Exists
                ParentProfile.objects.get_or_create(
                    parent_field=parent_user_instance,
                    defaults={
                        "relation": data[19],
                        "father_name": data[20],
                        "father_mobile_no": data[21],
                        "mother_name": data[22],
                        "mother_mobile_no": data[23],
                        "g_name": data[17],
                        "g_mobile_no": phone_number,
                    }
                )

                # Ensure Student Exists
                student_user_instance, created = Student.objects.get_or_create(
                    user_id=data[0],
                    defaults={
                        "username": data[0],
                        "avatar": data[1],
                        "phone_number": data[3],
                        "name": data[2],
                        "gender": data[6],
                        "religion": data[8],
                        "dob": data[5],
                        "blood_group": data[7],
                        "email": data[4],
                        "rfid": data[9],
                        "user_id": data[0],
                        "present_address": data[26],
                        "password": hashed_password
                    }
                )

                # Ensure Academic Session Exists
                academic_session_instance = None
                academic_session_year = data[16]
                if academic_session_year:
                    start_year, end_year = academic_session_year.split('-')
                    academic_session_instance = AcademicSession.objects.get(
                        start_year=start_year,
                        end_year=end_year
                    )

                admission_year_instance = Admission_Year.objects.get(name=data[15])

                # Check ClassGroupConfig and ClassConfig
                try:
                    class_group_instance = ClassGroupConfig.objects.get(
                        class_id__name=data[10], group_id__name=data[11]
                    )
                    class_config_instance = ClassConfig.objects.get(
                        class_group_id=class_group_instance,
                        section_id__name=data[12],
                        shift_id__name=data[13]
                    )
                except ClassGroupConfig.DoesNotExist:
                    logger.error(f"ClassGroupConfig not found for class: {data[10]}, group: {data[11]}")
                    continue
                except ClassConfig.DoesNotExist:
                    logger.error(f"ClassConfig not found for class group: {data[10]}-{data[11]}, section: {data[12]}, shift: {data[13]}")
                    continue

                # Ensure StudentProfile Exists
                if not StudentProfile.objects.filter(student_field=student_user_instance).exists():
                    student_profile = StudentProfile(
                        student_field=student_user_instance,
                        class_id=class_config_instance,
                        roll_no=data[14],
                        version=data[24],
                        name_tag=data[25],
                        admission_year_id=admission_year_instance,
                        academic_session_year=academic_session_instance,
                        parent_id=parent_user_instance,
                    )
                    student_profiles_to_create.append(student_profile)

            except IntegrityError as e:
                logger.error(f"IntegrityError for roll_no {data[14]}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error for roll_no {data[14]}: {e}")

        # Bulk insert for performance improvement
        try:
            StudentProfile.objects.bulk_create(student_profiles_to_create, ignore_conflicts=True)
            logger.info(f"{len(student_profiles_to_create)} StudentProfiles created successfully.")
        except Exception as e:
            logger.error(f"Failed to bulk create StudentProfiles: {e}")

    # Clean up the temporary file
    os.remove(file_path)
    return "Data import complete for tenant: {}".format(schema_name)
