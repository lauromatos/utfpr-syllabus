from django.shortcuts import render, get_object_or_404, redirect
from syllabus_app.models import Aluno, Departamento, Curso, ConjuntoDisciplinas, Disciplina, DisciplinasCursadas, ReqConclusao
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login # type: ignore
from .forms import UserRegistrationForm, ReqConclusaoForm
from django.core.exceptions import PermissionDenied


@login_required
def index(request):
    num_aluno = Aluno.objects.count()
    num_conjunto_disciplinas = ConjuntoDisciplinas.objects.count()
    num_disciplina = Disciplina.objects.count()

    aluno = None
    if hasattr(request.user, 'aluno'):
        aluno = request.user.aluno

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

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


from django.views import generic

class AlunoListView(generic.ListView):
    model = Aluno
    paginate_by = 10

class AlunoDetailView(generic.DetailView):
    model = Aluno

class DepartamentoListView(generic.ListView):
    model = Departamento
    paginate_by = 10

class DepartamentoDetailView(generic.DetailView):
    model = Departamento

class CursoListView(generic.ListView):
    model = Curso
    paginate_by = 10

class CursoDetailView(generic.DetailView):
    model = Curso

class ConjuntoDisciplinasDetailView(generic.DetailView):
    model = ConjuntoDisciplinas

class ConjuntoDisciplinasListView(generic.ListView):
    model = ConjuntoDisciplinas
    paginate_by = 10

class DisciplinaDetailView(generic.DetailView):
    model = Disciplina

class DisciplinaListView(generic.ListView):
    model = Disciplina
    paginate_by = 10

class DisciplinasCursadasDetailView(generic.DetailView):
    model = DisciplinasCursadas

class DisciplinasCursadasListView(generic.ListView):
    model = DisciplinasCursadas
    paginate_by = 10

class ReqConclusaoDetailView(generic.DetailView):
    model = ReqConclusao

class ReqConclusaoListView(generic.ListView):
    model = ReqConclusao
    paginate_by = 10


from django.contrib.auth.mixins import LoginRequiredMixin

class DisciplinasCursadasAlunoListView(LoginRequiredMixin, generic.ListView):
    model = DisciplinasCursadas
    template_name = 'syllabus_app/disciplinas_cursadas_aluno_list.html'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_authenticated:
            try:
                int(self.request.user.username)
                return DisciplinasCursadas.objects.filter(ra_aluno=self.request.user).select_related('cod_disciplina').order_by('cod_disciplina')
            except ValueError:
                return DisciplinasCursadas.objects.none()
        return DisciplinasCursadas.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        aluno = None
        if hasattr(self.request.user, 'aluno'):
            aluno = self.request.user.aluno
        context['aluno'] = aluno
        return context

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.db.models import ProtectedError
from django.contrib import messages
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import DisciplinasCursadas, Disciplina
from .forms import AlunoAdicionaDisciplinaForm

class DisciplinasCursadasCreate(PermissionRequiredMixin, CreateView):
    model = DisciplinasCursadas
    fields = ['ra_aluno', 'cod_disciplina']
    permission_required = 'syllabus_app.add_disciplinascursadas'

class DisciplinasCursadasUpdate(PermissionRequiredMixin, UpdateView):
    model = DisciplinasCursadas
    fields = ['ra_aluno', 'cod_disciplina']
    permission_required = 'syllabus_app.change_disciplinascursadas'

