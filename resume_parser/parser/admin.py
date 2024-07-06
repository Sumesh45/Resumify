from django.contrib import admin
from .models import Resume_data

# @admin.register(Resume)
# class ResumeAdmin(admin.ModelAdmin):
#     list_display = ('file', 'uploaded_at')
#     search_fields = ('file',)


admin.site.register(Resume_data)
