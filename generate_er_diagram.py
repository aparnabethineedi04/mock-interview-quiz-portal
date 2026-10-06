import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

# Create figure
fig, ax = plt.subplots(figsize=(18, 12), dpi=200)
ax.set_facecolor('#0f172a')
fig.patch.set_facecolor('#0f172a')

# Table definitions: (name, x, y, width, height, color, fields)
tables = [
    # Top Row: Core Users & Subjects
    {
        "name": "auth_user (Django Core)",
        "x": 0.5, "y": 8.2, "w": 3.2, "h": 2.5, "color": "#1e3a8a",
        "fields": [
            ("id", "PK, INT, AUTO_INCREMENT", True, False),
            ("username", "VARCHAR(150), UNIQUE", False, False),
            ("email", "VARCHAR(254)", False, False),
            ("password", "VARCHAR(128)", False, False),
            ("is_staff", "BOOLEAN", False, False),
        ]
    },
    {
        "name": "accounts_profile",
        "x": 4.5, "y": 8.5, "w": 3.2, "h": 2.2, "color": "#0369a1",
        "fields": [
            ("id", "PK, BIGINT, AUTO", True, False),
            ("user_id", "FK -> auth_user.id (1:1)", False, True),
            ("role", "VARCHAR(20) [admin, student]", False, False),
            ("created_at", "DATETIME", False, False),
        ]
    },
    {
        "name": "quizzes_topic",
        "x": 8.8, "y": 8.5, "w": 3.4, "h": 2.2, "color": "#047857",
        "fields": [
            ("id", "PK, BIGINT, AUTO", True, False),
            ("name", "VARCHAR(100), UNIQUE", False, False),
            ("description", "TEXT", False, False),
            ("created_at", "DATETIME", False, False),
        ]
    },
    {
        "name": "quizzes_quiz",
        "x": 13.2, "y": 7.8, "w": 3.6, "h": 3.2, "color": "#7c2d12",
        "fields": [
            ("id", "PK, BIGINT, AUTO", True, False),
            ("topic_id", "FK -> quizzes_topic.id", False, True),
            ("created_by_id", "FK -> auth_user.id", False, True),
            ("title", "VARCHAR(200)", False, False),
            ("time_limit", "INT (Minutes)", False, False),
            ("pass_percentage", "INT (Default 50)", False, False),
            ("is_active", "BOOLEAN", False, False),
        ]
    },

    # Middle Row: Questions & Quizzes Association
    {
        "name": "quizzes_question",
        "x": 8.8, "y": 4.2, "w": 3.4, "h": 2.8, "color": "#065f46",
        "fields": [
            ("id", "PK, BIGINT, AUTO", True, False),
            ("topic_id", "FK -> quizzes_topic.id", False, True),
            ("text", "TEXT", False, False),
            ("difficulty", "VARCHAR(10) [easy, med, hard]", False, False),
            ("explanation", "TEXT", False, False),
        ]
    },
    {
        "name": "quizzes_quizquestion",
        "x": 13.2, "y": 4.2, "w": 3.6, "h": 2.2, "color": "#9a3412",
        "fields": [
            ("id", "PK, BIGINT, AUTO", True, False),
            ("quiz_id", "FK -> quizzes_quiz.id", False, True),
            ("question_id", "FK -> quizzes_question.id", False, True),
            ("order", "INT", False, False),
        ]
    },
    {
        "name": "quizzes_option",
        "x": 8.8, "y": 0.8, "w": 3.4, "h": 2.2, "color": "#115e59",
        "fields": [
            ("id", "PK, BIGINT, AUTO", True, False),
            ("question_id", "FK -> quizzes_question.id", False, True),
            ("text", "VARCHAR(300)", False, False),
            ("is_correct", "BOOLEAN", False, False),
        ]
    },

    # Bottom Row: Attempts & Answers
    {
        "name": "quizzes_attempt",
        "x": 0.5, "y": 2.8, "w": 3.5, "h": 3.8, "color": "#581c87",
        "fields": [
            ("id", "PK, BIGINT, AUTO", True, False),
            ("user_id", "FK -> auth_user.id", False, True),
            ("quiz_id", "FK -> quizzes_quiz.id", False, True),
            ("score", "FLOAT", False, False),
            ("total_questions", "INT", False, False),
            ("correct_answers", "INT", False, False),
            ("percentage", "FLOAT", False, False),
            ("passed", "BOOLEAN", False, False),
            ("started_at / submitted_at", "DATETIME", False, False),
        ]
    },
    {
        "name": "quizzes_attemptanswer",
        "x": 4.5, "y": 2.8, "w": 3.6, "h": 3.2, "color": "#4c1d95",
        "fields": [
            ("id", "PK, BIGINT, AUTO", True, False),
            ("attempt_id", "FK -> quizzes_attempt.id", False, True),
            ("question_id", "FK -> quizzes_question.id", False, True),
            ("selected_option_id", "FK -> quizzes_option.id", False, True),
            ("is_correct", "BOOLEAN", False, False),
        ]
    }
]

