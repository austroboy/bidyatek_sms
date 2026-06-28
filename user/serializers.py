from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from shared.models import CustomUser 
from django.contrib.auth.models import Permission, Group
from .models import StaffProfile,StudentProfile,Student,Parent,ParentProfile
from django.db import transaction


class UserLSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'  # Return all user fields

class StaffLProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProfile
        fields = '__all__'

class StudentLProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = '__all__'

class ParentLProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentProfile
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    role = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True)
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    user_data = serializers.JSONField(read_only=True)  # To hold full user data

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        # Determine role and fetch profile data
        role = None
        profile_data = None

        if user.groups.filter(name='teacher').exists():
            try:
                staff_profile = StaffProfile.objects.get(staff_field=user)
                profile_data = StaffLProfileSerializer(staff_profile).data
                role = staff_profile.role.name
            except StaffProfile.DoesNotExist:
                role = 'staff'
        elif user.groups.filter(name='student').exists():
            try:
                student_profile = StudentProfile.objects.get(student_field=user)
                profile_data = StudentLProfileSerializer(student_profile).data
                role = 'Student'
            except StudentProfile.DoesNotExist:
                profile_data = None
        elif user.groups.filter(name='parent').exists():
            try:
                parent_profile = ParentProfile.objects.get(parent_field=user)
                profile_data = ParentLProfileSerializer(parent_profile).data
                role = 'Parent'
            except ParentProfile.DoesNotExist:
                profile_data = None

        refresh = RefreshToken.for_user(user)

        # Serialize user data
        user_data = UserLSerializer(user).data

        return {
            "username": user.username,
            "role": role,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user_data": user_data,  # Full user details
            "profile_data": profile_data,  # Additional profile details
        }

# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     role = serializers.CharField(read_only=True)
#     password = serializers.CharField(write_only=True)
#     access_token = serializers.CharField(read_only=True)
#     refresh_token = serializers.CharField(read_only=True)

#     def validate(self, data):
#         username = data.get("username")
#         password = data.get("password")

#         user = authenticate(username=username, password=password)
#         if not user:
#             raise serializers.ValidationError("Invalid username or password.")

#         if not user.is_active:
#             raise serializers.ValidationError("User account is disabled.")

#         role = None
#         if user.groups.filter(name='teacher').exists():
#             try:
#                 staff_profile = user.staff_profile
#                 role = staff_profile.role.name
#             except StaffProfile.DoesNotExist:
#                 role = 'staff' 
#         elif user.groups.filter(name='student').exists():
#             role = 'Student'
#         elif user.groups.filter(name='parent').exists():
#             role = 'Parent'

#         refresh = RefreshToken.for_user(user)

#         return {
#             "username": user.username,
#             "role": role,
#             "access_token": str(refresh.access_token),
#             "refresh_token": str(refresh),
#         }



class PermissionList_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class Group_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class StudentProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(source='student_field.avatar', read_only=True)
    name = serializers.CharField(source='student_field.name', read_only=True)
    class_id = serializers.SerializerMethodField()  # Return class name
    parent_id = serializers.SerializerMethodField()  # Return parent name
    admission_year_id = serializers.SerializerMethodField()  # Return admission year
    academic_session_year = serializers.SerializerMethodField()  # Return session year

    class Meta:
        model = StudentProfile
        fields = ['id', 'student_field','name', 'avatar', 'class_id', 'parent_id', 'roll_no', 'admission_year_id', 'academic_session_year']

    def get_class_id(self, obj):
        return obj.class_id.class_group_id.class_id.name if obj.class_id else None  # Return class name

    def get_parent_id(self, obj):
        return obj.parent_id.name if obj.parent_id else None  # Return parent's name

    def get_admission_year_id(self, obj):
        return obj.admission_year_id.name if obj.admission_year_id else None  # Return admission year name

    def get_academic_session_year(self, obj):
        return f"{obj.academic_session_year.start_year}-{obj.academic_session_year.end_year}" if obj.academic_session_year else None
    



class ParentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentProfile
        fields = '__all__'
        read_only_fields = '__all__'

class ParentSerializer(serializers.ModelSerializer):
    parent_profile = ParentProfileSerializer(read_only=True)
    
    class Meta:
        model = Parent
        fields = ['id', 'name', 'phone_number', 'email', 'parent_profile']
        read_only_fields = fields

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id', 'name', 'phone_number', 'email', 'dob', 'gender', 
            'religion', 'blood_group', 'avatar', 'present_address', 
            'permanent_address', 'nid', 'rfid'
        ]
        read_only_fields = fields

