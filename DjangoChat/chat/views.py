from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormMixin, CreateView, FormView

from django.views.generic import DetailView, ListView, TemplateView

from .forms import ComposeForm, CreateRoomForm, UpdateRoomForm
from .models import Chat, User, Contact


class ChatAccessMixin(object):
    def get(self, *args, **kwargs):
        try:
            chat_id = self.kwargs.get("room_name")
            party = Chat.objects.filter(id=int(chat_id)).first()
            if not party.participants.filter(user=self.request.user):
                raise Http404
        except:
            raise Http404

        return super().get(self.request, *args, **kwargs)


class ChatAllView(LoginRequiredMixin, TemplateView):
    template_name = 'chat/chats.html'

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['chats'] = Chat.objects.filter(participants__user=self.request.user)
        return kwargs


class ChatView(LoginRequiredMixin, FormMixin, ChatAccessMixin, DetailView):
    template_name = 'chat/chat_detail.html'
    form_class = ComposeForm
    success_url = './'

    # def get_queryset(self):
    #     return Thread.objects.by_user(self.request.user)


    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)

        kwargs['chats'] = Chat.objects.filter(participants__user=self.request.user)
        kwargs['users'] = User.objects.all()
        print(User.objects.get(id=5))
        return kwargs


    def get_object(self):
        chat_id = self.kwargs.get("room_name")
        obj = Chat.objects.filter(id=int(chat_id)).first()
        if obj is None:
            raise Http404
        return obj


class CreateRoomView(LoginRequiredMixin, FormView):
    model = Chat
    template_name = 'chat/form_create.html'
    success_url = reverse_lazy('chat:all')
    form_class = CreateRoomForm
    # fields = ('title', 'participants')

    def form_valid(self, form):
        if form.cleaned_data['participants'].count() < 1:
            messages.success(self.request,
                             f'В комнате должно быть не менее двух участников и одним из них должны быть вы')
            return HttpResponseRedirect(self.request.META['HTTP_REFERER'])

        form.cleaned_data['participants'] = form.cleaned_data['participants'] | Contact.objects.filter(
            user=self.request.user)


        instance = Chat.objects.create(author_id=Contact.objects.get(user=self.request.user).id, title=form.cleaned_data['title'])

        instance.participants.set(form.cleaned_data['participants'])
        messages.success(self.request, _(f'Чат создан'))
        return super().form_valid(form)
    # def form_invalid(self, form):
    #     print(form)

    def form_invalid(self, form):
        print('EEEEEEEEEEEEEEEEEEEEEEEEEEEE', form)
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        friends = []
        contact = Contact.objects.get(user=self.request.user)
        for friend in contact.friends.all():
            friends.append(friend)
        form = self.form_class()
        form.fields["participants"].queryset = Contact.objects.filter(user__in=friends)
        kwargs['form'] = form
        return kwargs


class ChatUpdate(LoginRequiredMixin, FormView):
    model = Chat
    template_name = 'chat/form_create.html'
    success_url = reverse_lazy('chat:all')
    form_class = UpdateRoomForm

    def form_valid(self, form):
        if form.cleaned_data['participants'].count() < 1:
            messages.success(self.request,
                             f'В комнате должно быть не менее двух участников и одним из них должны быть вы')
            return HttpResponseRedirect(self.request.META['HTTP_REFERER'])
        queryset = Chat.objects.filter(id=self.kwargs['pk'])
        author = queryset.first().author
        contact = Contact.objects.filter(user=self.request.user)
        if self.request.user == author.user:
            form.cleaned_data['participants'] = form.cleaned_data['participants'] | contact
            messages.success(self.request, _(f'Учасники обновлены'))
        else:
            user = contact.first()
            if user not in form.cleaned_data['participants']:
                form.cleaned_data['participants'] = form.cleaned_data['participants'] | queryset.first().participants.all().exclude(user=self.request.user)
                messages.success(self.request, _(f'Вы покинули чат'))
            else:
                form.cleaned_data['participants'] = form.cleaned_data['participants'] | queryset.first().participants.all()
                messages.success(self.request, _(f'Учасники обновлены'))


        instance = queryset.first()

        instance.participants.set(form.cleaned_data['participants'])

        return super().form_valid(form)
    # def form_invalid(self, form):
    #     print(form)

    def form_invalid(self, form):
        print('EEEEEEEEEEEEEEEEEEEEEEEEEEEE', form)
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        friends = []
        contact = Contact.objects.get(user=self.request.user)
        for friend in contact.friends.all():
            friends.append(friend)
        contact = Contact.objects.filter(user=self.request.user)
        participants = Chat.objects.get(id=self.kwargs['pk']).participants.all()

        form = self.form_class(initial={'participants': participants})
        form.fields["participants"].queryset = participants
        kwargs['form'] = form
        return kwargs