# Draw tables
for t in tables:
    x, y, w, h = t["x"], t["y"], t["w"], t["h"]
    
    # Outer box
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
                                  facecolor='#1e293b', edgecolor='#475569', linewidth=1.5)
    ax.add_patch(rect)
    
    # Header box
    header_h = 0.55
    h_rect = patches.FancyBboxPatch((x, y + h - header_h), w, header_h,
                                    boxstyle="round,pad=0.06,rounding_size=0.12",
                                    facecolor=t["color"], edgecolor='none')
    ax.add_patch(h_rect)
    
    # Header title
    ax.text(x + w/2, y + h - header_h/2, t["name"], color='#ffffff',
            fontsize=10.5, fontweight='bold', ha='center', va='center')
    
    # Fields
    field_y = y + h - header_h - 0.25
    for name, desc, is_pk, is_fk in t["fields"]:
        prefix = "🔑 " if is_pk else ("🔗 " if is_fk else "  • ")
        field_color = "#fde047" if is_pk else ("#67e8f9" if is_fk else "#e2e8f0")
        ax.text(x + 0.15, field_y, f"{prefix}{name}:", color=field_color, fontsize=8.5, fontweight='bold', va='center')
        ax.text(x + w - 0.15, field_y, desc, color='#94a3b8', fontsize=7.5, ha='right', va='center')
        field_y -= 0.32

# Relationships lines (start_x, start_y, end_x, end_y, label)
arrows = [
    # User to Profile (1:1)
    (3.7, 9.5, 4.5, 9.5, "1 : 1"),
    # Topic to Question (1:N)
    (10.5, 8.5, 10.5, 7.0, "1 : N"),
    # Topic to Quiz (1:N)
    (12.2, 9.5, 13.2, 9.5, "1 : N"),
    # Question to Option (1:N)
    (10.5, 4.2, 10.5, 3.0, "1 : N"),
    # Quiz to QuizQuestion (1:N)
    (15.0, 7.8, 15.0, 6.4, "1 : N"),
    # Question to QuizQuestion (1:N)
    (12.2, 5.3, 13.2, 5.3, "N : M Junction"),
    # User to Attempt (1:N)
    (2.1, 8.2, 2.1, 6.6, "1 : N"),
    # Quiz to Attempt (1:N)
    (13.2, 8.2, 4.0, 5.5, "1 : N"),
    # Attempt to AttemptAnswer (1:N)
    (4.0, 4.4, 4.5, 4.4, "1 : N"),
    # Question to AttemptAnswer (1:N)
    (8.8, 5.0, 8.1, 4.5, "1 : N"),
    # Option to AttemptAnswer (1:N)
    (8.8, 2.0, 8.1, 3.2, "1 : N"),
]

for sx, sy, ex, ey, label in arrows:
    ax.annotate(
        "", xy=(ex, ey), xytext=(sx, sy),
        arrowprops=dict(arrowstyle="->", color="#38bdf8", lw=1.6, mutation_scale=14,
                        connectionstyle="arc3,rad=0.08")
    )
    # text at midpoint
    mx, my = (sx + ex) / 2, (sy + ey) / 2
    ax.text(mx, my + 0.12, label, color="#a5f3fc", fontsize=7.5,
            bbox=dict(boxstyle="round,pad=0.2", fc="#0f172a", ec="#38bdf8", lw=0.8),
            ha='center', va='center')

# Title & Legend
ax.text(8.5, 11.4, "MOCK INTERVIEW & QUIZ PORTAL — RELATIONAL ER DIAGRAM",
        color='#ffffff', fontsize=17, fontweight='bold', ha='center', va='center')
ax.text(8.5, 11.0, "Normalized MySQL Relational Schema (3NF) with Foreign Key Constraints & Cardinalities",
        color='#94a3b8', fontsize=11, ha='center', va='center')

# Legend
legend_y = 0.25
ax.text(1.0, legend_y, "🔑 Primary Key (PK)", color="#fde047", fontsize=9, fontweight='bold')
ax.text(4.5, legend_y, "🔗 Foreign Key (FK)", color="#67e8f9", fontsize=9, fontweight='bold')
ax.text(8.0, legend_y, "• Regular Attribute", color="#e2e8f0", fontsize=9)
ax.text(12.0, legend_y, "-> Foreign Key Relationship", color="#38bdf8", fontsize=9, fontweight='bold')

ax.set_xlim(-0.2, 17.5)
ax.set_ylim(-0.2, 11.8)
ax.axis('off')

# Ensure output directory exists
os.makedirs('quiz-portal/docs', exist_ok=True)
output_path = 'quiz-portal/docs/er_diagram.png'
plt.tight_layout()
plt.savefig(output_path, dpi=250, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"ER diagram successfully created at: {output_path}")
