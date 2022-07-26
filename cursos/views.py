from django.shortcuts import reverse, render, get_object_or_404, redirect
from django.contrib import messages
from django.db.utils import IntegrityError
from django.views.generic.edit import CreateView, UpdateView
from django.http import JsonResponse, HttpResponse

from cursos.forms import CursoModelForm
from cursos.models import Curso, CursoLikes, Autor


def pagina_inicial(request):
    return render(request, "cursos/pagina_inicial.html")


def listar_cursos(request):
    ordem = request.GET.get("ordenacao", "nome")
    cursos = Curso.objects.all().order_by(ordem)
    context = {
        'cursos': cursos,
        'likes': [likes.curso for likes in CursoLikes.objects.filter(user=request.user)],
    }
    return render(request, 'cursos/listar_cursos.html', context)


def listar_aulas(request, pk):
    curso = Curso.objects.get(id=pk)
    context = {
        "curso": curso,
        "aulas": curso.aulas.all()
    }
    return render(request, 'cursos/listar_aulas.html', context)


class CursoMixin(object):
    model = Curso
    form_class = CursoModelForm
    context_object_name = "curso"

    def get_success_url(self):
        return reverse("cursos.listar.tudo")


class NovoCursoView(CursoMixin, CreateView):
    template_name = "cursos/curso_novo.html"


class AlterarCursoView(CursoMixin, UpdateView):
    template_name = "cursos/curso_alterar.html"


def like_no_curso(request, pk):
    # FYI
    # try:
    #     curso = Curso.objects.get(pk=pk)
    # except Curso.DoesNotExist:
    #     raise Http404("Given query not found....")

    user = request.user
    curso = get_object_or_404(Curso, pk=pk)

    try:
        CursoLikes.objects.create(user=user, curso=curso)
        messages.success(request, f'{curso.autor} agradece seu LIKE!')

    except IntegrityError as erro:
        # SOLUCAO 1
        # messages.error(request, f'Ops! você já deu like no {curso.nome}!')
        CursoLikes.objects.get(user=user, curso=curso).delete()
        messages.success(request, f'Like removido!')

    # SOLUCAO 1
    # return render(request, 'cursos/like_complete.html')
    return redirect(reverse('cursos.listar.tudo'))


def api_like_no_curso(request, pk):
    curso = get_object_or_404(Curso, id=pk)
    try:
        CursoLikes.objects.create(user=request.user, curso=curso)
        resposta = {
            'like': True,
        }

    except IntegrityError as error:
        CursoLikes.objects.get(user=request.user, curso=curso).delete()
        resposta = {
            'like': False,
        }

    resposta['likes'] = curso.likes.count()
    return JsonResponse(resposta)


def cursos_form(request):
    if request.method == 'POST':
        nome_post = request.POST.get('nome')
        descricao_post = request.POST.get('descricao')
        imagem_post = request.POST.get('imagem')
        ativo_post = request.POST.get('ativo', 'false').lower() == 'true'
        autor_id = int(request.POST.get('author'))
        curso_objeto = Curso(
            nome=nome_post,
            descricao=descricao_post,
            imagem=imagem_post,
            ativo=ativo_post,
            autor_id=autor_id

        )
        try:
            curso_objeto.save()
        except IntegrityError:
            autores = Autor.objects.order_by('nome').all()
            contexto = {'autores': autores}
            erros={'nome': 'Nome de curso duplicado, escolha outro'}
            contexto ={
                'autores': autores,
                'erros': erros,
                'curso': curso_objeto
            }
            return render(request, 'cursos/cursos_form.html', contexto, status=400)
        else:
            return redirect('cursos.listar.tudo')

    autores = Autor.objects.order_by('nome').all()
    contexto = {'autores': autores}
    return render(request, 'cursos/cursos_form.html', contexto)
