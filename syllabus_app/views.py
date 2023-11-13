from django.shortcuts import render
from syllabus_app.models import Aluno, ConjuntoDisciplinas, Disciplina
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_aluno = Aluno.objects.count()
    num_conjunto_disciplinas = ConjuntoDisciplinas.objects.count()
    num_disciplina = Disciplina.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1


    context = {
        'num_aluno': num_aluno,
        'num_conjunto_disciplinas': num_conjunto_disciplinas,
        'num_disciplina': num_disciplina,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)
