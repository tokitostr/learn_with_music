from django.db import models
import json
from django.contrib.auth.models import User

class Song(models.Model):
    LEVEL_CHOICES = [
        ('A1', 'Начальный (A1)'),
        ('A2', 'Элементарный (A2)'),
        ('B1', 'Средний (B1)'),
        ('B2', 'Выше среднего (B2)'),
        ('C1', 'Продвинутый (C1)'),
    ]
    
    title = models.CharField('название', max_length=200)
    artist = models.CharField('исполнитель', max_length=200)
    lyrics = models.TextField('текст песни')
    translate = models.TextField('перевод песни')
    level = models.CharField('уровень', max_length=2, choices=LEVEL_CHOICES, default='A1')
    vocabulary = models.TextField(
        'словарь песни',
        help_text='Формат JSON: {"word": "translation", "phrase": "translation"}',
        default='{}'
    )
    created_at = models.DateTimeField('дата добавления', auto_now_add=True)
    
    class Meta:
        verbose_name = 'song'
        verbose_name_plural = 'songs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.artist} - {self.title}'
    
    def get_vocabulary_dict(self):
        """Возвращает словарик в виде словаря Python"""
        try:
            return json.loads(self.vocabulary)
        except json.JSONDecodeError:
            return {}
        

class UserWord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='words')
    word = models.CharField('слово', max_length=200)
    translation = models.CharField('перевод', max_length=500)
    context = models.TextField('предложение с этим словом', blank=True)
    song_title = models.CharField('название песни', max_length=200, blank=True)
    created_at = models.DateTimeField('дата добавления', auto_now_add=True)
    
    class Meta:
        verbose_name = 'слово пользователя'
        verbose_name_plural = 'слова пользователя'
        unique_together = ['user', 'word']
    
    def __str__(self):
        return f'{self.user.username}: {self.word}'