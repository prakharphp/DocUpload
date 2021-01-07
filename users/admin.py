from django import forms
from django.contrib import admin
from django.contrib.auth import password_validation
from django.contrib.auth.models import Group
# Register your models here.
from django.contrib.admin import ModelAdmin
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from users.models import Documents, User, RoleList


class CreateUserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        # self.fields['date_of_birth'].required = True
        # self.fields['Phone'].required = True
        # self.fields['year'].max_value

    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = '__all__'

    # def clean(self):
    #     override_clean_adduser(self, forms)

    def clean_password1(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        user = User(
            username=self.cleaned_data.get("username"),
            first_name=self.cleaned_data.get("first_name"),
            email=self.cleaned_data.get("email"),
            last_name=self.cleaned_data.get("last_name")
        )
        try:
            validate_password(self.cleaned_data["password1"], user=user)
        except ValidationError as e:
            error = "\n".join(err for err in list(e))
            raise forms.ValidationError(error)
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password1

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdmin(ModelAdmin):
    form = CreateUserForm
    list_display = ('username', 'email', 'role', 'parent', 'doc_count', 'user_count', 'updated_on')

    fieldsets = (
        ('General', {'fields': ('username', 'email', 'role', 'password1', 'password2', 'parent', 'is_active',
                                'is_superuser')}),
        ('Address', {'fields': ('address1', 'address2', 'city', 'state', 'country')}),
    )

    def get_queryset(self, request):
        user_obj = User.objects.all()
        if request.user.role == RoleList.ADMIN and not request.user.is_superuser:
            user_obj = user_obj.filter(parent=request.user)
        return user_obj


class UploadDocumentAdmin(ModelAdmin):
    add_form_template = "admin/upload_doc.html"
    list_display = ('name', 'owner', 'url', 'created_on', 'updated_on')

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['users'] = User.objects.filter().exclude(role=RoleList.ADMIN)
        extra_context['help_text'] = "Upload .pdf,.jpg with max 5MB"
        extra_context['file_type'] = [{'type': 'pdf', 'size': float(5.0)},{'type': 'jpg', 'size': float(5.0)},]
        return super(UploadDocumentAdmin, self).changeform_view(request, object_id, extra_context=extra_context)


admin.site.register(User, UserAdmin)
admin.site.register(Documents, UploadDocumentAdmin)
admin.site.unregister(Group)
