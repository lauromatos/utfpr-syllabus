from django.shortcuts import render
from syllabus_app.models import Aluno, Departamento, Curso, ConjuntoDisciplinas, Disciplina, DisciplinasCursadas, ReqConclusao
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_aluno = Aluno.objects.count()
    num_conjunto_disciplinas = ConjuntoDisciplinas.objects.count()
    num_disciplina = Disciplina.objects.count()
    aluno = Aluno.objects.get(id=1)

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1


    context = {
        'aluno': aluno,
        'num_aluno': num_aluno,
        'num_conjunto_disciplinas': num_conjunto_disciplinas,
        'num_disciplina': num_disciplina,
        'num_visits': num_visits,
    }

    return render(request, 'index.html', context=context)



from django.views import generic


class AlunoListView(generic.ListView):
    """Generic class-based view for a list of Alunos."""
    model = Aluno
    paginate_by = 10

class AlunoDetailView(generic.DetailView):
    """Generic class-based detail view for a Aluno."""
    model = Aluno

class DepartamentoListView(generic.ListView):
    """Generic class-based list view for a list of Departamentos."""
    model = Departamento
    paginate_by = 10

class DepartamentoDetailView(generic.DetailView):
    """Generic class-based detail view for an Departamento."""
    model = Departamento

class CursoListView(generic.ListView):
    """Generic class-based list view for a list of Cursos."""
    model = Curso
    paginate_by = 10

class CursoDetailView(generic.DetailView):
    """Generic class-based detail view for a Curso."""
    model = Curso

class ConjuntoDisciplinasDetailView(generic.DetailView):
    """Generic class-based detail view for a ConjuntoDisciplinas."""
    model = ConjuntoDisciplinas

class ConjuntoDisciplinasListView(generic.ListView):
    """Generic class-based list view for a list of ConjuntoDisciplinas."""
    model = ConjuntoDisciplinas
    paginate_by = 10

class DisciplinaDetailView(generic.DetailView):
    """Generic class-based detail view for a Disciplina."""
    model = Disciplina

class DisciplinaListView(generic.ListView):
    """Generic class-based view for a list of Disciplinas."""
    model = Disciplina
    paginate_by = 10

class DisciplinasCursadasDetailView(generic.DetailView):
    """Generic class-based detail view for a DisciplinasCursadas."""
    model = DisciplinasCursadas

class DisciplinasCursadasListView(generic.ListView):
    """Generic class-based view for a list of DisciplinasCursadas."""
    model = DisciplinasCursadas
    paginate_by = 10

class ReqConclusaoDetailView(generic.DetailView):
    """Generic class-based detail view for a ReqConclusao."""
    model = ReqConclusao

class ReqConclusaoListView(generic.ListView):
    """Generic class-based view for a list of ReqConclusao."""
    model = ReqConclusao
    paginate_by = 10


from django.contrib.auth.mixins import LoginRequiredMixin

class DisciplinasCursadasAlunoListView(LoginRequiredMixin, generic.ListView):
    model = DisciplinasCursadas
    template_name = 'syllabus_app/disciplinas_cursadas_aluno_list.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            DisciplinasCursadas.objects.filter(ra_aluno_id=self.request.user)
            .filter(ra_aluno_id__exact=self.request.user)
            .order_by('cod_disciplina')
        )

from django.contrib.auth.mixins import PermissionRequiredMixin


from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import DisciplinasCursadas, Disciplina


class DisciplinasCursadasCreate(PermissionRequiredMixin, CreateView):
    model = DisciplinasCursadas
    fields = ['ra_aluno', 'cod_disciplina']
    permission_required = 'syllabus_app.add_disciplinascursadas'

class DisciplinasCursadasUpdate(PermissionRequiredMixin, UpdateView):
    model = DisciplinasCursadas
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'syllabus_app.change_disciplinascursadas'

class DisciplinasCursadasDelete(PermissionRequiredMixin, DeleteView):
    model = DisciplinasCursadas
    success_url = reverse_lazy('disciplinascursadas')
    permission_required = 'syllabus_app.delete_disciplinascursadas'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("disciplinascursadas-delete", kwargs={"pk": self.object.pk})
            )


class DisciplinaCreate(PermissionRequiredMixin, CreateView):
    model = Disciplina
    fields = ['cod_disciplina', 'nome_disciplina', 'Departamento', 'carga_horaria',
              'obrigatoria', 'cod_optativa', 'periodo', 'extensionista']
    permission_required = 'syllabus_app.add_disciplina'

class DisciplinaUpdate(PermissionRequiredMixin, UpdateView):
    model = Disciplina
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'syllabus_app.change_disciplina'

