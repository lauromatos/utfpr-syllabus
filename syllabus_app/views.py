from django.shortcuts import render, get_object_or_404, redirect
from syllabus_app.models import Aluno, Departamento, Curso, ConjuntoDisciplinas, Disciplina, DisciplinasCursadas, ReqConclusao
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login # type: ignore
from .forms import UserRegistrationForm, ReqConclusaoForm
# Adicionando importações para as views de login/logout personalizadas
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import resolve, Resolver404
from django.shortcuts import resolve_url # Importação corrigida para resolve_url
from django.conf import settings
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
    if request.user.is_authenticated:
        return redirect('index') # Redireciona para o index se já estiver logado
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def welcome(request):
    return render(request, 'welcome.html')

from django.views import generic
from .mixins import AuthListViewMixin, DisciplinaAdderMixin # Import DisciplinaAdderMixin
from django.contrib.auth.mixins import LoginRequiredMixin

class AlunoListView(AuthListViewMixin, generic.ListView):
    model = Aluno

class AlunoDetailView(generic.DetailView):
    model = Aluno

class DepartamentoListView(AuthListViewMixin, generic.ListView):
    model = Departamento

class DepartamentoDetailView(generic.DetailView):
    model = Departamento

class CursoListView(AuthListViewMixin, generic.ListView):
    model = Curso

class CursoDetailView(generic.DetailView):
    model = Curso

class ConjuntoDisciplinasDetailView(generic.DetailView):
    model = ConjuntoDisciplinas

class ConjuntoDisciplinasListView(AuthListViewMixin, generic.ListView):
    model = ConjuntoDisciplinas

class DisciplinaDetailView(generic.DetailView):
    model = Disciplina

class DisciplinaListView(AuthListViewMixin, generic.ListView):
    model = Disciplina

class DisciplinasCursadasDetailView(generic.DetailView):
    model = DisciplinasCursadas

class DisciplinasCursadasListView(AuthListViewMixin, generic.ListView): # Para a lista geral de admin
    model = DisciplinasCursadas

class ReqConclusaoDetailView(generic.DetailView):
    model = ReqConclusao

class ReqConclusaoListView(AuthListViewMixin, generic.ListView):
    model = ReqConclusao

class DisciplinasCursadasAlunoListView(AuthListViewMixin, generic.ListView):
    model = DisciplinasCursadas
    template_name = 'syllabus_app/disciplinas_cursadas_aluno_list.html'

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
from .models import DisciplinasCursadas, Disciplina # DisciplinasCursadasForm is from .forms
from .forms import AlunoAdicionaDisciplinaForm, DisciplinaForm, ReqConclusaoForm, CustomAuthenticationForm, DepartamentoForm, CursoForm, ConjuntoDisciplinasForm, DisciplinasCursadasForm # Added DisciplinasCursadasForm

