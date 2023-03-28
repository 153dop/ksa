from django.db import models

# Create your models here.

# Classe "Question", contient son intitulé, ses variables ainsi que les valeurs possibles que peuvent prendre les variables
class Question(models.Model):
    title = models.TextField()
    liste_variable = models.JSONField()
    liste_value = models.JSONField()
    comment = models.TextField(null=True)
    explanation = models.TextField(null=True)

    def __str__(self):
        return self.title

# Classe "Reponse", contient l'utilisateur, la bonne réponse, la réponse donnée, l'identifiant de la question et le résultat
class Response(models.Model):
    # user = models.CharField(max_length=30,null=True)
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True)
    correct_answer = models.FloatField(null=True)
    given_answer = models.FloatField(null=True, blank=True)
    # question_id = models.ForeignKey(Question, on_delete=models.CASCADE,null=True)
    result = models.BooleanField(null=True)

# Classe dont le but est d'avoir une variable "globale" par utilisateur
class VariablesUser(models.Model) :
    user = models.CharField(max_length=30)
    # i_indent = models.IntegerField()
    bool_tirage_question = models.BooleanField()
    question_infos = models.JSONField()

    # def add_indent(self):
    #     self.i_indent += 1
    # def reset_indent(self):
    #     self.i_indent = 0
    def reset_bool_tirage(self):
        self.bool_tirage_question = True