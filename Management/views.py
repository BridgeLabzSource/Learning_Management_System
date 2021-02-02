from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from .models import Course
from django.utils.decorators import method_decorator
from rest_framework.generics import GenericAPIView
from .serializers import CourseSerializer

import sys
sys.path.append('..')
from Auth.permissions import isAdmin
from Auth.middlewares import SessionAuthentication
from LMS.loggerConfig import log


@method_decorator(SessionAuthentication, name='dispatch')
class AddCourseAPIView(GenericAPIView):
    serializer_class = CourseSerializer
    permission_classes = [isAdmin]

    def post(self, request):
        """This API is used to add course by the admin
        @param request: course_name
        @return: save course in the database
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except IntegrityError:
            log.info('duplicate course entry is blocked')
            return Response({'response': f"{serializer.data.get('course_name')} is already present"},status=status.HTTP_400_BAD_REQUEST)
        log.info('Course is added')
        return Response({'response': f"{serializer.data.get('course_name')} is added in course"}, status=status.HTTP_201_CREATED)


@method_decorator(SessionAuthentication, name='dispatch')
class AllCoursesAPIView(GenericAPIView):
    serializer_class = CourseSerializer
    permission_classes = [isAdmin]
    queryset = Course.objects.all()

    def get(self, request):
        """This API is used to retrieve all courses by admin
        @return: returns all courses
        """
        serializer = self.serializer_class(self.queryset.all(), many=True)
        log.info('All courses are retrieved')
        return Response({'response': serializer.data}, status=status.HTTP_200_OK)


@method_decorator(SessionAuthentication, name='dispatch')
class UpdateCourseAPIView(GenericAPIView):
    permission_classes = [isAdmin]
    serializer_class = CourseSerializer

    def put(self, request, id):
        try:
            course = Course.objects.get(id=id)
        except Course.DoesNotExist:
            log.info('course not found')
            return Response({'response': 'Course with given id does not exist'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(instance=course, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
            return Response({'response': 'Course is updated'}, status=status.HTTP_200_OK)
        except IntegrityError:
            log.info('duplicate course entry is blocked')
            return Response({'response': f"{serializer.data.get('course_name')} is already present"},
                            status=status.HTTP_400_BAD_REQUEST)


@method_decorator(SessionAuthentication, name='dispatch')
class DeleteCourseAPIView(GenericAPIView):
    serializer_class = CourseSerializer
    permission_classes = [isAdmin]

    def delete(self, request, id):
        """This API is used to delete course by id by admin
        @return: deletes course from database
        """
        try:
            course = Course.objects.get(id=id)
            course.delete()
            return Response({'response': f"{course.course_name} is deleted"})
        except Course.DoesNotExist:
            log.info("course not found")
            return Response({'response': 'Course not found with this id'})

