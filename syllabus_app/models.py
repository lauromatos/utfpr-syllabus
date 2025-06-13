from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings


class Aluno(models.Model):
    """Modelo de cadastro de alunos."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    ra_aluno = models.IntegerField(unique=True, help_text='Digite seu RA', null=False)
    nome_aluno = models.CharField(max_length=60, help_text='Digite seu Nome')
    nome_curso = models.ForeignKey('Curso', on_delete=models.SET_NULL, null=True)
    # O campo senha foi removido, será gerenciado pelo User do Django.

    class Meta:
        ordering = ['ra_aluno', 'nome_aluno']

    def get_absolute_url(self):
            return reverse('aluno-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.ra_aluno} - {self.nome_aluno}'

# É importante que o username do User seja o ra_aluno.
# A ForeignKey em DisciplinasCursadas para AUTH_USER_MODEL usa to_field='username'.
# Isso significa que o valor armazenado em DisciplinasCursadas.ra_aluno_id será o username do User.

class Departamento(models.Model):
    departamento = models.CharField(max_length=10, unique=True, help_text='Digite a sigla do Departamento')
    nome_departamento = models.CharField(max_length=45, help_text='Digite o nome do Departamento')

    class Meta:
        ordering = ['departamento', 'nome_departamento']

    def get_absolute_url(self):
            return reverse('departamento-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.departamento} - {self.nome_departamento}'


class Curso(models.Model):
    nome_curso = models.CharField(max_length=45, help_text='Digite o nome do curso')
    departamento = models.ForeignKey('Departamento', on_delete=models.SET_NULL, null=True, help_text='Selecione o Departamento')

    def __str__(self):
        return self.nome_curso

class ConjuntoDisciplinas(models.Model):
    cod_optativa = models.CharField(max_length=4, help_text='Digite o nome do curso')
    nome_conjunto = models.CharField(max_length=45, help_text='Digite o nome do curso')
    ch_obrigatoria = models.DecimalField(max_digits=4, decimal_places=0, help_text='Digite o nome do curso')
#    ch_cursada = models.DecimalField(max_digits=3, decimal_places=0)
#    ch_faltando = models.DecimalField(max_digits=3, decimal_places=0)
#    ch_validada = models.DecimalField(max_digits=3, decimal_places=0)

    class Meta:
        ordering = ['cod_optativa', 'nome_conjunto']

    def get_absolute_url(self):
        return reverse('conjuntodisciplinas-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.cod_optativa} - {self.nome_conjunto}'

class Disciplina(models.Model):
    cod_disciplina = models.CharField(max_length=10)
    nome_disciplina = models.CharField(max_length=70)
    Departamento = models.ForeignKey('Departamento', on_delete=models.SET_NULL, null=True)
    carga_horaria = models.CharField(max_length=3)
    obrigatoria = models.BooleanField()
    cod_optativa = models.ForeignKey('ConjuntoDisciplinas', on_delete=models.SET_NULL, null=True)
    periodo = models.DecimalField(max_digits=1, decimal_places=0)
    extensionista = models.BooleanField()

    class Meta:
        ordering = ['cod_disciplina', 'nome_disciplina']

    def get_absolute_url(self):
        return reverse('disciplina-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.cod_disciplina} - {self.nome_disciplina}'

class DisciplinasCursadas(models.Model):
    ra_aluno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, to_field='username')
    cod_disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['ra_aluno', 'cod_disciplina']

    def get_absolute_url(self):
        return reverse('disciplinascursadas-detail', args=[str(self.id)])

    def __str__(self):
        return f"{self.ra_aluno.username} - {self.cod_disciplina}"

class ReqConclusao(models.Model):
    nome_curso = models.ForeignKey('Curso', on_delete=models.SET_NULL, null=True)
    ch_total = models.SmallIntegerField()
    ch_obrigatorias = models.SmallIntegerField()
    ch_optativas = models.SmallIntegerField()
    ch_estagio = models.SmallIntegerField()

    class Meta:
        ordering = ['nome_curso', 'ch_total', 'ch_obrigatorias', 'ch_optativas', 'ch_estagio']

    def get_absolute_url(self):
        return reverse('reqconclusao-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.nome_curso} - {self.ch_total} - {self.ch_obrigatorias} - {self.ch_optativas} - {self.ch_estagio}'