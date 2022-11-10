from django.contrib.auth.models import User, Group
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, TemplateView
from .models import *
from .forms import *
from .filters import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail


class PostList(ListView):
    model = Post
    template_name = 'index.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-created')
    paginate_by = 3


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    def post(self, request, *args, **kwargs):
        if request.POST['reply']:
            Reply.objects.create(post_id=self.kwargs.get('pk'), user=self.request.user, text=request.POST['reply'],
                                 accept=False)
            id = Post.objects.get(pk=self.kwargs.get('pk'))
            reply = request.POST['reply']
            email = User.objects.get(pk=id.author_id)
            post = Post.objects.get(pk=self.kwargs.get('pk'))
            send_mail(
                subject=f'Отклики на объявление!',
                message=f'На ваше объявление: {post}\n{self.request.user} оставил(а) отклик: {reply}',
                from_email='snewsportal@yandex.ru',
                recipient_list=[email.email],
            )
        return redirect(request.path)


class AddList(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'add.html'
    form_class = PostForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            author = form.save(commit=False)
            author.author = self.request.user
            author.save()
        return redirect('/')


class PersonalPage(LoginRequiredMixin, ListView):
    model = Reply
    template_name = 'personalpage.html'
    context_object_name = 'personalpage'

    def get_context_data(self, **kwargs):
        queryset = Reply.objects.filter(post__author_id=self.request.user.pk).order_by('-created')
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset, request=self.request.user.pk)
        return context


class AcceptReplyView(LoginRequiredMixin, TemplateView):
    template_name = 'accept.html'

    def get_context_data(self, **kwargs):
        id = self.kwargs.get('pk')
        reply = Reply.objects.get(pk=id)
        email = User.objects.get(id=reply.user_id)
        send_mail(
            subject=f'Ваш отклик принят!',
            message=f'Ваш отклик: {reply.text} {self.request.user} принял(а)!',
            from_email='snewsportal@yandex.ru',
            recipient_list=[email.email],
        )
        Reply.objects.filter(pk=id).update(accept=True)


class ReplyDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'delete.html'
    queryset = Reply.objects.all()
    context_object_name = 'reply'
    success_url = '/personalpage/'


class PostUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'edit.html'
    form_class = PostForm
    success_url = '/'

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'personaloffice.html'
    form_class = UserForm
    context_object_name = 'password'
    success_url = '/'

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return User.objects.get(pk=id)


class SetPassword(LoginRequiredMixin, ListView):
    model = User
    template_name = 'set_password.html'

    def post(self, request, *args, **kwargs):
        if request.POST['password']:
            u = User.objects.get(username=self.request.user)
            u.set_password(request.POST['password'])
            u.save()
        else:
            return redirect('/set_password/' + str(self.request.user))
        return redirect('/')


class AddSubscribers(LoginRequiredMixin, TemplateView):
    model = Post
    template_name = 'subscribers.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        premium_group = Group.objects.get(name='subscribe')
        if not self.request.user.groups.filter(name='subscribe').exists():
            premium_group.user_set.add(user)
        else:
            premium_group.user_set.remove(user)

