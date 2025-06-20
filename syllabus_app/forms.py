from django import forms
from django.contrib.auth.models import User
from .models import Aluno, Curso, DisciplinasCursadas, Disciplina, ReqConclusao
from django.core.exceptions import ValidationError

class UserRegistrationForm(forms.Form):
    ra_aluno = forms.IntegerField(label='RA', help_text='Seu RA será seu nome de usuário.')
    nome_aluno = forms.CharField(max_length=60, label='Nome Completo')
    nome_curso = forms.ModelChoiceField(queryset=Curso.objects.all(), label='Curso')
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Confirme a Senha', widget=forms.PasswordInput)

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
        required=True # Ensure input is provided for searching
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
        self.fields['ch_extensionista'].widget = BlankZeroInput()
        # Como ch_extensionista tem blank=True no modelo, o campo do formulário terá required=False.
        # Se o usuário submeter vazio (o widget renderizou ''), ele será validado como None.
        # Ao salvar, o default=0 do modelo será aplicado se o valor for None.

class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ['cod_disciplina', 'nome_disciplina', 'Departamento', 'curso', 
                  'carga_horaria', 'obrigatoria', 'cod_optativa', 'periodo', 'extensionista']
        # Se o usuário submeter vazio (o widget renderizou ''), ele será validado como None.
        # Ao salvar, o default=0 do modelo será aplicado se o valor for None.