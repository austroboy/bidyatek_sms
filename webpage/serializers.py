from rest_framework import serializers
from .models import *
from crucial.models import Notice,Download

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'


class SchoolHistoryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolHistoryImage
        fields = ['id', 'image']

class SchoolHistorySerializer(serializers.ModelSerializer):
    images = SchoolHistoryImageSerializer(many=True, read_only=True)

    class Meta:
        model = School_history
        fields = ['id', 'heading', 'text', 'img', 'status', 'images']

class MsgFromHeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Msg_from_head
        fields = '__all__'

class MsgFromOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Msg_from_other
        fields = '__all__'

class ImportantLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportantLink
        fields = '__all__'

class CredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credentials
        fields = '__all__'

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = '__all__'

class IconicStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Iconic_Student
        fields = '__all__'

class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = '__all__'

class VideoGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Video_Gallery
        fields = '__all__'

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = '__all__'

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = '__all__'

class LinkNameSerializer(serializers.ModelSerializer):
    page_link = LinkSerializer(many=True, read_only=True)

    class Meta:
        model = Link_name
        fields = ['id', 'name', 'page_link']

class CommitteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Committee
        fields = '__all__'

class DownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Download
        fields = '__all__'


class WelcomeSpeechSerializer(serializers.ModelSerializer):
    class Meta:
        model = Welcome_Speech
        fields = '__all__'


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'

class SiteColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site_color
        fields = '__all__'

class SeatInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat_info
        fields = '__all__'

class DressCodeSerializer(serializers.ModelSerializer):
    dress_image = serializers.ImageField(use_url=True)  # Ensures URL is returned for the image

    class Meta:
        model = Dress_code
        fields = '__all__'

class PublicMsgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Public_msg
        fields = ['name', 'subject', 'email_id', 'phone_no', 'msg']

    def validate_subject(self, value):
        """Allow subject to be empty or None"""
        return value if value else None

    def validate_email_id(self, value):
        """Allow email_id to be empty or None"""
        return value if value else None