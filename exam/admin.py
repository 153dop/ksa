from django.contrib import admin

# Register your models here.

from .models import Question, Response, Score, VariablesUser, Student
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.shortcuts import render
from django.urls import path
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages

import csv


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'liste_variable', 'liste_value', 'comment')

class ResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'correct_answer', 'given_answer', 'question_id', 'question_title', 'result')
    list_filter = ('user', 'question_id', 'result')


# Action permettant l'export des scores sélectionnés dans un fichier csv
def export_scores(modeladmin, request, queryset):
    http_response = HttpResponse(content_type='text/csv')
    http_response['Content-Disposition'] = 'attachment; filename="scores.csv"'
    writer = csv.writer(http_response, delimiter=";")
    writer.writerow(['Student', 'Score', 'Result', 'Date end test', 'Question 1', 'Correct answer 1', 'Given answer 1',
                     'Result 1', 'Question 2', 'Correct answer 2', 'Given answer 2', 'Result 2', 'Question 3',
                     'Correct answer 3', 'Given answer 3', 'Result 3', 'Question 4', 'Correct answer 4',
                     'Given answer 4', 'Result 4', 'Question 5', 'Correct answer 5', 'Given answer 5', 'Result 5',
                     'Question 6', 'Correct answer 6', 'Given answer 6', 'Result 6', 'Question 7', 'Correct answer 7',
                     'Given answer 7', 'Result 7', 'Question 8', 'Correct answer 8', 'Given answer 8', 'Result 8',
                     'Question 9', 'Correct answer 9', 'Given answer 9', 'Result 9', 'Question 10', 'Correct answer 10',
                     'Given answer 10', 'Result 10', 'Question 11', 'Correct answer 11', 'Given answer 11', 'Result 11',
                     'Question 12', 'Correct answer 12', 'Given answer 12', 'Result 12', 'Question 13',
                     'Correct answer 13', 'Given answer 13', 'Result 13', 'Question 14', 'Correct answer 14',
                     'Given answer 14', 'Result 14', 'Question 15', 'Correct answer 15', 'Given answer 15', 'Result 15',
                     'Question 16', 'Correct answer 16', 'Given answer 16', 'Result 16', 'Question 17',
                     'Correct answer 17', 'Given answer 17', 'Result 17', 'Question 18', 'Correct answer 18',
                     'Given answer 18', 'Result 18', 'Question 19', 'Correct answer 19', 'Given answer 19', 'Result 19',
                     'Question 20', 'Correct answer 20', 'Given answer 20', 'Result 20', 'Question 22',
                     'Correct answer 21', 'Given answer 21', 'Result 21', 'Question 22', 'Correct answer 22',
                     'Given answer 22', 'Result 22', 'Question 23', 'Correct answer 23', 'Given answer 23', 'Result 23',
                     'Question 24', 'Correct answer 24', 'Given answer 24', 'Result 24'])
    scores = queryset.values_list('user', 'score', 'final_result', 'date_fin_test')
    for score in scores:
        row = list(score)
        for i in range(1,25):
            response_question = Response.objects.filter(user=score[0]).filter(question_id=i).get()
            questions_user = [response_question.question_title, response_question.correct_answer, response_question.given_answer, response_question.result]
            row = row + questions_user
        writer.writerow(row)
    messages.success(request, 'Fichier créé et téléchargé.')
    return http_response
export_scores.short_description = 'Exporter les scores dans un fichier csv'

class ScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'final_result', 'date_fin_test')
    actions = [export_scores,]

class VariablesUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'i_indent', 'bool_tirage_exam', 'count_good_answers', 'list_q_exam')

class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam_access')

class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = "Students"

# Tentative de création d'un filtre pour voir quels utilisateurs avaient accès à l'examen
class ExamAccessFilter(admin.SimpleListFilter):
    title = "Accès à l'examen"
    parameter_name = "exam_access"
    def lookups(self, request, model_admin):
        return [("authorized", "Accès autorisé"),]
    def queryset(self, request, queryset):
        if self.value() == 'authorized':
            return queryset.filter(student=True)

# Action qui permet de donner l'accès à l'examen pour les utilisateurs sélectionnés
def give_exam_access(modeladmin, request, queryset):
    for user in queryset:
        Student.objects.update_or_create(user = user)
        student = Student.objects.get(user = user)
        student.exam_access = True
        student.save()
give_exam_access.short_description = "Donner l'accès à  l'examen"

# Action qui permet d'enlever l'accès à l'examen pour les utilisateurs sélectionnés
def delete_exam_access(modeladmin, request, queryset):
    for user in queryset:
        Student.objects.update_or_create(user = user)
        student = Student.objects.get(user = user)
        student.exam_access = False
        student.save()
delete_exam_access.short_description = "Enlever l'accès à  l'examen"

# Affichage admin customisé pour l'utilisateur pour permettre l'upload d'un fichier csv
class CustomizedUserAdmin (UserAdmin):
    inlines = (StudentInline,)
    actions = [give_exam_access, delete_exam_access,]

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv), ]
        return new_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]

            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)

            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")
            print(csv_data)

            for x in csv_data:
                fields = x.split(";")
                print(fields)

                User.objects.update_or_create(username = fields[0], is_staff = False)

                new_user = User.objects.get(username=fields[0])
                new_user.set_password(fields[1])
                new_user.exam_access = False
                group = Group.objects.get_or_create(name=fields[2])
                new_user.groups.add(group[0])
                new_user.save()

            messages.success(request, 'Nouveaux profils ajoutés.')
            return HttpResponseRedirect(request.path_info)

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_upload.html", data)

# Modèle form pour l'upload du fichier csv
class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()





# Affichage des modèles dans la partie administration du site
admin.site.register(Question, QuestionAdmin)
admin.site.register(Response, ResponseAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(VariablesUser, VariablesUserAdmin)
admin.site.register(Student, StudentAdmin)

# Pour le modèle user
admin.site.unregister(User)
admin.site.register(User, CustomizedUserAdmin)

