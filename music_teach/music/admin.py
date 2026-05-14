from django.contrib import admin
from .models import Song
import json

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'level', 'created_at']
    list_filter = ['level', 'created_at']
    search_fields = ['title', 'artist', 'lyrics']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'artist', 'level')
        }),
        ('Текст песни', {
            'fields': ('lyrics',),
            'description': 'Вставьте текст песни целиком'
        }),
        ('Перевод песни', {
            'fields': ('translate',),
            'description': 'Вставьте перевод песни'
        }),
        ('Словарь', {
            'fields': ('vocabulary',),
            'description': 'Формат: {"word": "перевод", "phrase": "перевод"}'
        }),
    )
    
    def save_model(self, request, obj, form, change):
        try:
            json.loads(obj.vocabulary)
        except json.JSONDecodeError:
            obj.vocabulary = '{}'
        super().save_model(request, obj, form, change)