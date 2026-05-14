from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm
from .models import Song, UserWord
from django.http import JsonResponse
import io
import csv
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
import random


def home(request):
    return render(request, 'music/home.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
        else:
            messages.error(request, 'Исправьте ошибки в форме')
    else:
        form = RegisterForm()
    return render(request, 'music/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    return render(request, 'music/login.html')

def user_logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('login')


def song_list(request):
    songs = Song.objects.all()
    
    level_choices = dict(Song.LEVEL_CHOICES)
    songs_by_level = []
    
    for level_code, level_name in Song.LEVEL_CHOICES:
        level_songs = songs.filter(level=level_code)
        if level_songs.exists():
            songs_by_level.append(((level_code, level_name), level_songs))
    
    return render(request, 'music/song_list.html', {'songs_by_level': songs_by_level})

def study_song(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    vocab = song.get_vocabulary_dict()
    return render(request, 'music/study_song.html', {'song': song, 'vocab': vocab})



@login_required
def add_to_vocabulary(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        word = data.get('word', '').strip()
        translation = data.get('translation', '').strip()
        context = data.get('context', '').strip()
        song_title = data.get('song_title', '').strip()
        
        if word and translation:
            existing = UserWord.objects.filter(user=request.user, word=word).first()
            
            if existing:
                if existing.context == context:
                    return JsonResponse({'status': 'exists', 'already_exists': True})
                else:
                    return JsonResponse({
                        'status': 'exists', 
                        'existing_context': existing.context,
                        'word': word
                    })
            else:
                UserWord.objects.create(
                    user=request.user,
                    word=word,
                    translation=translation,
                    context=context,
                    song_title=song_title
                )
                return JsonResponse({'status': 'ok', 'created': True})
        return JsonResponse({'status': 'error'}, status=400)
    return JsonResponse({'status': 'error'}, status=405)

@login_required
def vocabulary_list(request):
    words = request.user.words.all().order_by('-created_at')
    return render(request, 'music/vocabulary.html', {'words': words})

@login_required
def delete_word(request, word_id):
    if request.method == 'POST':
        word = UserWord.objects.get(id=word_id, user=request.user)
        word.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def clear_vocabulary(request):
    if request.method == 'POST':
        request.user.words.all().delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def merge_word_context(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        word = data.get('word', '').strip()
        new_context = data.get('new_context', '').strip()
        
        try:
            word_obj = UserWord.objects.get(user=request.user, word=word)
            if new_context and new_context not in word_obj.context:
                word_obj.context = word_obj.context + '\n\n' + new_context
                word_obj.save()
            return JsonResponse({'status': 'ok'})
        except UserWord.DoesNotExist:
            return JsonResponse({'status': 'error'}, status=400)
    return JsonResponse({'status': 'error'}, status=405)


class ExportVocabularyCSVView(LoginRequiredMixin, View):
    def get(self, request):
        deck_name = request.GET.get('deck_name', f"{request.user.username}_vocabulary")
        
        output = io.StringIO()
        writer = csv.writer(
            output,
            delimiter=',',
            quotechar='"',
            quoting=csv.QUOTE_ALL,
            lineterminator='\n'
        )
        
        writer.writerow([deck_name])
        
        for word_obj in request.user.words.all():
            writer.writerow([word_obj.word or ""])
            writer.writerow([word_obj.translation or ""])
            writer.writerow([])
        
        response = HttpResponse(
            output.getvalue().encode('utf-8-sig'),
            content_type='text/csv; charset=utf-8-sig'
        )
        
        safe_filename = f"{request.user.username}_vocabulary.csv"
        response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
        
        return response
    


def train_song(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    vocab = song.get_vocabulary_dict()
    
    original_lines = [line.strip() for line in song.lyrics.split('\n') if line.strip()]
    
    translation_lines = [line.strip() for line in song.translate.split('\n') if line.strip()]
    
    correct_pairs_lines = {original_lines[i]: translation_lines[i] for i in range(len(original_lines))}
    
    shuffled_originals = original_lines.copy()
    shuffled_translations = translation_lines.copy()
    random.shuffle(shuffled_originals)
    random.shuffle(shuffled_translations)
    
    words = list(vocab.keys())
    translations = list(vocab.values())
    
    correct_pairs_words = {words[i]: translations[i] for i in range(len(words))}
    
    shuffled_words = words.copy()
    shuffled_translations_words = translations.copy()
    random.shuffle(shuffled_words)
    random.shuffle(shuffled_translations_words)
    
    return render(request, 'music/train_song.html', {
        'song': song,
        'shuffled_originals': shuffled_originals,
        'shuffled_translations': shuffled_translations,
        'correct_pairs_lines': correct_pairs_lines,
        'words': shuffled_words,
        'translations': shuffled_translations_words,
        'correct_pairs_words': correct_pairs_words,
    })

def check_match(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        user_pairs = data.get('pairs', {})
        correct_pairs = data.get('correct', {})
        
        correct_count = 0
        for key, value in user_pairs.items():
            if value == correct_pairs.get(key):
                correct_count += 1
        
        total = len(correct_pairs)
        score = int((correct_count / total) * 100) if total > 0 else 0
        
        return JsonResponse({
            'status': 'ok',
            'correct_count': correct_count,
            'total': total,
            'score': score
        })
    return JsonResponse({'status': 'error'}, status=400)