class DisciplinasCursadasCreate(PermissionRequiredMixin, DisciplinaAdderMixin, generic.FormView):
    model = DisciplinasCursadas
    form_class = DisciplinasCursadasForm # Use the new form
    permission_required = 'syllabus_app.add_disciplinascursadas'
    success_url = reverse_lazy('disciplinascursadas')
    template_name = 'syllabus_app/disciplinascursadas_form.html' # Use the new template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'disciplinas' not in context:
            context['disciplinas'] = []
        if 'cursadas_cods_for_selected_aluno' not in context:
            context['cursadas_cods_for_selected_aluno'] = []
        if 'selected_ra_aluno_pk' not in context and self.request.GET.get('ra_aluno'):
            context['selected_ra_aluno_pk'] = self.request.GET.get('ra_aluno')
        return context

    def get_initial(self):
        initial = super().get_initial()
        if 'ra_aluno' in self.request.GET:
            initial['ra_aluno'] = self.request.GET.get('ra_aluno')
        if self.search_input_field_name in self.request.GET:
            initial[self.search_input_field_name] = self.request.GET.get(self.search_input_field_name)
        return initial

    def get(self, request, *args, **kwargs):
        add_ra_aluno_username = request.GET.get('add_ra_aluno') # This should be user's PK or username
        add_cod_disciplina = request.GET.get('add_cod_disciplina')
        retained_search_term = request.GET.get('cod_disciplina_input_retained', '')
        retained_ra_aluno_pk = request.GET.get('ra_aluno_retained_pk')

        user_obj_for_add = None
        if add_ra_aluno_username:
            try:
                user_obj_for_add = User.objects.get(pk=add_ra_aluno_username) # Assuming add_ra_aluno is PK
            except User.DoesNotExist:
                messages.error(request, f"Aluno com ID '{add_ra_aluno_username}' não encontrado.")

        if user_obj_for_add and add_cod_disciplina:
            self.try_add_discipline_to_user(request, user_obj_for_add, add_cod_disciplina)
            
            # Re-render the page
            form = self.get_form_class()(initial={'ra_aluno': user_obj_for_add.pk, self.search_input_field_name: retained_search_term})
            disciplinas_found = self.get_disciplines_for_search(retained_search_term)
            cursadas_cods = self.get_already_cursadas_codes(user_obj_for_add)
            return self.render_to_response(self.get_context_data(form=form, disciplinas=disciplinas_found, cursadas_cods_for_selected_aluno=cursadas_cods, selected_ra_aluno_pk=user_obj_for_add.pk))

        # For initial GET or GET after search POST (from form_valid)
        form = self.get_form()
        search_term = request.GET.get(self.search_input_field_name, '') 
        selected_ra_aluno_pk = request.GET.get('ra_aluno')
        
        disciplinas_found = []
        cursadas_cods = []
        user_for_check = None
        if selected_ra_aluno_pk:
            try:
                user_for_check = User.objects.get(pk=selected_ra_aluno_pk)
                cursadas_cods = self.get_already_cursadas_codes(user_for_check)
                if search_term : # Only search if a student is selected
                    disciplinas_found = self.get_disciplines_for_search(search_term)
            except User.DoesNotExist:
                messages.error(request, "Aluno selecionado não encontrado.")
        
        return self.render_to_response(self.get_context_data(form=form, disciplinas=disciplinas_found, cursadas_cods_for_selected_aluno=cursadas_cods, selected_ra_aluno_pk=selected_ra_aluno_pk))

    def form_valid(self, form): # Called on POST (for searching)
        ra_aluno_obj = form.cleaned_data.get('ra_aluno')
        search_term = form.cleaned_data.get(self.search_input_field_name, '').strip()
        
        if not ra_aluno_obj:
            form.add_error('ra_aluno', "Por favor, selecione um aluno para realizar a busca.")
            return self.form_invalid(form)

        disciplinas_found = self.get_disciplines_for_search(search_term)
        cursadas_cods = self.get_already_cursadas_codes(ra_aluno_obj)

        if search_term and not disciplinas_found:
            form.add_error(self.search_input_field_name, 'Nenhuma disciplina encontrada com o termo fornecido.')

        return self.render_to_response(self.get_context_data(form=form, disciplinas=disciplinas_found, cursadas_cods_for_selected_aluno=cursadas_cods, selected_ra_aluno_pk=ra_aluno_obj.pk))

class DisciplinasCursadasUpdate(PermissionRequiredMixin, UpdateView):
    model = DisciplinasCursadas
    fields = ['ra_aluno', 'cod_disciplina']
    permission_required = 'syllabus_app.change_disciplinascursadas'
    success_url = reverse_lazy('disciplinascursadas')

# Note: DisciplinasCursadasDelete does not need a form template change as it's a confirmation page.
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
    template_name = 'syllabus_app/disciplina_form.html' # Especificar template
    success_url = reverse_lazy('disciplina')
    permission_required = 'syllabus_app.add_disciplina'

