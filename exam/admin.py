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
from django.urls import reverse
from django.contrib.admin import SimpleListFilter

import csv


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'liste_variable', 'liste_value', 'comment')

class ResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'correct_answer', 'given_answer', 'question_id', 'result')


# Action permettant l'export des scores sélectionnés dans un fichier csv
def export_scores(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="scores.csv"'
    writer = csv.writer(response, delimiter = ";")
    writer.writerow(['Eleve', 'Score', 'Resultat', 'Date fin test'])
    scores = queryset.values_list('user', 'score', 'final_result', 'date_fin_test')
    for score in scores:
        writer.writerow(score)
    messages.success(request, 'Fichier créé et téléchargé.')
    return response
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

