import datetime

from django.shortcuts import render
from django.http import HttpResponse

import random
import math

from .models import Response, Question, Score, VariablesUser, Student
from .forms import ResponseForm


# Fonction pour l'accueil utilisateur
def home_user(request):
    if str(request.user) == "AnonymousUser":
        return render(request, 'custom_error_page.html', {'erreur': "Il faut être connecté pour passer le mode examen."})
    return render(request, 'home_user.html')


# Fonction qui gère l'examen et son affichage
def exam(request):
    # Si l'utilisateur n'est pas connecté
    if str(request.user) == "AnonymousUser":
        return render(request, 'custom_error_page.html', {'erreur': "Il faut être connecté pour passer le mode examen."})

    Student.objects.update_or_create(user=request.user)
    student = Student.objects.get(user=request.user)
    if not student.exam_access:
        return render(request, 'custom_error_page.html', {'erreur': "Vous n'avez pas accès à l'examen."})

    # Création objet pour le user en cours s'il n'existe pas
    if len((VariablesUser.objects.filter(user=request.user))) == 0:
        variables_user = VariablesUser(user=request.user, i_indent=0, bool_tirage_exam=True, count_good_answers=0,
                                       list_q_exam=[])
        variables_user.save()

    # On crée notre liste de questions pour l'examen
    variables_user = VariablesUser.objects.filter(user=request.user).get()
    variables_user.list_q_exam = create_exam(24, request.user)
    variables_user.bool_tirage_exam = False
    variables_user.save()
    list_exam_questions = VariablesUser.objects.filter(user=request.user).get().list_q_exam



    # Cas pour le lancement du test avec une question "Prêt ? Taper 1."
    if variables_user.i_indent == 0 and request.method == "GET":
        variables_user = VariablesUser.objects.filter(user=request.user).get()
        variables_user.add_indent()
        variables_user.save()
        form = ResponseForm()
        return render(request, 'exam/question.html', {'form': form, 'question': "Prêt ? Taper 1."})

    else:
        if request.method == "POST":
            # On récupère le résultat du formulaire avec cette ligne
            form = ResponseForm(request.POST)

            # On ne sauvegarde pas le premier formulaire car il correspond à la réponse à "Prêt ? Taper 1."
            if variables_user.i_indent == 1:
                variables_user = VariablesUser.objects.filter(user=request.user).get()
                variables_user.add_indent()
                variables_user.save()
                form = ResponseForm()

            # Pour chacun des formulaires correspondants aux réponses aux 22 questions
            elif 1 < variables_user.i_indent < 25:
                # Si le formulaire est "valid"
                if form.is_valid():

                    # On récupère la réponse donnée dans le formulaire avec "cleaned_data" et "get"
                    given_answer = form.cleaned_data.get('given_answer')
                    # On sauvegarde le formulaire
                    form.save()

                    # Si l'utilisateur n'a pas eu le temps de donner une réponse
                    if given_answer is None:
                        reponse_test = Response.objects.latest('id')
                        reponse_test.user = str(request.user)
                        reponse_test.question_id = Question.objects.get(pk=variables_user.i_indent - 1)
                        reponse_test.result = False
                        reponse_test.correct_answer = list_exam_questions[variables_user.i_indent - 2][2]

                    else:
                        # On récupère la dernière réponse ajoutée à la bdd, qui est celle contenant déjà la réponse donnée par le user
                        # puis on lui complète ses attributs user et question_id, puis le résultat (True ou False) de la question ainsi
                        # que la bonne réponse grâce à la fonction
                        reponse_test = Response.objects.latest('id')
                        reponse_test.user = str(request.user)
                        reponse_test.question_id = Question.objects.get(pk=variables_user.i_indent - 1)
                        reponse_test.result = test_result_question(given_answer, variables_user.i_indent - 1, request.user)
                        reponse_test.correct_answer = list_exam_questions[variables_user.i_indent - 2][2]

                    # Sauvegarde de la réponse
                    reponse_test.save()
                    # Réinitialisation du formulaire
                    form = ResponseForm()
                    # Incrémentation du compteur des questions
                    variables_user = VariablesUser.objects.filter(user=request.user).get()
                    variables_user.add_indent()
                    variables_user.save()

            # Dernière question
            elif variables_user.i_indent >= 25:
                # On sauvegarde le formulaire
                form.save()

                # On récupère la réponse donnée dans le formulaire avec "cleaned_data" et "get"
                given_answer = form.cleaned_data.get('given_answer')

                # Si l'utilisateur n'a pas eu le temps de donner une réponse
                if given_answer is None:
                    reponse_test = Response.objects.latest('id')
                    reponse_test.user = str(request.user)
                    reponse_test.question_id = Question.objects.get(pk=variables_user.i_indent - 1)
                    reponse_test.result = False
                    reponse_test.correct_answer = list_exam_questions[variables_user.i_indent - 2][2]

                if given_answer is not None:
                    # On récupère la dernière réponse ajoutée à la bdd, qui est celle contenant déjà la réponse donnée par le user
                    # puis on lui complète ses attributs user et question_id, puis le résultat (True ou False) de la question ainsi
                    # que la bonne réponse grâce à la fonction
                    reponse_test = Response.objects.latest('id')
                    reponse_test.user = str(request.user)
                    reponse_test.question_id = Question.objects.get(pk=variables_user.i_indent - 1)
                    reponse_test.result = test_result_question(given_answer, variables_user.i_indent - 1, request.user)
                    reponse_test.correct_answer = list_exam_questions[variables_user.i_indent - 2][2]

                # Sauvegarde de la réponse
                reponse_test.save()

                # Réinitialisation des variables globales
                variables_user = VariablesUser.objects.filter(user=request.user).get()
                variables_user.reset_indent()
                variables_user.reset_bool_tirage()

                # On calcule le score obtenu grâce au compteur de bonnes réponses
                # score = round(count_correct_answers / 22 * 100, 2)
                score = round(variables_user.count_good_answers / 24 * 100, 2)
                # Puis on le réinitialise
                variables_user.reset_points()
                # Ainsi que la liste des questions
                variables_user.list_q_exam = []
                variables_user.save()

                # On crée un nouvel objet pour la table score, puis on précise ses attributes "user" et "score"
                new_score = Score()
                new_score.user = str(request.user)
                new_score.score = score
                new_score.date_fin_test = datetime.datetime.now()
                # Si le score est supérieur ou égal à 75%, l'attribut "final_result" devient True, sinon, il devient False
                if score >= 75:
                    new_score.final_result = True
                elif score < 75:
                    new_score.final_result = False
                new_score.save()  # sauvegarde de l'objet créé

                return render(request, 'end_test.html', {'score': score})

        # if a GET (or any other method) we'll create a blank form
        else:
            form = ResponseForm()

    # On renvoie toujours le fichier question.html avec un context qui varie pour faire changer la question ainsi que
    # les variables et leurs valeurs associées
    return render(request, 'exam/question.html', {'form': form, 'question': list_exam_questions[variables_user.i_indent - 2][1]})


