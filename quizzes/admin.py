from django.contrib import admin
from .models import Topic, Question, Option, Quiz, QuizQuestion, Attempt, AttemptAnswer


class OptionInline(admin.TabularInline):
    model = Option
    extra = 4
    min_num = 2


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'question_count', 'quiz_count', 'created_at')
    search_fields = ('name', 'description')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'topic', 'difficulty', 'created_at')
    list_filter = ('topic', 'difficulty')
    search_fields = ('text', 'explanation')
    inlines = [OptionInline]

    def text_preview(self, obj):
        return obj.text[:60] + "..." if len(obj.text) > 60 else obj.text
    text_preview.short_description = 'Question Text'


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 3


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'time_limit', 'pass_percentage', 'is_active', 'created_by', 'created_at')
    list_filter = ('topic', 'is_active')
    search_fields = ('title', 'description')
    inlines = [QuizQuestionInline]


class AttemptAnswerInline(admin.TabularInline):
    model = AttemptAnswer
    extra = 0
    readonly_fields = ('question', 'selected_option', 'is_correct')
    can_delete = False


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'percentage', 'passed', 'completed', 'started_at', 'submitted_at')
    list_filter = ('passed', 'completed', 'quiz__topic')
    search_fields = ('user__username', 'quiz__title')
    inlines = [AttemptAnswerInline]
    readonly_fields = ('started_at', 'submitted_at', 'score', 'percentage', 'passed', 'completed')