class DisciplinaDelete(PermissionRequiredMixin, DeleteView):
    model = Disciplina
    success_url = reverse_lazy('disciplina')
    permission_required = 'syllabus_app.delete_disciplina'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("disciplina-delete", kwargs={"pk": self.object.pk})
            )

class CursoCreate(PermissionRequiredMixin, CreateView):
    model = Curso
    fields = ['nome_curso', 'departamento']
    permission_required = 'syllabus_app.add_curso'

class CursoUpdate(PermissionRequiredMixin, UpdateView):
    model = Curso
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'syllabus_app.change_curso'

class CursoDelete(PermissionRequiredMixin, DeleteView):
    model = Curso
    success_url = reverse_lazy('curso')
    permission_required = 'syllabus_app.delete_curso'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("curso-delete", kwargs={"pk": self.object.pk})
            )


class DepartamentoCreate(PermissionRequiredMixin, CreateView):
    model = Departamento
    fields = ['departamento', 'nome_departamento']
    permission_required = 'syllabus_app.add_departamento'


class DepartamentoUpdate(PermissionRequiredMixin, UpdateView):
    model = Departamento
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'syllabus_app.change_departamento'


class DepartamentoDelete(PermissionRequiredMixin, DeleteView):
    model = Departamento
    success_url = reverse_lazy('departamentos')
    permission_required = 'syllabus_app.delete_departamento'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("departamento-delete", kwargs={"pk": self.object.pk})
            )


class ConjuntoDisciplinasCreate(PermissionRequiredMixin, CreateView):
    model = ConjuntoDisciplinas
    fields = ['cod_optativa', 'nome_conjunto', 'ch_obrigatoria']
    permission_required = 'syllabus_app.add_conjuntodisciplinas'


class ConjuntoDisciplinasUpdate(PermissionRequiredMixin, UpdateView):
    model = ConjuntoDisciplinas
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'syllabus_app.change_conjuntodisciplinas'


class ConjuntoDisciplinasDelete(PermissionRequiredMixin, DeleteView):
    model = ConjuntoDisciplinas
    success_url = reverse_lazy('conjuntodisciplinas')
    permission_required = 'syllabus_app.delete_conjuntodisciplinaso'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("conjuntodisciplinas-delete", kwargs={"pk": self.object.pk})
            )


class ReqConclusaoCreate(PermissionRequiredMixin, CreateView):
    model = ReqConclusao
    fields = ['nome_curso', 'ch_total', 'ch_obrigatorias', 'ch_optativas', 'ch_estagio']
    permission_required = 'syllabus_app.add_reqconclusao'


class ReqConclusaoUpdate(PermissionRequiredMixin, UpdateView):
    model = ReqConclusao
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'syllabus_app.change_reqconclusao'


class ReqConclusaoDelete(PermissionRequiredMixin, DeleteView):
    model = ReqConclusao
    success_url = reverse_lazy('reqconclusao')
    permission_required = 'syllabus_app.delete_reqconclusao'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("reqconclusao-delete", kwargs={"pk": self.object.pk})
            )
        



from django.shortcuts import render
from .models import Aluno, DisciplinasCursadas, ConjuntoDisciplinas, ReqConclusao
from django.contrib.auth.models import User

def verificar_conclusao_curso(request, aluno_id):
    aluno = Aluno.objects.get(id=aluno_id)
    disciplinas_cursadas = DisciplinasCursadas.objects.filter(ra_aluno=aluno)
    
    conjunto_obrigatorio = ConjuntoDisciplinas.objects.filter(ch_obrigatoria__gt=0)
    conjuntos_optativos = ConjuntoDisciplinas.objects.exclude(ch_obrigatoria__gt=0)
    
    requisitos_conclusao = ReqConclusao.objects.get(nome_curso=aluno.nome_curso)
    
    disciplinas_obrigatorias_cursadas = []
    disciplinas_optativas_cursadas = []

    for disciplina_cursada in disciplinas_cursadas:
        if disciplina_cursada.cod_disciplina in conjunto_obrigatorio.values_list('disciplina', flat=True):
            disciplinas_obrigatorias_cursadas.append(disciplina_cursada.cod_disciplina)
        elif disciplina_cursada.cod_disciplina in conjuntos_optativos.values_list('disciplina', flat=True):
            disciplinas_optativas_cursadas.append(disciplina_cursada.cod_disciplina)

    return render(request, 'verificar_conclusao.html', {
        'aluno': aluno,
        'disciplinas_cursadas': disciplinas_cursadas,
        'conjunto_obrigatorio': conjunto_obrigatorio,
        'conjuntos_optativos': conjuntos_optativos,
        'requisitos_conclusao': requisitos_conclusao,
    })
