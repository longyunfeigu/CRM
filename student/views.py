from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import os
import json
import time

from my_crm import models

# Create your views here.
def stu_my_classes(request):
    return render(request, 'student/my_classes.html')

def studyrecords(request, enroll_id):
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)

    return render(request, 'student/studyrecords.html', {'enroll_obj': enroll_obj,})

def homework_detail(request, studyrecord_id):
    studyrecord_obj = models.StudyRecord.objects.get(id=studyrecord_id)
    homework_path = "{base_dir}/{class_id}/{course_record_id}/{studyrecord_id}/" \
        .format(base_dir=settings.HOMEWORK_DATA,
                class_id=studyrecord_obj.student.enrolled_class_id,
                course_record_id=studyrecord_obj.course_record_id,
                studyrecord_id=studyrecord_obj.id
                )
    if not os.path.exists(homework_path):
        os.makedirs(homework_path, exist_ok=True)
    if request.method == 'POST':
        for k, file_obj in request.FILES.items():
            with open(os.path.join(homework_path, file_obj.name), 'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)

    file_list = []
    for file_name in os.listdir(homework_path):
        file_path = os.path.join(homework_path, file_name)
        modify_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(os.stat(file_path).st_mtime))
        file_list.append([file_name, os.stat(file_path).st_size//1024, modify_time])
    if request.method == 'POST':
        return HttpResponse(json.dumps({"status": 0, "msg": "file upload success"}))

    return render(request, 'student/homework_detail.html', {'studyrecord_obj': studyrecord_obj,
                                                            'file_list': file_list})