class DisciplinaUpdate(PermissionRequiredMixin, UpdateView):
    model = Disciplina
    form_class = DisciplinaForm
    template_name = 'syllabus_app/disciplina_form.html' # Especificar template
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
    form_class = CursoForm # Usar form_class
    template_name = 'syllabus_app/curso_form.html' # Especificar template
    success_url = reverse_lazy('curso')
    permission_required = 'syllabus_app.add_curso'

class CursoUpdate(PermissionRequiredMixin, UpdateView):
    model = Curso
    form_class = CursoForm # Usar form_class
    template_name = 'syllabus_app/curso_form.html' # Especificar template
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
    form_class = DepartamentoForm # Usar form_class
    template_name = 'syllabus_app/departamento_form.html' # Especificar template
    permission_required = 'syllabus_app.add_departamento'
    success_url = reverse_lazy('departamento') # Redireciona para a lista de departamentos após a criação


class DepartamentoUpdate(PermissionRequiredMixin, UpdateView):
    model = Departamento
    form_class = DepartamentoForm # Usar form_class
    template_name = 'syllabus_app/departamento_form.html' # Especificar template
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
    form_class = ConjuntoDisciplinasForm # Usar form_class
    template_name = 'syllabus_app/conjuntodisciplinas_form.html' # Especificar template
    success_url = reverse_lazy('conjuntodisciplinas')
    permission_required = 'syllabus_app.add_conjuntodisciplinas'


class ConjuntoDisciplinasUpdate(PermissionRequiredMixin, UpdateView):
    model = ConjuntoDisciplinas
    form_class = ConjuntoDisciplinasForm # Usar form_class
    template_name = 'syllabus_app/conjuntodisciplinas_form.html' # Especificar template
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
    template_name = 'syllabus_app/reqconclusao_form.html' # Especificar template
    success_url = reverse_lazy('reqconclusao')
    permission_required = 'syllabus_app.add_reqconclusao'


class ReqConclusaoUpdate(PermissionRequiredMixin, UpdateView):
    model = ReqConclusao
    form_class = ReqConclusaoForm
    template_name = 'syllabus_app/reqconclusao_form.html' # Especificar template
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
from collections import defaultdict

