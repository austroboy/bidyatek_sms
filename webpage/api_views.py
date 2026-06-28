from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from .models import *
from .serializers import *
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

class BannerListAPIView(GenericAPIView, ListModelMixin):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class SchoolHistoryListAPIView(GenericAPIView, ListModelMixin):
    queryset = School_history.objects.prefetch_related('images').all()
    serializer_class = SchoolHistorySerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
class MsgFromHeadListAPIView(GenericAPIView, ListModelMixin):
    queryset = Msg_from_head.objects.all()
    serializer_class = MsgFromHeadSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class MsgFromOtherListAPIView(GenericAPIView, ListModelMixin):
    queryset = Msg_from_other.objects.all()
    serializer_class = MsgFromOtherSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class ImportantLinkListAPIView(GenericAPIView, ListModelMixin):
    queryset = ImportantLink.objects.all()
    serializer_class = ImportantLinkSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
class CredentialsListAPIView(GenericAPIView, ListModelMixin):
    queryset = Credentials.objects.all()
    serializer_class = CredentialsSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
class FeatureListAPIView(GenericAPIView, ListModelMixin):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
class IconicStudentListAPIView(GenericAPIView, ListModelMixin):
    queryset = Iconic_Student.objects.all()
    serializer_class = IconicStudentSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class GalleryListAPIView(GenericAPIView, ListModelMixin):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
class VideoGalleryListAPIView(GenericAPIView, ListModelMixin):
    queryset = Video_Gallery.objects.all()
    serializer_class = VideoGallerySerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    

class TestimonialListAPIView(GenericAPIView, ListModelMixin):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
class ContactListAPIView(GenericAPIView, ListModelMixin):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    

class LinkNameListAPIView(GenericAPIView, ListModelMixin):
    queryset = Link_name.objects.prefetch_related('page_link').all()
    serializer_class = LinkNameSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
class LinkListAPIView(GenericAPIView, ListModelMixin):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
class CommitteeListAPIView(GenericAPIView, ListModelMixin):
    queryset = Committee.objects.all()
    serializer_class = CommitteeSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
class WelcomeSpeechListAPIView(GenericAPIView, ListModelMixin):
    queryset = Welcome_Speech.objects.all()
    serializer_class = WelcomeSpeechSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    

class NoticeListAPIView(GenericAPIView, ListModelMixin):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)





class DownloadListAPIView(ListAPIView):
    queryset = Download.objects.all()
    serializer_class = DownloadSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = {
        'class_id': ['exact'],
        'academic_year__name': ['exact'],
        'academic_session_year__start_year': ['exact'],  
        'academic_session_year__end_year': ['exact'],    
        'download_type': ['exact']
    }

class SiteColorAPIView(RetrieveAPIView):
    serializer_class = SiteColorSerializer

    def get(self, request, *args, **kwargs):
        site_color = Site_color.objects.first()  # Get the first Site_color record
        if site_color:
            serializer = self.get_serializer(site_color)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "No site color found"}, status=status.HTTP_404_NOT_FOUND)
    
class SeatInfoListView(ListAPIView):
    queryset = Seat_info.objects.all()
    serializer_class = SeatInfoSerializer

class DressCodeListView(ListAPIView):
    queryset = Dress_code.objects.all()
    serializer_class = DressCodeSerializer

class PublicMsgCreateAPIView(APIView):
    def post(self, request):
        serializer = PublicMsgSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Public message created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)