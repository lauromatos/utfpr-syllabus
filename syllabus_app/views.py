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
from django.db.models import ProtectedError, Q
from django.contrib import messages
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import DisciplinasCursadas, Disciplina
from .forms import AlunoAdicionaDisciplinaForm, DisciplinaForm, ReqConclusaoForm

class DisciplinasCursadasCreate(PermissionRequiredMixin, CreateView):
    model = DisciplinasCursadas
    fields = ['ra_aluno', 'cod_disciplina']
    permission_required = 'syllabus_app.add_disciplinascursadas'
    success_url = reverse_lazy('disciplinascursadas')

class DisciplinasCursadasUpdate(PermissionRequiredMixin, UpdateView):
    model = DisciplinasCursadas
    fields = ['ra_aluno', 'cod_disciplina']
    permission_required = 'syllabus_app.change_disciplinascursadas'
    success_url = reverse_lazy('disciplinascursadas')

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
    form_class = DisciplinaForm
    success_url = reverse_lazy('disciplina')
    permission_required = 'syllabus_app.add_disciplina'

class DisciplinaUpdate(PermissionRequiredMixin, UpdateView):
    model = Disciplina
    form_class = DisciplinaForm
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

class AlunoAdicionaDisciplinaView(LoginRequiredMixin, generic.FormView): # Changed to FormView
    form_class = AlunoAdicionaDisciplinaForm
    template_name = 'syllabus_app/aluno_adiciona_disciplina.html'
    success_url = reverse_lazy('disciplinascursadas')

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'aluno'):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        # Retain search term if page is reloaded/navigated back with it in GET params
        if 'cod_disciplina_input' in self.request.GET:
            initial['cod_disciplina_input'] = self.request.GET.get('cod_disciplina_input')
        return initial

    def get(self, request, *args, **kwargs):
        add_this_cod = request.GET.get('add_this_cod')

        if add_this_cod:
            try:
                disciplina_to_add = Disciplina.objects.get(cod_disciplina__iexact=add_this_cod)
                
                if DisciplinasCursadas.objects.filter(ra_aluno=request.user, cod_disciplina=disciplina_to_add).exists():
                    messages.error(request, f"Disciplina '{disciplina_to_add}' já cadastrada.")
                else:
                    DisciplinasCursadas.objects.create(ra_aluno=request.user, cod_disciplina=disciplina_to_add)
                    messages.success(request, f"Disciplina '{disciplina_to_add}' adicionada com sucesso.")
                # Don't redirect immediately. Re-render the search page.
                # We need to re-fetch search results if a search term was present.
                form = self.get_form() # Get a fresh form instance
                search_term_from_get = request.GET.get('cod_disciplina_input_retained', '')
                disciplinas_found = []
                if search_term_from_get: # If a search term was retained
                    form.fields['cod_disciplina_input'].initial = search_term_from_get # Pre-fill form
                    disciplinas_found = list(
                        Disciplina.objects.filter(
                            Q(nome_disciplina__icontains=search_term_from_get) | Q(cod_disciplina__iexact=search_term_from_get)
                        ).distinct()
                    )
                
                # Pass already cursadas to template for button state
                cursadas_cods = list(DisciplinasCursadas.objects.filter(ra_aluno=request.user).values_list('cod_disciplina__cod_disciplina', flat=True))
                return self.render_to_response(self.get_context_data(form=form, disciplinas=disciplinas_found, cursadas_cods=cursadas_cods))

            except Disciplina.DoesNotExist:
                messages.error(request, "Disciplina inválida para adição.")
                return redirect(reverse('aluno_adiciona_disciplina'))
            except Exception as e: # Catch any other potential errors during creation
                messages.error(request, f"Ocorreu um erro ao adicionar a disciplina: {str(e)}")
                return redirect(reverse('aluno_adiciona_disciplina'))
        return super().get(request, *args, **kwargs)

    def form_valid(self, form): # Called by FormView's post method if form is valid
        # This method is now only for searching and displaying results.
        search_term = form.cleaned_data.get('cod_disciplina_input', '').strip()
        disciplinas_found = []

        if search_term:
            disciplinas_found = list(
                Disciplina.objects.filter(
                    Q(nome_disciplina__icontains=search_term) | Q(cod_disciplina__iexact=search_term)
                ).distinct()
            )

        if disciplinas_found:
            # Always display results, even if only one, as per new requirement
            # Pass already cursadas to template for button state
            cursadas_cods = list(DisciplinasCursadas.objects.filter(ra_aluno=self.request.user).values_list('cod_disciplina__cod_disciplina', flat=True))
            return self.render_to_response(
                self.get_context_data(form=form, disciplinas=disciplinas_found, cursadas_cods=cursadas_cods)
            )
        else: # No search term provided (form might be valid but empty if not required, though it is) or no results
            if search_term: # Only add error if a search was attempted
                form.add_error('cod_disciplina_input', 'Nenhuma disciplina encontrada com o termo fornecido.')
            return self.form_invalid(form) # Renders form with errors


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'aluno'): # Ensure aluno is in context
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
            messages.error(request, "Você não tem permissão para remover disciplinas cursadas.")
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_message = f"Disciplina '{self.object.cod_disciplina}' removida da sua lista com sucesso."
        # The actual deletion is handled by super().delete()