def _get_verificacao_conclusao_context(aluno_id):
    """Função auxiliar para buscar e calcular todos os dados para o relatório de conclusão."""
    aluno_obj = get_object_or_404(Aluno, id=aluno_id)

    # Obter todas as disciplinas que o aluno cursou
    disciplinas_cursadas_qs = DisciplinasCursadas.objects.filter(
        ra_aluno=aluno_obj.user
    ).select_related('cod_disciplina', 'cod_disciplina__cod_optativa')
    
    disciplinas_aluno_cursou_objs = [dc.cod_disciplina for dc in disciplinas_cursadas_qs]
    
    # Cria uma lista separada para as disciplinas extensionistas cursadas
    cursadas_extensionistas = [d for d in disciplinas_aluno_cursou_objs if d.extensionista]

    # Obter IDs das disciplinas cursadas para um filtro eficiente
    disciplinas_cursadas_ids = {dc.cod_disciplina_id for dc in disciplinas_cursadas_qs}

    # Lógica definitiva para identificar disciplinas obrigatórias via conjunto '0000'
    try:
        conjunto_obrigatorio = ConjuntoDisciplinas.objects.get(cod_optativa='0000')
    except ConjuntoDisciplinas.DoesNotExist:
        # Se o conjunto '0000' não existe no banco, nenhuma disciplina pode ser obrigatória por esta regra.
        conjunto_obrigatorio = None

    if conjunto_obrigatorio:
        todas_obrigatorias_do_curso = Disciplina.objects.filter(
            # REMOVIDO: O filtro 'curso' estava impedindo a localização das disciplinas.
            # A lógica agora assume que se uma disciplina está no conjunto '0000',
            # ela é uma candidata a obrigatória para qualquer curso.
            cod_optativa=conjunto_obrigatorio
        ).order_by('periodo', 'nome_disciplina')
    else:
        todas_obrigatorias_do_curso = Disciplina.objects.none()

    # Determinar quais disciplinas obrigatórias estão faltando
    obrigatorias_faltantes = todas_obrigatorias_do_curso.exclude(id__in=disciplinas_cursadas_ids)
    
    # Particionar as disciplinas cursadas usando a mesma lógica do conjunto '0000'
    cursadas_obrigatorias = []
    cursadas_optativas = []
    for d in disciplinas_aluno_cursou_objs:
        # A verificação d.cod_optativa_id é mais eficiente e segura
        if conjunto_obrigatorio and d.cod_optativa_id == conjunto_obrigatorio.id:
            cursadas_obrigatorias.append(d)
        else:
            cursadas_optativas.append(d)
    
    # --- Cálculos de Carga Horária ---
    ch_obrigatorias_cursadas = sum(int(d.carga_horaria) for d in cursadas_obrigatorias if d.carga_horaria.isdigit())

    # Processar optativas de forma mais eficiente (um loop)
    _trilhas_data_map = defaultdict(lambda: {'hours': 0, 'disciplines': [], 'conjunto': None})
    isolated_optativas = [] # Para optativas que não pertencem a nenhum conjunto específico

    for disciplina in cursadas_optativas:
        try:
            ch = int(disciplina.carga_horaria)
        except (ValueError, TypeError):
            continue  # Ignora disciplinas com carga horária inválida

        if disciplina.cod_optativa:
            nome_trilha = disciplina.cod_optativa.nome_conjunto
            # Se a disciplina tem um conjunto optativo, adicione-a à trilha correspondente
            _trilhas_data_map[nome_trilha]['hours'] += ch
            _trilhas_data_map[nome_trilha]['disciplines'].append(disciplina)
            _trilhas_data_map[nome_trilha]['conjunto'] = disciplina.cod_optativa
        else:
            # Se a disciplina não tem um conjunto optativo, é uma optativa isolada
            isolated_optativas.append(disciplina)

    # Recalcula as horas optativas e de humanidades, aplicando os limites
    ch_optativas_cursadas = 0
    ch_humanidades_cursadas = 0

    for data in _trilhas_data_map.values():
        conjunto = data['conjunto']
        horas_reais = data['hours']
        
        if conjunto.limitar_carga_horaria:
            horas_contabilizadas = min(horas_reais, int(conjunto.ch_obrigatoria))
        else:
            horas_contabilizadas = horas_reais
        
        ch_optativas_cursadas += horas_contabilizadas

        if "humanidades" in conjunto.nome_conjunto.lower():
            ch_humanidades_cursadas = horas_contabilizadas

    # Adiciona as horas das optativas isoladas, que não têm limite
    ch_optativas_cursadas += sum(int(d.carga_horaria) for d in isolated_optativas if d.carga_horaria.isdigit())

    # Calcular carga horária extensionista
    ch_extensionista_cursada = sum(int(d.carga_horaria) for d in disciplinas_aluno_cursou_objs if d.extensionista and d.carga_horaria.isdigit())

    try:
        requisitos_conclusao = ReqConclusao.objects.get(nome_curso=aluno_obj.nome_curso)
    except ReqConclusao.DoesNotExist:
        requisitos_conclusao = None

    # Lógica de verificação dos requisitos
    apto_a_concluir = True
    mensagens_pendencias = []

    # Calcula as horas faltantes para exibição no template
    faltam_obrigatorias = 0
    faltam_optativas = 0
    faltam_extensionista = 0
    extensionista_concluida = False
    if requisitos_conclusao:
        if ch_obrigatorias_cursadas < requisitos_conclusao.ch_obrigatorias:
            faltam_obrigatorias = requisitos_conclusao.ch_obrigatorias - ch_obrigatorias_cursadas
        if ch_optativas_cursadas < requisitos_conclusao.ch_optativas:
            faltam_optativas = requisitos_conclusao.ch_optativas - ch_optativas_cursadas
        if ch_extensionista_cursada < requisitos_conclusao.ch_extensionista:
            faltam_extensionista = requisitos_conclusao.ch_extensionista - ch_extensionista_cursada
        
        if requisitos_conclusao.ch_extensionista > 0:
            extensionista_concluida = ch_extensionista_cursada >= requisitos_conclusao.ch_extensionista

    if requisitos_conclusao:
        total_cursado = ch_obrigatorias_cursadas + ch_optativas_cursadas
        if total_cursado < requisitos_conclusao.ch_total:
            apto_a_concluir = False
            faltam = requisitos_conclusao.ch_total - total_cursado
            mensagens_pendencias.append(f"Carga horária total insuficiente (faltam {faltam}h).")

        if ch_obrigatorias_cursadas < requisitos_conclusao.ch_obrigatorias:
            apto_a_concluir = False
            faltam = requisitos_conclusao.ch_obrigatorias - ch_obrigatorias_cursadas
            mensagens_pendencias.append(f"Carga horária obrigatória insuficiente (faltam {faltam}h).")

        if ch_optativas_cursadas < requisitos_conclusao.ch_optativas:
            apto_a_concluir = False
            # A variável `faltam_optativas` já foi calculada anteriormente.
            mensagens_pendencias.append(f"Carga horária optativa insuficiente (faltam {faltam_optativas}h).")

        trilhas_hours_only = {name: data['hours'] for name, data in _trilhas_data_map.items()}
        # Verificar trilhas
        trilhas_ok = False
        trilhas_validas = [ch for ch in trilhas_hours_only.values() if ch >= 90]
        if len(trilhas_validas) >= 3:
            trilhas_ok = True
        elif len(trilhas_validas) >= 2 and ch_optativas_cursadas >= requisitos_conclusao.ch_optativas:
            trilhas_ok = True

        if not trilhas_ok:
            apto_a_concluir = False
            mensagens_pendencias.append("Requisitos de trilhas não atendidos (3 Trilhas (ou 2 Trilhas e Optativas Isoladas) + Ciclo de Humanidades).")

        if ch_extensionista_cursada < requisitos_conclusao.ch_extensionista:
            apto_a_concluir = False
            faltam = requisitos_conclusao.ch_extensionista - ch_extensionista_cursada
            mensagens_pendencias.append(f"Carga horária extensionista insuficiente (faltam {faltam}h).")
    else:
        apto_a_concluir = False
        mensagens_pendencias.append("Requisitos de conclusão não definidos para este curso.")
    
    mensagem_status = "Parabéns! Você cumpriu todos os requisitos para a conclusão do curso." if apto_a_concluir else "Existem pendências para a conclusão do curso. Veja abaixo:"

    # --- Preparação dos dados para o template ---
    MIN_HORAS_TRILHA = 90

    # 1. Prepara a lista detalhada de trilhas cursadas
    trilhas_info_list = []
    for name, data in _trilhas_data_map.items():
        horas_cursadas = data['hours']
        concluida = horas_cursadas >= MIN_HORAS_TRILHA
        faltam = MIN_HORAS_TRILHA - horas_cursadas if not concluida else 0
        trilhas_info_list.append({
            'nome': name,
            'horas': horas_cursadas,
            'disciplinas': data['disciplines'],
            'concluida': concluida,
            'faltam': faltam,
        })

    trilhas_info = sorted(
        trilhas_info_list,
        key=lambda x: x['nome']
    )

    # 2. Prepara a lista de resumo de trilhas para o topo da página
    resumo_trilhas = []
    outras_trilhas_cursadas = [t for t in trilhas_info if "humanidades" not in t['nome'].lower()]
    
    # Adiciona o Ciclo de Humanidades
    humanidades = next((t for t in trilhas_info if "humanidades" in t['nome'].lower()), None)
    resumo_trilhas.append({
        'nome': 'Ciclo de Humanidades',
        'concluida': humanidades['concluida'] if humanidades else False
    })

    # Adiciona as outras trilhas cursadas e preenche com placeholders
    for i in range(3):
        if i < len(outras_trilhas_cursadas):
            resumo_trilhas.append(outras_trilhas_cursadas[i])
        else:
            resumo_trilhas.append({'nome': f'Trilha Optativa {i+1}', 'concluida': False})

    return {
        'aluno': aluno_obj,
        'disciplinas_cursadas_objs': disciplinas_aluno_cursou_objs,
        'cursadas_obrigatorias': cursadas_obrigatorias,
        'cursadas_optativas': cursadas_optativas,
        'obrigatorias_faltantes': obrigatorias_faltantes,
        'cursadas_extensionistas': cursadas_extensionistas,
        'trilhas_info': trilhas_info,
        'resumo_trilhas': resumo_trilhas, # Nova lista de resumo
        'isolated_optativas': isolated_optativas, # Optativas que não pertencem a nenhuma trilha
        'ch_humanidades_cursadas': ch_humanidades_cursadas,
        'ch_extensionista_cursada': ch_extensionista_cursada,
        'ch_obrigatorias_cursadas': ch_obrigatorias_cursadas,
        'ch_optativas_cursadas': ch_optativas_cursadas,
        'faltam_obrigatorias': faltam_obrigatorias,
        'faltam_optativas': faltam_optativas,
        'faltam_extensionista': faltam_extensionista,
        'extensionista_concluida': extensionista_concluida,
        'requisitos_conclusao': requisitos_conclusao,
        'apto_a_concluir': apto_a_concluir,
        'mensagem_status': mensagem_status,
        'mensagens_pendencias': mensagens_pendencias,
    }

