from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from .models import Disciplina, DisciplinasCursadas

class AuthListViewMixin(LoginRequiredMixin):
    paginate_by = 10

class DisciplinaAdderMixin:
    search_input_field_name = 'cod_disciplina_input' # Can be overridden by views if needed

    def get_disciplines_for_search(self, search_term):
        """
        Performs a search for disciplines based on the search term.
        """
        if search_term:
            return list(
                Disciplina.objects.filter(
                    Q(nome_disciplina__icontains=search_term) | Q(cod_disciplina__iexact=search_term)
                ).distinct()
            )
        return []

    def get_already_cursadas_codes(self, user_obj):
        """
        Returns a list of cod_disciplina for disciplines already cursadas by the user.
        """
        if user_obj:
            return list(DisciplinasCursadas.objects.filter(ra_aluno=user_obj).values_list('cod_disciplina__cod_disciplina', flat=True))
        return []

    def try_add_discipline_to_user(self, request, user_obj, disciplina_cod_to_add):
        """
        Attempts to add a discipline to a user's cursadas list.
        Sets messages for success or failure. Returns True if added, False otherwise.
        """
        try:
            disciplina_obj = Disciplina.objects.get(cod_disciplina__iexact=disciplina_cod_to_add)
            if DisciplinasCursadas.objects.filter(ra_aluno=user_obj, cod_disciplina=disciplina_obj).exists():
                messages.error(request, f"Disciplina '{disciplina_obj}' já cadastrada para {user_obj.username}.")
                return False
            else:
                DisciplinasCursadas.objects.create(ra_aluno=user_obj, cod_disciplina=disciplina_obj)
                messages.success(request, f"Disciplina '{disciplina_obj}' adicionada com sucesso para {user_obj.username}.")
                return True
        except Disciplina.DoesNotExist:
            messages.error(request, f"Disciplina com código '{disciplina_cod_to_add}' não encontrada.")
        except Exception as e:
            messages.error(request, f"Ocorreu um erro ao adicionar a disciplina: {str(e)}")
        return False