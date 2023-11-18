from django.contrib import admin
from syllabus_app.models import Aluno, Departamento, Curso, ConjuntoDisciplinas, Disciplina, DisciplinasCursadas, ReqConclusao

admin.site.register(Aluno)
admin.site.register(Departamento)
admin.site.register(Curso)
admin.site.register(ConjuntoDisciplinas)
admin.site.register(Disciplina)
#admin.site.register(DisciplinasCursadas)
admin.site.register(ReqConclusao)

@admin.register(DisciplinasCursadas)
class DisciplinasCursadasAdmin(admin.ModelAdmin):
    list_display = ('ra_aluno', 'cod_disciplina')
#    list_filter = ('ra_aluno')

    fieldsets = (
        (None, {
            'fields': ('ra_aluno','cod_disciplina')
        }),
    )