class DisciplinasCursadasDelete(PermissionRequiredMixin, DeleteView):
    model = DisciplinasCursadas
    success_url = reverse_lazy('disciplinascursadas')
    permission_required = 'syllabus_app.delete_disciplinascursadas'
    
    def delete(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            response = super().delete(request, *args, **kwargs)
            messages.success(request, f"'{self.object}' foi removido com sucesso.")
            return response
        except ProtectedError:
            messages.error(request, f"Não é possível remover '{self.object}', pois está referenciado por outros objetos.")
            return HttpResponseRedirect(self.get_success_url())


class DisciplinaCreate(PermissionRequiredMixin, CreateView):
    model = Disciplina
    fields = ['cod_disciplina', 'nome_disciplina', 'Departamento', 'carga_horaria',
              'obrigatoria', 'cod_optativa', 'periodo', 'extensionista']
    success_url = reverse_lazy('disciplina')
    permission_required = 'syllabus_app.add_disciplina'

class DisciplinaUpdate(PermissionRequiredMixin, UpdateView):
    model = Disciplina
    fields = ['cod_disciplina', 'nome_disciplina', 'Departamento', 'carga_horaria',
              'obrigatoria', 'cod_optativa', 'periodo', 'extensionista']
    success_url = reverse_lazy('disciplina')
    permission_required = 'syllabus_app.change_disciplina'

class DisciplinaDelete(PermissionRequiredMixin, DeleteView):
    model = Disciplina
    success_url = reverse_lazy('disciplina')
    permission_required = 'syllabus_app.delete_disciplina'
    
    def delete(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            response = super().delete(request, *args, **kwargs)
            messages.success(request, f"'{self.object}' foi removido com sucesso.")
            return response
        except ProtectedError:
            messages.error(request, f"Não é possível remover '{self.object}', pois está referenciado por outros objetos.")
            return HttpResponseRedirect(self.get_success_url())

class CursoCreate(PermissionRequiredMixin, CreateView):
    model = Curso
    fields = ['nome_curso', 'departamento']
    success_url = reverse_lazy('curso')
    permission_required = 'syllabus_app.add_curso'

class CursoUpdate(PermissionRequiredMixin, UpdateView):
    model = Curso
    fields = ['nome_curso', 'departamento']
    success_url = reverse_lazy('curso')
    permission_required = 'syllabus_app.change_curso'

class CursoDelete(PermissionRequiredMixin, DeleteView):
    model = Curso
    success_url = reverse_lazy('curso')
    permission_required = 'syllabus_app.delete_curso'
    
    def delete(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            response = super().delete(request, *args, **kwargs)
            messages.success(request, f"'{self.object}' foi removido com sucesso.")
            return response
        except ProtectedError:
            messages.error(request, f"Não é possível remover '{self.object}', pois está referenciado por outros objetos.")
            return HttpResponseRedirect(self.get_success_url())


class DepartamentoCreate(PermissionRequiredMixin, CreateView):
    model = Departamento
    fields = ['departamento', 'nome_departamento']
    permission_required = 'syllabus_app.add_departamento'
    success_url = reverse_lazy('departamento') # Redireciona para a lista de departamentos após a criação


class DepartamentoUpdate(PermissionRequiredMixin, UpdateView):
    model = Departamento
    fields = ['departamento', 'nome_departamento']
    permission_required = 'syllabus_app.change_departamento'
    success_url = reverse_lazy('departamento') # Redireciona para a lista de departamentos após a atualização


class DepartamentoDelete(PermissionRequiredMixin, DeleteView):
    model = Departamento
    success_url = reverse_lazy('departamento')
    permission_required = 'syllabus_app.delete_departamento'
    
    def delete(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            response = super().delete(request, *args, **kwargs)
            messages.success(request, f"'{self.object}' foi removido com sucesso.")
            return response
        except ProtectedError:
            messages.error(request, f"Não é possível remover '{self.object}', pois está referenciado por outros objetos.")
            return HttpResponseRedirect(self.get_success_url())


class ConjuntoDisciplinasCreate(PermissionRequiredMixin, CreateView):
    model = ConjuntoDisciplinas
    fields = ['cod_optativa', 'nome_conjunto', 'ch_obrigatoria']
    success_url = reverse_lazy('conjuntodisciplinas')
    permission_required = 'syllabus_app.add_conjuntodisciplinas'


class ConjuntoDisciplinasUpdate(PermissionRequiredMixin, UpdateView):
    model = ConjuntoDisciplinas
    fields = ['cod_optativa', 'nome_conjunto', 'ch_obrigatoria']
    success_url = reverse_lazy('conjuntodisciplinas')
    permission_required = 'syllabus_app.change_conjuntodisciplinas'


class ConjuntoDisciplinasDelete(PermissionRequiredMixin, DeleteView):
    model = ConjuntoDisciplinas
    success_url = reverse_lazy('conjuntodisciplinas')
    permission_required = 'syllabus_app.delete_conjuntodisciplinas'
    
    def delete(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            response = super().delete(request, *args, **kwargs)
            messages.success(request, f"'{self.object}' foi removido com sucesso.")
            return response
        except ProtectedError:
            messages.error(request, f"Não é possível remover '{self.object}', pois está referenciado por outros objetos.")
            return HttpResponseRedirect(self.get_success_url())


class ReqConclusaoCreate(PermissionRequiredMixin, CreateView):
    model = ReqConclusao
    form_class = ReqConclusaoForm
    success_url = reverse_lazy('reqconclusao')
    permission_required = 'syllabus_app.add_reqconclusao'


class ReqConclusaoUpdate(PermissionRequiredMixin, UpdateView):
    model = ReqConclusao
    form_class = ReqConclusaoForm
    permission_required = 'syllabus_app.change_reqconclusao'
    success_url = reverse_lazy('reqconclusao') # Redireciona para a lista após a atualização


class ReqConclusaoDelete(PermissionRequiredMixin, DeleteView):
    model = ReqConclusao
    success_url = reverse_lazy('reqconclusao')
    permission_required = 'syllabus_app.delete_reqconclusao'
    
    def delete(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            response = super().delete(request, *args, **kwargs)
            messages.success(request, f"'{self.object}' foi removido com sucesso.")
            return response
        except ProtectedError:
            messages.error(request, f"Não é possível remover '{self.object}', pois está referenciado por outros objetos.")
            return HttpResponseRedirect(self.get_success_url())


from django.shortcuts import render
from .models import Aluno, DisciplinasCursadas, ConjuntoDisciplinas, ReqConclusao
from django.contrib.auth.models import User

@login_required
def verificar_conclusao_curso(request, aluno_id):
    aluno_obj = get_object_or_404(Aluno, id=aluno_id)

    disciplinas_aluno_cursou_objs = [
        dc.cod_disciplina for dc in DisciplinasCursadas.objects.filter(
            ra_aluno=aluno_obj.user
        ).select_related('cod_disciplina')
    ]

    cursadas_obrigatorias = [d for d in disciplinas_aluno_cursou_objs if d.obrigatoria]
    cursadas_optativas = [d for d in disciplinas_aluno_cursou_objs if not d.obrigatoria]
    
    ch_obrigatorias_cursadas = sum(int(d.carga_horaria) for d in cursadas_obrigatorias if d.carga_horaria.isdigit())
    ch_optativas_cursadas = sum(int(d.carga_horaria) for d in cursadas_optativas if d.carga_horaria.isdigit())
    
    try:
        requisitos_conclusao = ReqConclusao.objects.get(nome_curso=aluno_obj.nome_curso)
    except ReqConclusao.DoesNotExist:
        requisitos_conclusao = None

    return render(request, 'syllabus_app/verificar_conclusao.html', {
        'aluno': aluno_obj,
        'disciplinas_cursadas_objs': disciplinas_aluno_cursou_objs,
        'cursadas_obrigatorias': cursadas_obrigatorias,
        'cursadas_optativas': cursadas_optativas,
        'ch_obrigatorias_cursadas': ch_obrigatorias_cursadas,
        'ch_optativas_cursadas': ch_optativas_cursadas,
        'requisitos_conclusao': requisitos_conclusao,
    })

class AlunoAdicionaDisciplinaView(LoginRequiredMixin, CreateView):
    model = DisciplinasCursadas
    form_class = AlunoAdicionaDisciplinaForm
    template_name = 'syllabus_app/aluno_adiciona_disciplina.html'
    success_url = reverse_lazy('disciplinascursadas')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'aluno'):
            raise PermissionDenied("Você não tem permissão para adicionar disciplinas cursadas.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.ra_aluno = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aluno'] = self.request.user.aluno
        return context

class AlunoRemoveDisciplinaView(LoginRequiredMixin, DeleteView):
    model = DisciplinasCursadas
    template_name = 'syllabus_app/aluno_remove_disciplina_confirm.html'
    success_url = reverse_lazy('disciplinascursadas')

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(ra_aluno=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'aluno'):
            raise PermissionDenied("Você não tem permissão para remover disciplinas cursadas.")
        return super().dispatch(request, *args, **kwargs)