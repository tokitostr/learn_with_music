from django.urls import path
from . import views

urlpatterns = [
    path('', views.song_list, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('songs/', views.song_list, name='song_list'),
    path('study/<int:song_id>/', views.study_song, name='study_song'),
     path('add-to-vocabulary/', views.add_to_vocabulary, name='add_to_vocabulary'),
     path('vocabulary/', views.vocabulary_list, name='vocabulary'),
    path('delete-word/<int:word_id>/', views.delete_word, name='delete_word'),
    path('clear-vocabulary/', views.clear_vocabulary, name='clear_vocabulary'),
    path('merge-word-context/', views.merge_word_context, name='merge_word_context'),
    path('export-vocabulary-csv/', views.ExportVocabularyCSVView.as_view(), name='export_vocabulary_csv'),
    path('train/<int:song_id>/', views.train_song, name='train_song'),
    path('check-match/', views.check_match, name='check_match'),
]