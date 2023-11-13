from django.contrib import admin
from syllabus_app.models import Aluno, Departamento, Curso, ConjuntoDisciplinas, Disciplina, DisciplinasCursadas, ReqConclusao

admin.site.register(Aluno)
admin.site.register(Departamento)
admin.site.register(Curso)
admin.site.register(ConjuntoDisciplinas)
admin.site.register(Disciplina)
admin.site.register(DisciplinasCursadas)
admin.site.register(ReqConclusao)