from django.urls import path
from syllabus_app import views


urlpatterns = [
    # URLs principais e de autenticação
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),

    # URLs for Curso
    path('curso/', views.CursoListView.as_view(), name='curso'),
    path('curso/<int:pk>', views.CursoDetailView.as_view(), name='curso-detail'),
    path('curso/create/', views.CursoCreate.as_view(), name='curso-create'),
    path('curso/<int:pk>/update/', views.CursoUpdate.as_view(), name='curso-update'),
    path('curso/<int:pk>/delete/', views.CursoDelete.as_view(), name='curso-delete'),

    # URLs for DisciplinasCursadas
    path('disciplinascursadas/', views.DisciplinasCursadasAlunoListView.as_view(), name='disciplinascursadas'),
    path('disciplinascursadas/<int:pk>', views.DisciplinasCursadasDetailView.as_view(), name='disciplinascursadas-detail'),
    path('disciplinascursadas/create/', views.DisciplinasCursadasCreate.as_view(), name='disciplinascursadas-create'),
    path('disciplinascursadas/<int:pk>/update/', views.DisciplinasCursadasUpdate.as_view(), name='disciplinascursadas-update'),
    path('disciplinascursadas/<int:pk>/delete/', views.DisciplinasCursadasDelete.as_view(), name='disciplinascursadas-delete'),
    path('aluno/disciplinas/adicionar/', views.AlunoAdicionaDisciplinaView.as_view(), name='aluno_adiciona_disciplina'),
    path('aluno/disciplinas/<int:pk>/remover/', views.AlunoRemoveDisciplinaView.as_view(), name='aluno_remove_disciplina'),

    # URLs for Departamento
    path('departamento/', views.DepartamentoListView.as_view(), name='departamento'),
    path('departamento/<int:pk>', views.DepartamentoDetailView.as_view(), name='departamento-detail'),
    path('departamento/create/', views.DepartamentoCreate.as_view(), name='departamento-create'),
    path('departamento/<int:pk>/update/', views.DepartamentoUpdate.as_view(), name='departamento-update'),
    path('departamento/<int:pk>/delete/', views.DepartamentoDelete.as_view(), name='departamento-delete'),

    # URLs for Disciplina
    path('disciplina/', views.DisciplinaListView.as_view(), name='disciplina'),
    path('disciplina/<int:pk>', views.DisciplinaDetailView.as_view(), name='disciplina-detail'),
    path('disciplina/create/', views.DisciplinaCreate.as_view(), name='disciplina-create'),
    path('disciplina/<int:pk>/update/', views.DisciplinaUpdate.as_view(), name='disciplina-update'),
    path('disciplina/<int:pk>/delete/', views.DisciplinaDelete.as_view(), name='disciplina-delete'),

    # URLs for ConjuntoDisciplinas
    path('conjuntodisciplinas/', views.ConjuntoDisciplinasListView.as_view(), name='conjuntodisciplinas'),
    path('conjuntodisciplinas/<int:pk>', views.ConjuntoDisciplinasDetailView.as_view(), name='conjuntodisciplinas-detail'),
    path('conjuntodisciplinas/create/', views.ConjuntoDisciplinasCreate.as_view(), name='conjuntodisciplinas-create'),
    path('conjuntodisciplinas/<int:pk>/update/', views.ConjuntoDisciplinasUpdate.as_view(), name='conjuntodisciplinas-update'),
    path('conjuntodisciplinas/<int:pk>/delete/', views.ConjuntoDisciplinasDelete.as_view(), name='conjuntodisciplinas-delete'),

    # URLs for ReqConclusao
    path('reqconclusao/', views.ReqConclusaoListView.as_view(), name='reqconclusao'),
    path('reqconclusao/<int:pk>', views.ReqConclusaoDetailView.as_view(), name='reqconclusao-detail'),
    path('reqconclusao/create/', views.ReqConclusaoCreate.as_view(), name='reqconclusao-create'),
    path('reqconclusao/<int:pk>/update/', views.ReqConclusaoUpdate.as_view(), name='reqconclusao-update'),
    path('reqconclusao/<int:pk>/delete/', views.ReqConclusaoDelete.as_view(), name='reqconclusao-delete'),
]

urlpatterns += [
    path('verificarconclusao/<int:aluno_id>/', views.verificar_conclusao_curso, name='verificar_conclusao_curso'),
]
