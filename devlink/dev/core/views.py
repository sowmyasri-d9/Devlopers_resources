from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from .models import Like, Resource, Category, Tag, Bookmark
from .forms import ResourceForm, EmailShareForm
from rest_framework import generics, permissions
from .forms import CommentForm
from .models import Comment
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.core.mail import send_mail

from .serializers import (
    ResourceSerializer, 
    ResourceCreateSerializer,
    CategorySerializer,
    TagSerializer,
    BookmarkSerializer
)

# HTML Views
class HomeView(ListView):
    model = Resource
    template_name = 'core/home.html'
    context_object_name = 'resources'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get filter parameters from request
        search = self.request.GET.get('search')
        category = self.request.GET.get('category')
        author = self.request.GET.get('author')
        tag = self.request.GET.get('tag')
        filter_type = self.request.GET.get('filter', 'all')
        
        # Apply filters
        if search:
            queryset = queryset.filter(title__icontains=search)
        if category:
            queryset = queryset.filter(category__slug=category)
        if author:
            queryset = queryset.filter(author__username=author)
        if tag:
            queryset = queryset.filter(tags__slug=tag)
            
        # Apply my/others filter
        if filter_type == 'my' and self.request.user.is_authenticated:
            queryset = queryset.filter(author=self.request.user)
        elif filter_type == 'others' and self.request.user.is_authenticated:
            queryset = queryset.exclude(author=self.request.user)
            
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['authors'] = User.objects.filter(resource__isnull=False).distinct()
        context['tags'] = Tag.objects.all()
        context['current_filter'] = self.request.GET.get('filter', 'all')  # Add current filter to context
        return context

class ResourceDetailView(DetailView):
    model = Resource
    template_name = 'core/resource_detail.html'

class ResourceCreateView(LoginRequiredMixin, CreateView):
    model = Resource
    form_class = ResourceForm
    template_name = 'core/resource_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

@login_required
def bookmark_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    Bookmark.objects.get_or_create(user=request.user, resource=resource)
    return redirect('resource_detail', pk=pk)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            messages.success(request, f'Account created for {user.username}! You can now log in.')
            return redirect('login')
        else:
            # Show form errors to user
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserCreationForm()
    
    return render(request, 'core/register.html', {'form': form})

# API Views
class ResourceListAPI(generics.ListCreateAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ResourceCreateSerializer
        return ResourceSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class ResourceDetailAPI(generics.RetrieveAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

class CategoryListAPI(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class TagListAPI(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class BookmarkCreateAPI(generics.CreateAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@login_required
def toggle_like(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    value = request.GET.get('value') == '1'
    like, created = Like.objects.update_or_create(
        user=request.user, resource=resource,
        defaults={'value': value}
    )
    return JsonResponse({'success': True, 'liked': value})

@login_required
def bookmark_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user, 
        resource=resource
    )
    
    if not created:
        bookmark.delete()
        messages.success(request, "Bookmark removed")
    else:
        messages.success(request, "Resource bookmarked")
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))

class ResourceDetailView(DetailView):
    model = Resource
    template_name = 'core/resource_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.order_by('-created_at')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.resource = self.object
            comment.author = request.user
            comment.save()
        return redirect('resource_detail', pk=self.object.pk)

class ResourceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Resource
    form_class = ResourceForm
    template_name = 'core/resource_form.html'

    def test_func(self):
        return self.get_object().author == self.request.user

class ResourceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Resource
    template_name = 'core/resource_confirm_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        return self.get_object().author == self.request.user

class BookmarkListView(LoginRequiredMixin, ListView):
    model = Bookmark
    template_name = 'core/bookmark_list.html'
    context_object_name = 'bookmarks'

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related('resource')

def resource_share(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    sent = False

    if request.method == 'POST':
        form = EmailShareForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            resource_url = request.build_absolute_uri(resource.get_absolute_url())
            subject = f"{cd['name']} recommends you check out this resource: {resource.title}"
            message = f"Check out \"{resource.title}\" at {resource_url}\n\n" \
                      f"{cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, cd['from_email'], [cd['to_email']])
            sent = True
    else:
        form = EmailShareForm()

    return render(request, 'resources/resource_share.html', {
        'resource': resource,
        'form': form,
        'sent': sent
    })

def resource_list(request):
    resources = Resource.objects.all().annotate(
        likes_count=Count('like', filter=Q(like__value=True)),
        comments_count=Count('comments')
    )

    # Filters
    sort_by = request.GET.get('sort')
    category = request.GET.get('category')
    tag = request.GET.get('tag')
    author = request.GET.get('author')

    if category:
        resources = resources.filter(category__slug=category)
    if tag:
        resources = resources.filter(tags__slug=tag)
    if author:
        resources = resources.filter(author__username=author)

    if sort_by == 'most_liked':
        resources = resources.order_by('-likes_count')
    elif sort_by == 'most_commented':
        resources = resources.order_by('-comments_count')
    elif sort_by == 'name':
        resources = resources.order_by('title')

    categories = Category.objects.all()
    tags = Tag.objects.all()
    authors = User.objects.all()

    context = {
        'resources': resources,
        'categories': categories,
        'tags': tags,
        'authors': authors,
    }
    return render(request, 'core/resource_list.html', context)

