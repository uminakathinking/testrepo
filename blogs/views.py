from django.db.models import Count,Q
from django.http import Http404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from .models import Post,Category,Tag
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,redirect
from django.views.generic.edit import CreateView
from .forms import CommentForm,ReplayForm
from .models import Post,Category,Tag,Comment,Replay

class PostDetailView(DetailView):
    model = Post
    
    def get_object(self,queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_public and not self.request.user.is_authenticated:
            raise Http404
        return obj

class IndexView(ListView):
    model = Post
    template_name = 'blogs/index.html'
    context_object_name = 'index'
    paginate_by = 1

class CategoryListView(ListView):
    queryset = Category.objects.annotate(
        num_posts = Count('post',filter=Q(post__is_public=True)))

class TagListView(ListView):
    queryset = Tag.objects.annotate(
        num_posts = Count('post',filter=Q(post__is_public=True)))

class CategoryPostView(ListView):
    model = Post
    template_name = 'blogs/category_post.html'

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        self.category = get_object_or_404(Category,slug=category_slug)
        qs = super().get_queryset.filter(category=self.category)
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context
    
class TagPostView(ListView):
    model = Post
    template_name = 'blogs/tag_post.html'

    def get_queryset(self):
        tag_slug = self.kwargs['tag_slug']
        self.tag = get_object_or_404(Tag,slug=tag_slug)
        qs = super().get_queryset().filter(tags=self.tag)
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        return context
    

    
class SearchPostView(ListView):
    model =Post
    template_name= 'blogs/search_post.html'
    paginate_by = 3

    def get_queryset(self):
        query = self.request.GET.get('q',None)
        lookups = (
            Q(title__icontains=query)  |     
            Q(text__icontains=query)    | 
            Q(category__name__icontains=query)        |
            Q(tags__name__icontains=query)       
        )
        if query is not None:
            qs = super().get_queryset().filter(lookups).distinct()
            return qs
        qs = super().get_queryset()
        return qs

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q')
        context['query'] = query
        return context
    
class CommentFormView(CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self,form):
        comment = form.save(commit=False)
        post_pk = self.kwargs['pk']
        comment.post = get_object_or_404(Post,pk=post_pk)
        comment.save()
        return redirect('blogs:post_detail',pk=post_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_pk = self.kwargs['pk']
        context["post"] = get_object_or_404(Post,pk=post_pk)
        return context

@login_required
def comment_approve(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    comment.approve()
    return redirect('blogs:post_detail',pk=comment.post.pk)

@login_required
def comment_remove(request,pk):
    comment =  get_object_or_404(Comment,pk=pk)
    comment.delete()
    return redirect('blogs:post_detail',pk=comment.post.pk)

class ReplayFormView(CreateView):
    model = Replay
    form_class = ReplayForm

    def form_valid(self,form):
        replay = form.save(commit=False)
        comment_pk = self.kwargs['pk']
        replay.comment = get_object_or_404(Comment,pk=comment_pk)
        replay.save()
        return redirect('blogs:post_detail',pk=replay.comment.post.pk)

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        comment_pk = self.kwargs['pk']
        context['comments'] = get_object_or_404(Comment,pk=comment_pk)
        return context

@login_required
def replay_approve(request,pk):
    replay = get_object_or_404(Replay,pk=pk)
    replay.approve()
    return redirect('blogs:post_detail',pk=replay.comment.post.pk)

@login_required
def replay_remove(request,pk):
    replay = get_object_or_404(Replay,pk=pk)
    replay.delete()
    return redirect('blogs:post_detail',pk=replay.comment.post.pk)
    