@login_required
def verificar_conclusao_curso(request, aluno_id):
    """Exibe a página de verificação de conclusão do curso."""
    context = _get_verificacao_conclusao_context(aluno_id)

    # Paginação para Disciplinas Obrigatórias Cursadas
    cursadas_list = context['cursadas_obrigatorias']
    paginator_cursadas = Paginator(cursadas_list, 10) # 10 por página
    page_cursadas_num = request.GET.get('page_cursadas')
    try:
        cursadas_paginadas = paginator_cursadas.page(page_cursadas_num)
    except PageNotAnInteger:
        cursadas_paginadas = paginator_cursadas.page(1)
    except EmptyPage:
        cursadas_paginadas = paginator_cursadas.page(paginator_cursadas.num_pages)

    # Paginação para Disciplinas Obrigatórias Pendentes
    pendentes_list = context['obrigatorias_faltantes']
    paginator_pendentes = Paginator(pendentes_list, 10) # 10 por página
    page_pendentes_num = request.GET.get('page_pendentes')
    try:
        pendentes_paginadas = paginator_pendentes.page(page_pendentes_num)
    except PageNotAnInteger:
        pendentes_paginadas = paginator_pendentes.page(1)
    except EmptyPage:
        pendentes_paginadas = paginator_pendentes.page(paginator_pendentes.num_pages)

    context['cursadas_obrigatorias_paginadas'] = cursadas_paginadas
    context['obrigatorias_faltantes_paginadas'] = pendentes_paginadas

    return render(request, 'syllabus_app/verificar_conclusao.html', context)

