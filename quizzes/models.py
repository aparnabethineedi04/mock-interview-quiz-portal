from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Topic(models.Model):
    """
    Represents a subject domain for mock interviews and quizzes (e.g. Python, SQL, DBMS, Java).
    """
    name = models.CharField(max_length=100, unique=True, help_text="Name of the topic/subject (e.g., Python, SQL)")
    description = models.TextField(blank=True, help_text="Brief overview of the topic concepts")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'

    def __str__(self):
        return self.name

    @property
    def question_count(self):
        return self.questions.count()

    @property
    def quiz_count(self):
        return self.quizzes.count()


class Question(models.Model):
    """
    Represents a multiple-choice question categorized under a specific topic.
    Includes difficulty level and explanatory rationale for post-quiz review.
    """
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )

    topic = models.ForeignKey(
        Topic, 
        on_delete=models.CASCADE, 
        related_name='questions',
        help_text="Topic category this question belongs to"
    )
    text = models.TextField(help_text="The question prompt or problem statement")
    difficulty = models.CharField(
        max_length=10, 
        choices=DIFFICULTY_CHOICES, 
        default='medium',
        help_text="Question difficulty level"
    )
    explanation = models.TextField(
        blank=True, 
        help_text="Detailed explanation of why the correct answer is right"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return f"[{self.topic.name} | {self.difficulty.upper()}] {self.text[:60]}..."

    @property
    def correct_option(self):
        """Returns the correct Option object for this question."""
        return self.options.filter(is_correct=True).first()


class Option(models.Model):
    """
    Represents one of the multiple choice alternatives for a Question.
    `is_correct` specifies whether choosing this option gives credit.
    """
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name='options',
        help_text="Question this choice belongs to"
    )
    text = models.CharField(max_length=300, help_text="Answer option text")
    is_correct = models.BooleanField(default=False, help_text="Mark True if this is the correct answer")

    class Meta:
        verbose_name = 'Option'
        verbose_name_plural = 'Options'

    def __str__(self):
        status = " (Correct)" if self.is_correct else ""
        return f"{self.text}{status}"


class Quiz(models.Model):
    """
    Represents a curated mock quiz/interview test containing a subset of questions.
    Has a timer limit (minutes), passing threshold (%), and belongs to a Topic.
    """
    title = models.CharField(max_length=200, help_text="Title of the quiz (e.g., Python OOP Assessment)")
    topic = models.ForeignKey(
        Topic, 
        on_delete=models.CASCADE, 
        related_name='quizzes',
        help_text="Topic/subject covered by this quiz"
    )
    description = models.TextField(blank=True, help_text="Guidelines and topics covered in this quiz")
    time_limit = models.PositiveIntegerField(
        default=15, 
        help_text="Duration allowed in minutes (0 means untimed)"
    )
    pass_percentage = models.PositiveIntegerField(
        default=50, 
        help_text="Minimum score percentage required to pass"
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_quizzes',
        help_text="Admin who authored this quiz"
    )
    is_active = models.BooleanField(default=True, help_text="Whether students can see and attempt this quiz")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return f"{self.title} ({self.topic.name})"

    @property
    def total_questions(self):
        return self.quiz_questions.count()


class QuizQuestion(models.Model):
    """
    Junction table connecting Quiz and Question.
    Allows reusability of questions across multiple quizzes and maintains custom ordering.
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='quiz_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='quiz_instances')
    order = models.PositiveIntegerField(default=1, help_text="Display order in the quiz")

    class Meta:
        ordering = ['order', 'id']
        unique_together = ('quiz', 'question')
        verbose_name = 'Quiz Question'
        verbose_name_plural = 'Quiz Questions'

    def __str__(self):
        return f"{self.quiz.title} -> Q#{self.order}: {self.question.text[:40]}..."


class Attempt(models.Model):
    """
    Represents a student's attempt at taking a Quiz.
    Stores score, total questions, timestamp, and completion status.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='quiz_attempts',
        help_text="Student who took the quiz"
    )
    quiz = models.ForeignKey(
        Quiz, 
        on_delete=models.CASCADE, 
        related_name='attempts',
        help_text="Quiz that was attempted"
    )
    score = models.FloatField(default=0.0, help_text="Number of correctly answered questions")
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    percentage = models.FloatField(default=0.0, help_text="Calculated score percentage (0-100)")
    passed = models.BooleanField(default=False, help_text="True if percentage >= quiz pass_percentage")
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Attempt'
        verbose_name_plural = 'Attempts'

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.percentage:.1f}%)"

    def calculate_score(self):
        """
        Computes the final score, percentage, and pass/fail result based on submitted answers.
        """
        total = self.answers.count()
        correct = self.answers.filter(is_correct=True).count()
        self.total_questions = total
        self.correct_answers = correct
        self.score = float(correct)
        self.percentage = (correct / total * 100.0) if total > 0 else 0.0
        self.passed = self.percentage >= self.quiz.pass_percentage
        self.completed = True
        self.submitted_at = timezone.now()
        self.save()


class AttemptAnswer(models.Model):
    """
    Records a student's chosen option for each specific Question within an Attempt.
    """
    attempt = models.ForeignKey(
        Attempt, 
        on_delete=models.CASCADE, 
        related_name='answers',
        help_text="Parent quiz attempt session"
    )
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE,
        help_text="Question being answered"
    )
    selected_option = models.ForeignKey(
        Option, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="The choice option chosen by student (null if skipped)"
    )
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('attempt', 'question')
        verbose_name = 'Attempt Answer'
        verbose_name_plural = 'Attempt Answers'

    def __str__(self):
        chosen = self.selected_option.text if self.selected_option else "Skipped"
        return f"Attempt #{self.attempt.id} | Q: {self.question.id} -> {chosen}"

    def save(self, *args, **kwargs):
        """Automatically check correctness before saving."""
        if self.selected_option and self.selected_option.is_correct:
            self.is_correct = True
        else:
            self.is_correct = False
        super().save(*args, **kwargs)
