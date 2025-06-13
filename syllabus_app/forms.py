from django import forms
from django.contrib.auth.models import User
from .models import Aluno, Curso
from django.core.exceptions import ValidationError

class UserRegistrationForm(forms.ModelForm):
    ra_aluno = forms.IntegerField(label='RA', help_text='Seu RA será seu nome de usuário.')
    nome_aluno = forms.CharField(max_length=60, label='Nome Completo')
    nome_curso = forms.ModelChoiceField(queryset=Curso.objects.all(), label='Curso')
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Confirme a Senha', widget=forms.PasswordInput)

    class Meta:
        model = User # Usamos User como base, mas vamos criar Aluno também
        fields = ['ra_aluno', 'nome_aluno', 'nome_curso', 'password', 'password_confirm']

    def clean_ra_aluno(self):
        ra = self.cleaned_data.get('ra_aluno')
        if User.objects.filter(username=str(ra)).exists():
            raise ValidationError("Um usuário com este RA já existe.")
        if Aluno.objects.filter(ra_aluno=ra).exists():
            # Esta verificação é redundante se o User já foi checado e o username é o RA
            # Mas mantemos por segurança caso a lógica de username mude.
            raise ValidationError("Um aluno com este RA já está cadastrado.")
        return ra

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise ValidationError("As senhas não coincidem.")
        return password_confirm

    def save(self, commit=True):
        # Não chamamos super().save() diretamente pois precisamos criar User e Aluno separadamente.
        ra_aluno_val = self.cleaned_data['ra_aluno']
        nome_aluno_val = self.cleaned_data['nome_aluno']
        nome_curso_val = self.cleaned_data['nome_curso']
        password_val = self.cleaned_data['password']

        user = User.objects.create_user(username=str(ra_aluno_val), password=password_val)
        aluno = Aluno.objects.create(user=user, ra_aluno=ra_aluno_val, nome_aluno=nome_aluno_val, nome_curso=nome_curso_val)
        
        # Não há instância do User para retornar como no ModelForm padrão,
        # mas a operação de salvar foi concluída.
        return user # Retornar o usuário criado pode ser útil.