@login_required
def gerar_relatorio_pdf(request, aluno_id):
    """Gera e retorna um relatório de conclusão em formato PDF."""
    from django.template.loader import render_to_string
    from django.http import HttpResponse
    try:
        from weasyprint import HTML
    except ImportError:
        messages.error(request, "A exportação para PDF não está disponível. A biblioteca WeasyPrint não foi encontrada.")
        return redirect('verificar_conclusao_curso', aluno_id=aluno_id)

    context = _get_verificacao_conclusao_context(aluno_id)
    html_string = render_to_string('syllabus_app/verificar_conclusao_pdf.html', context)
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_conclusao_{context["aluno"].ra_aluno}.pdf"'
    return response

class AlunoAdicionaDisciplinaView(LoginRequiredMixin, DisciplinaAdderMixin, generic.FormView):
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
        if self.search_input_field_name in self.request.GET:
            initial[self.search_input_field_name] = self.request.GET.get(self.search_input_field_name)
        return initial

    def get(self, request, *args, **kwargs):
        add_this_cod = request.GET.get('add_this_cod')
        retained_search_term = request.GET.get('cod_disciplina_input_retained', '')

        if add_this_cod:
            self.try_add_discipline_to_user(request, request.user, add_this_cod)
            # Re-render the page
            form = self.get_form_class()(initial={self.search_input_field_name: retained_search_term})
            disciplinas_found = self.get_disciplines_for_search(retained_search_term)
            cursadas_cods = self.get_already_cursadas_codes(request.user)
            return self.render_to_response(self.get_context_data(form=form, disciplinas=disciplinas_found, cursadas_cods=cursadas_cods))

        return super().get(request, *args, **kwargs)

    def form_valid(self, form): # Called by FormView's post method if form is valid
        # This method is now only for searching and displaying results.
        search_term = form.cleaned_data.get(self.search_input_field_name, '').strip()
        disciplinas_found = self.get_disciplines_for_search(search_term)

        if disciplinas_found:
            # Always display results, even if only one, as per new requirement
            # Pass already cursadas to template for button state
            cursadas_cods = self.get_already_cursadas_codes(self.request.user)
            return self.render_to_response(
                self.get_context_data(form=form, disciplinas=disciplinas_found, cursadas_cods=cursadas_cods)
            )
        else: # No search term provided (form might be valid but empty if not required, though it is) or no results
            if search_term: # Only add error if a search was attempted
                form.add_error(self.search_input_field_name, 'Nenhuma disciplina encontrada com o termo fornecido.')
            return self.form_invalid(form) # Renders form with errors


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'aluno'): # Ensure aluno is in context
            context['aluno'] = self.request.user.aluno
        if 'cursadas_cods' not in context: # Ensure this is available for the student view
            context['cursadas_cods'] = self.get_already_cursadas_codes(self.request.user) if self.request.user.is_authenticated else []
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
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, success_message)
        return response


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = CustomAuthenticationForm # Seu formulário personalizado

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            # Se "Lembrar-me" não estiver marcado, a sessão expira quando o navegador fechar.
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return super().form_valid(form)

    def get_success_url(self):
        url = self.get_redirect_url()
        # Lista de nomes de URL que não devem ser o destino após o login
        # se passados como 'next'
        restricted_next_pages = [
            'register', 'login', 'welcome', 
            'password_reset', 'password_reset_done', 
            'password_reset_confirm', 'password_reset_complete'
        ]
        if url:
            try:
                # Remove query parameters (como ?next=...) antes de resolver o nome da URL
                path_to_resolve = url.split('?')[0]
                match = resolve(path_to_resolve)
                if match.url_name in restricted_next_pages:
                    # Se 'next' for uma dessas páginas restritas, redireciona para LOGIN_REDIRECT_URL
                    return resolve_url(settings.LOGIN_REDIRECT_URL)
            except Resolver404:
                # Se a URL 'next' não resolver, usa LOGIN_REDIRECT_URL como fallback
                return resolve_url(settings.LOGIN_REDIRECT_URL)
        
        # Se 'url' (next) for válido e não restrito, usa-o.
        # Caso contrário (url é None ou vazio), usa LOGIN_REDIRECT_URL.
        return url or resolve_url(settings.LOGIN_REDIRECT_URL)

class CustomLogoutView(LogoutView):
    def get_next_page(self):
        next_page_param = self.request.POST.get('next', self.request.GET.get('next'))
        if next_page_param:
            try:
                path_to_resolve = next_page_param.split('?')[0]
                match = resolve(path_to_resolve)
                if match.url_name == 'register':
                    return resolve_url(settings.LOGOUT_REDIRECT_URL or '/')
            except Resolver404:
                pass
        return super().get_next_page()