class StudentAppProfileSerializer(serializers.ModelSerializer):
    student_field = StudentSerializer(read_only=True)
    parent_id = ParentSerializer(read_only=True)
    admission_year_id = serializers.StringRelatedField()
    academic_session_year = serializers.StringRelatedField()
    class_id = serializers.StringRelatedField()

    class Meta:
        model = StudentProfile
        fields = '__all__'
        read_only_fields = fields




class StaffProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(source='staff_field.avatar', read_only=True)  # Get staff avatar
    name = serializers.CharField(source='staff_field.name', read_only=True)
    role = serializers.CharField(source='role.name', read_only=True)  # Get role name

    class Meta:
        model = StaffProfile
        fields = ['id', 'avatar','name', 'designation', 'staff_id_no', 'employee_type', 'role']








# Online serializer #
class StudentUserOSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student  
        fields = ['email', 'phone_number', 'name', 'status', 'nid', 'user_id',
                 'present_address', 'permanent_address', 'disability_info']
        extra_kwargs = {
            'status': {'default': CustomUser.Status.DEACTIVE},
            'email': {'required': False, 'allow_blank': True},  
            'nid': {'required': False, 'allow_null': True},  
            'user_id': {'required': False, 'allow_null': True}, 
            'present_address': {'required': False, 'allow_blank': True},
            'permanent_address': {'required': False, 'allow_blank': True},
            'disability_info': {'required': False, 'allow_blank': True},
        }


class StudentProfileOSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['admission_year_id', 'academic_session_year', 'class_id',
                'birth_certificate_no', 'nationality', 'tc_no', 'village',
                'post_office', 'ps_or_upazilla', 'district', 'status']
        extra_kwargs = {
            'status': {'default': StudentProfile.Status.ONLINE},
            'academic_session_year': {'required': False, 'allow_null': True}, 
            'birth_certificate_no': {'required': False, 'allow_blank': True},  
            'nationality': {'required': False, 'allow_blank': True},
            'tc_no': {'required': False, 'allow_blank': True},
            'village': {'required': False, 'allow_blank': True},
            'post_office': {'required': False, 'allow_blank': True},
            'ps_or_upazilla': {'required': False, 'allow_blank': True},
            'district': {'required': False, 'allow_blank': True},
        }


class ParentUserOSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = ['email', 'phone_number', 'name', 'nid']
        extra_kwargs = {
            'email': {'required': False, 'allow_blank': True}, 
            'phone_number': {'required': False, 'allow_blank': True},
            'nid': {'required': False, 'allow_null': True}, 
        }


class ParentProfileOSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentProfile
        fields = ['father_name', 'father_mobile_no', 'mother_name', 
                'mother_mobile_no', 'relation', 'occupation', 'g_name', 'g_mobile_no']
        extra_kwargs = {
            'father_name': {'required': False, 'allow_blank': True},
            'father_mobile_no': {'required': False, 'allow_blank': True},
            'mother_name': {'required': False, 'allow_blank': True},
            'mother_mobile_no': {'required': False, 'allow_blank': True},
            'relation': {'required': False, 'allow_blank': True},
            'occupation': {'required': False, 'allow_blank': True},
            'g_name': {'required': False, 'allow_blank': True},
            'g_mobile_no': {'required': False, 'allow_blank': True},
        }


class CombinedCreateSerializer(serializers.Serializer):
    student_user = StudentUserOSerializer()
    student_profile = StudentProfileOSerializer()
    parent_user = ParentUserOSerializer()
    parent_profile = ParentProfileOSerializer()

    def create(self, validated_data):
        with transaction.atomic():
            student_user_data = validated_data.pop('student_user', {})
            student_profile_data = validated_data.pop('student_profile', {})
            parent_user_data = validated_data.pop('parent_user', {})
            parent_profile_data = validated_data.pop('parent_profile', {})

            if not student_user_data:
                raise serializers.ValidationError({"student_user": "This field is required."})
            if not student_profile_data:
                raise serializers.ValidationError({"student_profile": "This field is required."})
            if not parent_user_data:
                raise serializers.ValidationError({"parent_user": "This field is required."})
            if not parent_profile_data:
                raise serializers.ValidationError({"parent_profile": "This field is required."})

            student_user_data.pop('status', None)
            student_user = Student.objects.create(
                **student_user_data,
                status=CustomUser.Status.DEACTIVE 
            )

            student_profile_data.pop('status', None)
            student_profile = StudentProfile.objects.create(
                student_field=student_user,
                **student_profile_data,
                status=StudentProfile.Status.ONLINE
            )

            parent_user = Parent.objects.create(**parent_user_data)

            parent_profile = ParentProfile.objects.create(
                parent_field=parent_user,
                **parent_profile_data
            )

            return {
                'student_user': student_user,
                'student_profile': student_profile,  
                'parent_user': parent_user,
                'parent_profile': parent_profile
            }
