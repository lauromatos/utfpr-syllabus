from django import forms
from django.contrib.auth.models import User
from .models import Aluno, Curso, Departamento, ConjuntoDisciplinas, Disciplina, DisciplinasCursadas, ReqConclusao
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm

class UserRegistrationForm(forms.Form):
    ra_aluno = forms.IntegerField(
        label='RA', 
        help_text='Seu RA será seu nome de usuário.',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu RA'})
    )
    nome_aluno = forms.CharField(
        max_length=60, 
        label='Nome Completo',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome completo'})
    )
    nome_curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(), 
        label='Curso',
        empty_label="Selecione seu curso",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Senha', 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua senha'})
    )
    password_confirm = forms.CharField(
        label='Confirme a Senha', 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme sua senha'})
    )

    def clean_ra_aluno(self):
        ra = self.cleaned_data.get('ra_aluno')
        if User.objects.filter(username=str(ra)).exists():
            raise ValidationError("Um usuário com este RA já existe.")
        if Aluno.objects.filter(ra_aluno=ra).exists():
            raise ValidationError("Um aluno com este RA já está cadastrado.")
        return ra

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise ValidationError("As senhas não coincidem.")
        return password_confirm

    def save(self, commit=True):
        ra_aluno_val = self.cleaned_data['ra_aluno']
        nome_aluno_val = self.cleaned_data['nome_aluno']
        nome_curso_val = self.cleaned_data['nome_curso']
        password_val = self.cleaned_data['password']

        user = User.objects.create_user(username=str(ra_aluno_val), password=password_val)
        aluno = Aluno.objects.create(user=user, ra_aluno=ra_aluno_val, nome_aluno=nome_aluno_val, nome_curso=nome_curso_val)
        
        return user

class AlunoAdicionaDisciplinaForm(forms.Form): # Changed from ModelForm to Form
    cod_disciplina_input = forms.CharField(
        label='Disciplina (Código ou Nome)',
        help_text='Digite o código ou nome da disciplina para buscar.',
        max_length=100,
        required=True, # Ensure input is provided for searching <-- VÍRGULA ADICIONADA AQUI
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código ou Nome da Disciplina'})
    )


class BlankZeroInput(forms.NumberInput):
    def format_value(self, value):
        if value == 0 or value is None: # Se o valor for 0 ou None
            return '' # Exibe como vazio no template
        return super().format_value(value)

class ReqConclusaoForm(forms.ModelForm):
    class Meta:
        model = ReqConclusao
        fields = ['nome_curso', 'ch_total', 'ch_obrigatorias', 'ch_optativas', 'ch_estagio', 'ch_extensionista']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'ch_extensionista' and not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                existing_attrs = field.widget.attrs
                existing_class = existing_attrs.get('class', '')
                field.widget.attrs['class'] = f'{existing_class} form-control'.strip()
        
        # Atribui o widget customizado para ch_extensionista
        self.fields['ch_extensionista'].widget = BlankZeroInput()
        # Adiciona a classe 'form-control' explicitamente a este widget customizado
        # para garantir a consistência visual com os outros campos.
        self.fields['ch_extensionista'].widget.attrs['class'] = 'form-control'

class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ['cod_disciplina', 'nome_disciplina', 'Departamento', 'curso', 
                  'carga_horaria', 'obrigatoria', 'cod_optativa', 'periodo', 'extensionista']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, BlankZeroInput)):
                existing_attrs = field.widget.attrs
                existing_class = existing_attrs.get('class', '')
                field.widget.attrs['class'] = f'{existing_class} form-control'.strip()
            elif isinstance(field.widget, forms.CheckboxInput): # Especificamente para checkboxes
                 field.widget.attrs['class'] = 'form-check-input'

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Usuário', widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}))
    password = forms.CharField(label='Senha', strip=False, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    remember_me = forms.BooleanField(
        label='Lembrar-me',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = ['departamento', 'nome_departamento']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields(): # Itera sobre campos visíveis
            visible.field.widget.attrs['class'] = 'form-control'

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nome_curso', 'departamento']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class DisciplinasCursadasForm(forms.ModelForm): # Esta é a definição que será usada para o admin
    cod_disciplina_input = forms.CharField(
        label='Disciplina (Código ou Nome para busca)',
        help_text='Digite o código ou nome da disciplina para buscar.',
        max_length=100,
        required=False, # O termo de busca não é obrigatório para carregar a página inicialmente
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite código ou nome'})
    )
    class Meta:
        model = DisciplinasCursadas
        fields = ['ra_aluno'] # Apenas ra_aluno do modelo para seleção inicial

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'ra_aluno' in self.fields:
            self.fields['ra_aluno'].widget.attrs['class'] = 'form-control'
            self.fields['ra_aluno'].label = "Aluno (RA)"
            self.fields['ra_aluno'].queryset = User.objects.order_by('username') # Garante que o queryset aponte para User
            self.fields['ra_aluno'].empty_label = "Selecione um Aluno" # Adiciona um rótulo vazio para o select

class ConjuntoDisciplinasForm(forms.ModelForm):
    class Meta:
        model = ConjuntoDisciplinas 
        fields = ['cod_optativa', 'nome_conjunto', 'ch_obrigatoria']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'