# Fonction qui crée l'examen en remplissant une liste avec une sous-liste contenant : l'ID de la question, l'énoncé ainsi que la bonne réponse.
def create_exam(total_number_questions, user):
    variable_user = VariablesUser.objects.filter(user=user).get()
    if variable_user.bool_tirage_exam:  # si le booléen est True
        list_questions_exam = []
        for id_question in range(1,
                                 total_number_questions + 1):  # Attention : le type de question commence à 1, donc on décale l'indentation de la liste
            list_questions_exam.append(create_question(id_question))
        variable_user.bool_tirage_exam = False
        variable_user.save()
        return list_questions_exam
    return VariablesUser.objects.filter(user=user).get().list_q_exam


# Fonction qui renvoie un intitulé de question ainsi que la réponse associée pour un id de question demandé
def create_question(id_question):
    question = Question.objects.get(pk=id_question).title
    list_values = Question.objects.get(pk=id_question).liste_value
    title = ""
    correct_answer = 0

    if id_question == 1:
        # "What is the weight of # USG with a specific gravity of # kg/l ?"
        # Formule : W * 3.785 * S
        W = random.choice(list_values[0])
        S = random.choice(list_values[1])
        correct_answer = W * 3.785 * S  # réponse correcte
        title = question.format(W, S)

    elif id_question == 2:
        # "How much is # L in USG ?"
        # Formule : V * 0.264172
        V = random.choice(list_values)
        correct_answer = V * 0.264172
        title = question.format(V)

    elif id_question == 3:
        # "How long (in minutes) to travel # km at # kt GS ?"
        # Formule : D / (V*1.852) * 60
        D = random.choice(list_values[0])
        V = random.choice(list_values[1])
        correct_answer = D / (V * 1.852) * 60
        title = question.format(D, V)

    elif id_question == 4:
        # "How much time (in minutes) to travel # NM at # km/h ?"
        # Formule : (D*1.852) / V * 60
        D = random.choice(list_values[0])
        V = random.choice(list_values[1])
        correct_answer = (D * 1.852) / V * 60
        title = question.format(D, V)

    elif id_question == 5:
        # "What is the distance to descend from # ft to # ft, with a GS of # kt and a rate of descent of # ft/min ?"
        # Formule : (X1 - X2)/R/60 * V
        X1 = random.choice(list_values[0])
        X2 = random.choice(list_values[1])
        V = random.choice(list_values[2])
        R = random.choice(list_values[3])
        correct_answer = ((X1 - X2) / R / 60) * V
        title = question.format(X1, X2, V, R)

    elif id_question == 6:
        # "What is the rate of descent from # ft to # ft with a GS of # kt in # NM ?"
        # Formule : (X1 -X2) / ((D/V)*60)
        X1 = random.choice(list_values[0])
        X2 = random.choice(list_values[1])
        V = random.choice(list_values[2])
        D = random.choice(list_values[3])
        correct_answer = (X1 - X2) / ((D / V) * 60)
        title = question.format(X1, X2, V, D)

    elif id_question == 7:
        # You enter the holding at #, you leave it at #, the fuel flow is # kg/h, how many kgs of fuel did you consume ?
        # Formule : (T2 - T1) * FF / 60
        T1 = random.choice(list_values[0])
        T2 = random.choice(list_values[1])
        FF = random.choice(list_values[2])
        T1_mm = int(str(T1)[2:4])
        T2_mm = int(str(T2)[2:4])
        correct_answer = (T2_mm - T1_mm) * FF / 60
        title = question.format(T1, T2, FF)

    elif id_question == 8:
        # You take off at #, your flight time is # hours and # minutes, when do you land at your destination ?
        # Formule : TOT + (H+M)
        TOT = random.choice(list_values[0])
        H = random.choice(list_values[1])
        M = random.choice(list_values[2])
        TOT_hh = int(str(TOT)[0:2])
        TOT_mm = int(str(TOT)[2:4])
        TOT_minutes = TOT_hh * 60 + TOT_mm
        correct_answers_minutes = TOT_minutes + H * 60 + M
        time_hh = correct_answers_minutes // 60
        time_mm = correct_answers_minutes % 60
        if time_hh < 10:
            time_hh = str(0) + str(time_hh)
        correct_answer = int(str(time_hh) + str(time_mm))
        title = question.format(TOT, H, M)

    elif id_question == 9:
        # "Fuel flow : # kg/min. How much weight do we lose in # minutes ?"
        # Formule : FF * M
        FF = random.choice(list_values[0])
        M = random.choice(list_values[1])
        correct_answer = FF * M
        title = question.format(FF, M)

    elif id_question == 10:
        # "Fuel flow:  # USG/h. How much weight do we lose in # minutes with a specific gravity of # kg/L ?"
        # Formule : FF * 3.7854 * S / 60 * M
        FF = random.choice(list_values[0])
        M = random.choice(list_values[1])
        S = random.choice(list_values[2])
        correct_answer = FF * 3.7854 * S / 60 * M
        title = question.format(FF, M, S)

    elif id_question == 11:
        # "How much time (in minutes) to lose # kg with a fuel flow of # kg/min ?"
        # Formule : W / FF
        W = random.choice(list_values[0])
        FF = random.choice(list_values[1])
        correct_answer = W / FF
        title = question.format(W, FF)

    elif id_question == 12:
        # "Fuel flow : # lb/h. How fast (in minutes) are # kg consumed ?"
        # Formule : W / (FF*0,453592/60)
        FF = random.choice(list_values[0])
        W = random.choice(list_values[1])
        correct_answer = W / (FF * 0.453592 / 60)
        title = question.format(FF, W)

    elif id_question == 13 or id_question == 14:
        # "Descending at # kt and # ft/min. I must be at # NM from DME and # ft. Current position at # ft. How far (in NM) from DME should I begin the descent ?"
        # "Descending at # kt and # ft/min. I must be at # NM from DME and # ft. Current position at # ft. At what distance (in NM) from DME should I start the descent ?"
        # Formule : ((X2 - X1)/R/60 * V) + D
        V = random.choice(list_values[0])
        R = random.choice(list_values[1])
        D = random.choice(list_values[2])
        X1 = random.choice(list_values[3])
        X2 = random.choice(list_values[4])
        correct_answer = ((X2 - X1) / R / 60 * V) + D
        title = question.format(V, R, D, X1, X2)

    elif id_question == 15 or id_question == 16:
        # "How much is # % of # m ?"
        # "How much is # % of # ft ?"
        # Formule : P/100 * D
        P = random.choice(list_values[0])
        D = random.choice(list_values[1])
        correct_answer = P / 100 * D
        title = question.format(P, D)

    elif id_question == 17:
        # "Which height is given by a slope of # % at # NM ?"
        # Formule : D*(S/100)*6080
        D = random.choice(list_values[0])
        S = random.choice(list_values[1])
        correct_answer = D * (S / 100) * 6080
        title = question.format(D, S)

    elif id_question == 18:
        # "Which height is given by a slope of # ° at # NM ?"
        # Formule : S*D/60 * 6080
        D = random.choice(list_values[0])
        S = random.choice(list_values[1])
        correct_answer = S * D / 60 * 6080
        title = question.format(D, S)

    elif id_question == 19 or id_question == 20:
        # "Using the 1/60 rule, # NM of lateral gap at # NM gives a drift of how many degrees ?"
        # "Lateral drift is # NM after # NM. What is the drift angle in degrees ?
        # Formule : L / (D/60)
        L = random.choice(list_values[0])
        D = random.choice(list_values[1])
        correct_answer = L / (D / 60)
        title = question.format(L, D)

    elif id_question == 21:
        # "RWY # and wind is # for # kts. What is the crosswind ?"
        # Formule : S * sin(abs(XX-W))
        XX = random.choice(list_values[0])
        W = random.choice(list_values[1])
        S = random.choice(list_values[0])
        RWY = XX * 10
        alpha = abs(RWY - W)
        correct_answer = abs(S * math.sin(alpha * math.pi / 180))
        title = question.format(XX, W, S)

    elif id_question == 22:
        # "RWY # and wind is # for # kts. What is the facewind ?"
        # Formule : S * cos(abs(XX-W))
        XX = random.choice(list_values[0])
        W = random.choice(list_values[1])
        S = random.choice(list_values[0])
        RWY = XX * 10
        alpha = abs(RWY - W)
        correct_answer = abs(S * math.cos(alpha * math.pi / 180))
        title = question.format(XX, W, S)

    elif id_question == 23:
        # How much is {} km in NM ?
        # Formule : D * 0,539957
        D = random.choice(list_values)
        correct_answer = D * 0.539957
        title = question.format(D)

    elif id_question == 24:
        # How much is {} ft in meters ?
        # Formule : D * 0,3048
        D = random.choice(list_values)
        correct_answer = D * 0.3048
        title = question.format(D)

    return [id_question, title, correct_answer]


# Fonction qui renvoie True ou False en fonction de si la réponse donnée est dans les + ou - 10%
def test_result_question(given_answer, id_question, user):
    global list_exam_questions
    list_exam_questions = VariablesUser.objects.filter(user=user).get().list_q_exam
    correct_answer = list_exam_questions[id_question - 1][2]  # on récupère la réponse correcte en fonction de la question

    # Pour la question 8, passage en minutes pour l'intervalle de 10%
    if id_question == 8:
        correct_answer = int(str(correct_answer)[0:2]) * 60 + int(str(correct_answer)[2:4])
        given_answer = int(str(given_answer)[0:2]) * 60 + int(str(given_answer)[2:4])

    # Définition des bornes hautes et basses de l'intervalle à partir de la bonne réponse
    up_interval = correct_answer + 0.1 * correct_answer
    down_interval = correct_answer - 0.1 * correct_answer

    # Si la réponse donnée est dans le bon intervalle, on incrémente le compteur et on renvoie True
    if down_interval < given_answer < up_interval:
        variables_user = VariablesUser.objects.filter(user=user).get()
        variables_user.add_point()
        variables_user.save()
        return True
    # Sinon, on renvoie False
    else:
        return False