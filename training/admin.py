from django.contrib import admin

# Register your models here.

from .models import Question, VariablesUser


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'liste_variable', 'liste_value', 'comment', 'explanation')

# class ResponseAdmin(admin.ModelAdmin):
#     list_display = ('user', 'correct_answer', 'given_answer', 'question_id', 'result')
#
# class ScoreAdmin(admin.ModelAdmin):
#     list_display = ('user', 'score', 'final_result', 'date_fin_test')
#
class VariablesUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'bool_tirage_question', 'question_infos')

# Affichage des modèles dans la partie administration du site
admin.site.register(Question, QuestionAdmin)
# admin.site.register(Response, ResponseAdmin)
# admin.site.register(Score, ScoreAdmin)
admin.site.register(VariablesUser, VariablesUserAdmin)