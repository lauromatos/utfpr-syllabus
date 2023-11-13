from django.shortcuts import render

# Create your views here.

from syllabus_app.models import Aluno, ConjuntoDisciplinas, Disciplina

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_aluno = Aluno.objects.count()
    num_conjunto_disciplinas = ConjuntoDisciplinas.objects.count()
    num_disciplina = Disciplina.objects.count()

    # Available books (status = 'a')
    # num_instances_available = BookInstance.objects.filter(status__exact='a').count()


    context = {
        'num_aluno': num_aluno,
        'num_conjunto_disciplinas': num_conjunto_disciplinas,
        'num_disciplina': num_disciplina,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)
