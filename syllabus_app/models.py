from django.db import models
from django.urls import reverse 

class Aluno(models.Model):
    """Model de cadastro de alunos."""
    ra_aluno = models.IntegerField(primary_key=True, help_text='Digite seu RA')
    nome_aluno = models.CharField(max_length=60, help_text='Digite seu Nome')
    nome_curso = models.ForeignKey('Curso', on_delete=models.SET_NULL, null=True)
    senha = models.CharField(max_length=64, help_text='Digite uma senha')

    class Meta:
        ordering = ['ra_aluno', 'nome_aluno']

    def get_absolute_url(self):
            """Returns the url to access a particular Departamento instance."""
            return reverse('detalhe-Aluno', args=[str(self.id)])

    def __str__(self):
        return f'{self.ra_aluno} - {self.nome_aluno}'
    

class Departamento(models.Model):
    Departamento = models.CharField(max_length=10, primary_key=True)
    nome_departamento = models.CharField(max_length=45)

    class Meta:
        ordering = ['Departamento', 'nome_departamento']

    def get_absolute_url(self):
            """Returns the url to access a particular Departamento instance."""
            return reverse('detalhe-Departamento', args=[str(self.id)])

    def __str__(self):
        return f'{self.Departamento} - {self.nome_departamento}'


class Curso(models.Model):
    nome_curso = models.CharField(max_length=45, primary_key=True, help_text='Digite o nome do curso')
    Departamento = models.ForeignKey('Departamento', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.nome_curso

class ConjuntoDisciplinas(models.Model):
    cod_optativa = models.CharField(max_length=4, primary_key=True)
    nome_conjunto = models.CharField(max_length=45)
    ch_obrigatoria = models.DecimalField(max_digits=4, decimal_places=0)
#    ch_cursada = models.DecimalField(max_digits=3, decimal_places=0)
#    ch_faltando = models.DecimalField(max_digits=3, decimal_places=0)
#    ch_validada = models.DecimalField(max_digits=3, decimal_places=0)

    class Meta:
        ordering = ['cod_optativa', 'nome_conjunto']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('detalhe-optativa', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.cod_optativa} - {self.nome_conjunto}'

class Disciplina(models.Model):
    cod_disciplina = models.CharField(max_length=10, primary_key=True)
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
        """Returns the url to access a particular author instance."""
        return reverse('detalhe-disciplina', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.cod_disciplina} - {self.nome_disciplina}'

class DisciplinasCursadas(models.Model):
    ra_aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    cod_disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['ra_aluno', 'cod_disciplina']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('detalhe-disciplinascursadas', args=[str(self.id)])

    def __str__(self):
        return f"{self.ra_aluno} - {self.cod_disciplina}"

class ReqConclusao(models.Model):
    nome_curso = models.ForeignKey('Curso', on_delete=models.SET_NULL, null=True)
    ch_total = models.SmallIntegerField()
    ch_optativas = models.SmallIntegerField()
    ch_estagio = models.SmallIntegerField()

    class Meta:
        ordering = ['nome_curso', 'ch_total', 'ch_optativas', 'ch_estagio']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('detalhe-optativa', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.nome_curso} - {self.ch_total} - {self.ch_optativas} - {self.ch_estagio}'