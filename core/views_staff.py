# Temporarily disabled due to missing models SpecialistProfile and Specialization

from django.shortcuts import render

# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.views.generic import ListView, CreateView, UpdateView, DeleteView
# from django.shortcuts import redirect, get_object_or_404
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.db import transaction
# from django.urls import reverse_lazy
# from django.contrib.messages.views import SuccessMessageMixin

# from .models import SpecialistProfile, Specialization, User
# from .forms_staff import SpecialistUserForm, SpecialistProfileForm, SpecializationForm


# # --- Specialist Management (Staff) --- #

# class SpecialistListView(LoginRequiredMixin, ListView):
#     """
#     Отображает список всех специалистов с пагинацией.
#     """
#     model = SpecialistProfile
#     template_name = 'core/staff/specialist_list.html'
#     context_object_name = 'specialist_profiles'
#     paginate_by = 15

#     def get_queryset(self):
#         """
#         Оптимизируем запрос, чтобы избежать N+1 проблем,
#         предварительно загружая связанные данные пользователей и специализаций.
#         """
#         return SpecialistProfile.objects.select_related('user').prefetch_related('specializations').order_by('user__last_name', 'user__first_name')


# @login_required
# @transaction.atomic
# def specialist_create(request):
#     """
#     Создание нового специалиста (User + SpecialistProfile).
#     """
#     if request.method == 'POST':
#         user_form = SpecialistUserForm(request.POST)
#         profile_form = SpecialistProfileForm(request.POST)
#         if user_form.is_valid() and profile_form.is_valid():
#             user = user_form.save(commit=False)
#             password = User.objects.make_random_password()
#             user.set_password(password)
#             user.save()

#             profile = profile_form.save(commit=False)
#             profile.user = user
#             profile.save()
#             profile_form.save_m2m()

#             messages.success(request, f'Специалист "{user.get_full_name()}" успешно создан. Временный пароль: {password}')
#             return redirect('core:staff_specialist_list')
#     else:
#         user_form = SpecialistUserForm()
#         profile_form = SpecialistProfileForm()

#     context = {
#         'user_form': user_form,
#         'profile_form': profile_form,
#         'page_title': 'Добавить специалиста'
#     }
#     return render(request, 'core/staff/specialist_form.html', context)


# @login_required
# @transaction.atomic
# def specialist_update(request, pk):
#     """
#     Редактирование данных специалиста.
#     """
#     specialist_profile = get_object_or_404(SpecialistProfile, pk=pk)
#     user = specialist_profile.user

#     if request.method == 'POST':
#         user_form = SpecialistUserForm(request.POST, instance=user)
#         profile_form = SpecialistProfileForm(request.POST, instance=specialist_profile)
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             messages.success(request, f'Данные специалиста "{user.get_full_name()}" успешно обновлены.')
#             return redirect('core:staff_specialist_list')
#     else:
#         user_form = SpecialistUserForm(instance=user)
#         profile_form = SpecialistProfileForm(instance=specialist_profile)

#     context = {
#         'user_form': user_form,
#         'profile_form': profile_form,
#         'page_title': 'Редактировать специалиста'
#     }
#     return render(request, 'core/staff/specialist_form.html', context)


# @login_required
# def specialist_delete(request, pk):
#     """
#     Удаление специалиста.
#     """
#     specialist_profile = get_object_or_404(SpecialistProfile, pk=pk)
#     if request.method == 'POST':
#         full_name = specialist_profile.user.get_full_name()
#         specialist_profile.user.delete()
#         messages.success(request, f'Специалист "{full_name}" был успешно удален.')
#         return redirect('core:staff_specialist_list')

#     context = {
#         'specialist': specialist_profile
#     }
#     return render(request, 'core/staff/specialist_confirm_delete.html', context)


# # --- Specialization Management --- #

# class SpecializationListView(LoginRequiredMixin, ListView):
#     model = Specialization
#     template_name = 'core/staff/specialization_list.html'
#     context_object_name = 'specializations'
#     paginate_by = 20
#     ordering = ['name']

# class SpecializationCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
#     model = Specialization
#     form_class = SpecializationForm
#     template_name = 'core/staff/specialization_form.html'
#     success_url = reverse_lazy('core:staff_specialization_list')
#     success_message = "Специализация \"%(name)s\" была успешно создана."

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['page_title'] = 'Создать специализацию'
#         return context

# class SpecializationUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
#     model = Specialization
#     form_class = SpecializationForm
#     template_name = 'core/staff/specialization_form.html'
#     success_url = reverse_lazy('core:staff_specialization_list')
#     success_message = "Специализация \"%(name)s\" была успешно обновлена."

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['page_title'] = 'Редактировать специализацию'
#         return context

# class SpecializationDeleteView(LoginRequiredMixin, DeleteView):
#     model = Specialization
#     template_name = 'core/staff/specialization_confirm_delete.html'
#     success_url = reverse_lazy('core:staff_specialization_list')

#     def delete(self, request, *args, **kwargs):
#         obj = self.get_object()
#         messages.success(self.request, f'Специализация "{obj.name}" была успешно удалена.')
#         return super(SpecializationDeleteView, self).delete(request, *args, **kwargs)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['page_title'] = 'Удалить специализацию'
#         return context

# Placeholder functions for URL routing
def specialist_list(request):
    return render(request, 'core/staff/specialist_list.html', {'message': 'Staff management temporarily disabled'})

def specialist_create(request):
    return render(request, 'core/staff/specialist_form.html', {'message': 'Staff management temporarily disabled'})

def specialist_update(request, pk):
    return render(request, 'core/staff/specialist_form.html', {'message': 'Staff management temporarily disabled'})

def specialist_delete(request, pk):
    return render(request, 'core/staff/specialist_confirm_delete.html', {'message': 'Staff management temporarily disabled'})
