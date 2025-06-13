from django.shortcuts import render, get_object_or_404, redirect
from syllabus_app.models import Aluno, Departamento, Curso, ConjuntoDisciplinas, Disciplina, DisciplinasCursadas, ReqConclusao
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import UserRegistrationForm
from django.core.exceptions import PermissionDenied


@login_required
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_aluno = Aluno.objects.count()
    num_conjunto_disciplinas = ConjuntoDisciplinas.objects.count()
    num_disciplina = Disciplina.objects.count()

    aluno = None
    # Tenta buscar o Aluno apenas se o username puder ser um RA (numérico)
    # Com a OneToOneField, podemos buscar diretamente pelo usuário.
    if hasattr(request.user, 'aluno'): # Verifica se o perfil Aluno existe para o usuário
        aluno = request.user.aluno
    # Se o usuário for 'admin' ou outro sem perfil Aluno, 'aluno' permanecerá None.

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

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Loga o usuário automaticamente após o cadastro
            return redirect('index') # Redireciona para a página inicial
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})





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
        # O campo DisciplinasCursadas.ra_aluno é uma ForeignKey para User,
        # usando User.username (que é o RA) como to_field.
        # Portanto, podemos filtrar diretamente pela instância do usuário.
        if self.request.user.is_authenticated:
            try:
                # Verifica se o username do usuário é um RA válido (numérico)
                # Esta verificação pode não ser estritamente necessária se todos os usuários
                # em DisciplinasCursadas tiverem usernames numéricos (RAs).
                int(self.request.user.username)
                return DisciplinasCursadas.objects.filter(ra_aluno=self.request.user).select_related('cod_disciplina').order_by('cod_disciplina')
            except ValueError: # Caso o username não seja numérico (ex: admin)
                return DisciplinasCursadas.objects.none()
        return DisciplinasCursadas.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        aluno = None
        # Tenta obter o perfil Aluno associado ao usuário logado
        if hasattr(self.request.user, 'aluno'):
            aluno = self.request.user.aluno
        context['aluno'] = aluno
        return context

from django.contrib.auth.mixins import PermissionRequiredMixin


from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse_lazy
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

@login_required # Adicionar login_required se esta view deve ser protegida
def verificar_conclusao_curso(request, aluno_id):
    aluno_obj = get_object_or_404(Aluno, id=aluno_id)

    # Disciplinas que o aluno efetivamente cursou (lista de objetos Disciplina)
    disciplinas_aluno_cursou_objs = [
        dc.cod_disciplina for dc in DisciplinasCursadas.objects.filter(
            ra_aluno=aluno_obj.user # Correção: filtrar pelo User associado ao Aluno
        ).select_related('cod_disciplina')
    ]

    # Separar as disciplinas cursadas em obrigatórias e optativas
    cursadas_obrigatorias = [d for d in disciplinas_aluno_cursou_objs if d.obrigatoria]
    cursadas_optativas = [d for d in disciplinas_aluno_cursou_objs if not d.obrigatoria]
    
    # Calcular CH cursada (convertendo carga_horaria para int)
    ch_obrigatorias_cursadas = sum(int(d.carga_horaria) for d in cursadas_obrigatorias if d.carga_horaria.isdigit())
    ch_optativas_cursadas = sum(int(d.carga_horaria) for d in cursadas_optativas if d.carga_horaria.isdigit())
    
    # Requisitos do curso do aluno
    try:
        requisitos_conclusao = ReqConclusao.objects.get(nome_curso=aluno_obj.nome_curso)
    except ReqConclusao.DoesNotExist:
        requisitos_conclusao = None # Tratar no template se não houver requisitos definidos

    return render(request, 'syllabus_app/verificar_conclusao.html', {
        'aluno': aluno_obj,
        'disciplinas_cursadas_objs': disciplinas_aluno_cursou_objs,
        'cursadas_obrigatorias': cursadas_obrigatorias,
        'cursadas_optativas': cursadas_optativas,
        'ch_obrigatorias_cursadas': ch_obrigatorias_cursadas,
        'ch_optativas_cursadas': ch_optativas_cursadas,
        'requisitos_conclusao': requisitos_conclusao,
        # A lógica original com 'conjunto_obrigatorio' e 'conjuntos_optativos'
        # baseada em ConjuntoDisciplinas.ch_obrigatoria foi removida pois a classificação
        # de uma disciplina como obrigatória/optativa é mais diretamente feita pelo campo Disciplina.obrigatoria.
        # Se a lógica de ConjuntoDisciplinas for necessária para validação de CH de grupos optativos,
        # ela precisará ser adicionada aqui.
    })

class AlunoAdicionaDisciplinaView(LoginRequiredMixin, CreateView):
    model = DisciplinasCursadas
    fields = ['cod_disciplina'] # Aluno só seleciona a disciplina
    template_name = 'syllabus_app/aluno_adiciona_disciplina.html'
    success_url = reverse_lazy('disciplinascursadas') # Redireciona para a lista de suas disciplinas

    def dispatch(self, request, *args, **kwargs):
        # Verificar se o usuário logado tem um perfil de Aluno
        if not hasattr(request.user, 'aluno'):
            raise PermissionDenied("Você não tem permissão para adicionar disciplinas cursadas.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.ra_aluno = self.request.user # Define o aluno logado (User instance)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aluno'] = self.request.user.aluno # Passar o objeto aluno para o template
        return context
