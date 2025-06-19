import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from syllabus_app.models import Disciplina, Departamento, ConjuntoDisciplinas

class Command(BaseCommand):
    help = 'Importa disciplinas de um arquivo CSV para o banco de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file', 
            type=str, 
            nargs='?', # Torna o argumento opcional
            help='O caminho para o arquivo CSV a ser importado. Se não fornecido, tenta "syllabus_app/data/matriz_curricular_completa.csv"'
        )

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        if not csv_file_path:
            # Constrói o caminho padrão relativo à raiz do projeto
            csv_file_path = os.path.join(settings.BASE_DIR, 'syllabus_app', 'data', 'matriz_curricular_completa.csv')
            self.stdout.write(self.style.NOTICE(f'Nenhum arquivo CSV fornecido. Usando o padrão: {csv_file_path}'))

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                # next(reader) # Descomente se o seu CSV tiver uma linha de cabeçalho que você queira pular

                for row_number, row in enumerate(reader, 1):
                    if not any(field.strip() for field in row): # Pula linhas completamente vazias
                        self.stdout.write(self.style.WARNING(f'Linha {row_number} está vazia e será ignorada.'))
                        continue
                    
                    if len(row) < 8:
                        self.stdout.write(self.style.ERROR(f'Linha {row_number} tem menos colunas que o esperado ({len(row)} de 8) e será ignorada: {row}'))
                        continue

                    cod_disciplina = row[0].strip()
                    nome_disciplina = row[1].strip()
                    departamento_sigla = row[2].strip()
                    carga_horaria_str = row[3].strip()
                    obrigatoria_str = row[4].strip().lower()
                    cod_optativa_str = row[5].strip()
                    periodo_str = row[6].strip()
                    extensionista_str = row[7].strip().lower()

                    if not cod_disciplina:
                        self.stdout.write(self.style.WARNING(f'Linha {row_number} não possui código da disciplina e será ignorada: {row}'))
                        continue
                    
                    if not nome_disciplina:
                        self.stdout.write(self.style.WARNING(f'Linha {row_number} (Disciplina: {cod_disciplina}) não possui nome e será ignorada.'))
                        continue

                    # Tratar Departamento
                    departamento_obj = None
                    if departamento_sigla:
                        departamento_obj, created = Departamento.objects.get_or_create(
                            departamento=departamento_sigla,
                            defaults={'nome_departamento': ''} # Cadastra sem nome completo se não existir
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Departamento "{departamento_sigla}" criado.'))
                    
                    # Tratar Carga Horária
                    carga_horaria = '0' # Default se vazio ou inválido
                    if carga_horaria_str.isdigit():
                        carga_horaria = carga_horaria_str
                    elif carga_horaria_str:
                         self.stdout.write(self.style.WARNING(f'Carga horária inválida "{carga_horaria_str}" para {cod_disciplina} na linha {row_number}. Usando "0".'))


                    # Tratar Obrigatória
                    obrigatoria = obrigatoria_str == 'sim'

                    # Tratar Conjunto de Disciplinas (cod_optativa)
                    conjunto_obj = None
                    if cod_optativa_str: # Agora '0000' é um código válido
                        conjunto_obj, created = ConjuntoDisciplinas.objects.get_or_create(
                            cod_optativa=cod_optativa_str,
                            defaults={'nome_conjunto': f'Conjunto {cod_optativa_str}', 'ch_obrigatoria': 0} # ch_obrigatoria default
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Conjunto de Disciplinas "{cod_optativa_str}" criado.'))
                    
                    # Tratar Período
                    periodo = 0 # Default se vazio ou inválido
                    if periodo_str.isdigit():
                        periodo = int(periodo_str)
                    elif periodo_str:
                        self.stdout.write(self.style.WARNING(f'Período inválido "{periodo_str}" para {cod_disciplina} na linha {row_number}. Usando "0".'))


                    # Tratar Extensionista
                    extensionista = extensionista_str == 'sim'

                    # Criar ou atualizar Disciplina
                    disciplina, created = Disciplina.objects.update_or_create(
                        cod_disciplina=cod_disciplina,
                        defaults={
                            'nome_disciplina': nome_disciplina,
                            'Departamento': departamento_obj,
                            'carga_horaria': carga_horaria,
                            'obrigatoria': obrigatoria,
                            'cod_optativa': conjunto_obj,
                            'periodo': periodo,
                            'extensionista': extensionista,
                        }
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Disciplina "{cod_disciplina} - {nome_disciplina}" criada com sucesso.'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Disciplina "{cod_disciplina} - {nome_disciplina}" atualizada com sucesso.'))

        except FileNotFoundError:
            raise CommandError(f'Arquivo "{csv_file_path}" não encontrado.')
        except Exception as e:
            raise CommandError(f'Um erro ocorreu: {e}')

        self.stdout.write(self.style.SUCCESS('Importação concluída.'))