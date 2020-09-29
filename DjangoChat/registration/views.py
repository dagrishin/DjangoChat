from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormMixin, FormView

from chat.models import Contact, Deal
from utilities.conver_images import img_convert
from .forms import UserRegisterForm, UserUpdateForm, SearchForm
from .models import User


class Login(SuccessMessageMixin, LoginView):
    success_message = _('Вошли в систему')


class Logout(LoginRequiredMixin, LogoutView):
    success_message = _('Вы вышли из системы')

    def get_next_page(self):
        next_page = super().get_next_page()
        if next_page:
            messages.success(self.request, self.success_message)
        return next_page


class AccountCreate(SuccessMessageMixin, CreateView):

    model = User
    form_class = UserRegisterForm
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('auth:login')
    success_message = 'Вы успешно зарегестрировались'

class AccountUpdate(SuccessMessageMixin, LoginRequiredMixin, FormView):
    model = User
    form_class = UserUpdateForm
    template_name = 'registration/update_profile.html'
    # success_url = reverse_lazy('auth:profile')
    success_message = 'Аккаунт обновлен'

    def form_valid(self, form):
        if self.request.user.id:
            contact = Contact.objects.filter(user=self.request.user)
            contact.first().interests.clear()

            if form.cleaned_data['avatar']:
                avatar = img_convert(form.cleaned_data['avatar'])
                contact.update(avatar=avatar)
                User.objects.filter(id=self.request.user.id).update(avatar=avatar)
            for interest in form.cleaned_data['interests']:
                contact.first().interests.add(interest)
            messages.success(self.request, _(f'Интересы сохранены'))


        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        interests = []
        contact = Contact.objects.get(user=self.request.user)
        for interest in contact.interests.all():
            interests.append(interest.id)
        kwargs['form'] = self.form_class(initial={'interests': interests, 'avatar': contact.avatar})

        kwargs['object'] = User.objects.get(id=self.kwargs['pk'])
        if self.request.user.id == self.kwargs['pk']:
            user_bids = Deal.objects.filter(partner=self.request.user, status=False)
            kwargs['user_bids'] = user_bids
            kwargs['friends'] = Contact.objects.get(user=self.request.user).friends.all()
            print('Друзья', user_bids)

        else:
            button_style = ''
            find1 = Deal.objects.filter(user_id=self.request.user.id, partner_id=self.kwargs['pk'])
            find2 = Deal.objects.filter(partner_id=self.request.user.id, user_id=self.kwargs['pk'])
            if not find1 and not find2:
                button_style = 'add'

            contact_view = False

            if find1:
                contact_view = find1.first().status
            elif find2:
                contact_view = find2.first().status
                if not contact_view:
                    button_style = 'confirm'

            kwargs['button_style'] = button_style
            kwargs['contact_view'] = contact_view



        return kwargs
    def get_success_url(self):
        return reverse('auth:profile', kwargs={'pk': self.request.user.id})


class SearchMixin(LoginRequiredMixin, ListView):
    template_name = 'registration/search_form.html'
    model = Contact
    forms_filter = [SearchForm]
    search_form = None
    model_tag = None

    def get_queryset(self):
        queryset = super().get_queryset()
        users = Contact.objects.values('user_id').distinct()
        sta = False
        for form_class in self.forms_filter:
            if self.request.method == form_class.method:
                if 'interests' in self.request.GET:
                    if not self.request.GET['interests'].isdigit() and self.request.GET['interests'] != '':
                        sta = True
                if sta:
                    self.search_form = form_class()
                else:
                    self.search_form = form_class(self.request.GET)
                if self.search_form.is_valid():
                    if 'interests' in self.request.GET:
                        if self.search_form.cleaned_data['interests']:
                            interests = self.search_form.cleaned_data['interests']
                            users = self.model_tag.objects.filter(interests__in=interests).values('user_id').distinct()
                            # print(users)

                queryset = queryset.filter(user_id__in=users)

                paginator = Paginator(queryset, 1)  # Show 1 contacts per page
                page = self.request.GET.get('page')

                queryset = paginator.get_page(page)

        return queryset

    def get_context_data(self, **kwargs):
        kwargs['form'] = self.search_form
        return super().get_context_data(**kwargs)


class SearchInterest(SearchMixin):
    model_tag = Contact


class DealUpdate(LoginRequiredMixin, View):

    model = Deal

    def post(self, request, *args, **kwargs):
        if self.request.POST.get('add'):
            self.model.objects.create(user=self.request.user, partner=get_object_or_404(User, pk=kwargs['pk']))

        if self.request.POST.get('confirm'):
            queryset = self.model.objects.filter(partner=self.request.user, user=get_object_or_404(User, pk=kwargs['pk']))
            queryset.update(status=True)
            user1 = self.request.user
            user2 = get_object_or_404(User, pk=kwargs['pk'])
            contact1 = Contact.objects.get(user=user1)
            contact2 = Contact.objects.get(user=user2)

            contact1.friends.add(user2)
            contact2.friends.add(user1)

        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

