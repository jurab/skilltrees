from django.conf import settings
from django.db import models


class FileCategory(models.TextChoices):
    N8N_WORKFLOW = 'n8n', 'n8n Workflow'
    MAKE_WORKFLOW = 'make', 'Make Workflow'
    JSON = 'json', 'JSON'
    OTHER = 'other', 'Other'


class File(models.Model):
    """Downloadable resource file attached to skills."""

    file = models.FileField(upload_to='resources/')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=FileCategory.choices, default=FileCategory.OTHER)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Skill(models.Model):
    """A short video tutorial with text description and resources."""

    title = models.CharField(max_length=255)
    video_url = models.URLField(help_text='YouTube embed URL')
    text = models.TextField(help_text='Markdown content with inline images')
    duration = models.PositiveIntegerField(help_text='Duration in seconds')
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        limit_choices_to={'is_staff': True},
        related_name='created_skills',
    )
    resources = models.ManyToManyField(File, blank=True, related_name='skills')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Pause(models.Model):
    """Video sync point - pause at specific time to show content/download prompt."""

    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='pauses')
    time = models.PositiveIntegerField(help_text='Pause time in seconds')
    title = models.CharField(max_length=255)
    attachment = models.ForeignKey(
        File,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pause_attachments',
    )

    class Meta:
        ordering = ['time']
        unique_together = ['skill', 'time']

    def __str__(self):
        return f'{self.skill.title} @ {self.time}s: {self.title}'


class Tree(models.Model):
    """A course - a tree-like graph of skills leading to a goal."""

    title = models.CharField(max_length=255)
    description = models.TextField()
    intro_video_url = models.URLField(blank=True)
    goal_skill = models.ForeignKey(
        Skill,
        on_delete=models.PROTECT,
        related_name='goal_of_trees',
        help_text='The final skill that completes this tree',
    )
    resources_zip = models.FileField(upload_to='tree_resources/', blank=True)
    is_free = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Node(models.Model):
    """A skill instance within a tree. Same skill can appear in multiple nodes."""

    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name='nodes')
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT, related_name='nodes')
    requires = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='unlocks',
        blank=True,
        through='Edge',
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.tree.title}: {self.skill.title}'


class Edge(models.Model):
    """Dependency edge between nodes - defines prerequisite ordering."""

    from_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='outgoing_edges')
    to_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='incoming_edges')
    optional = models.BooleanField(default=False)
    priority = models.PositiveIntegerField(default=0, help_text='Lower = complete first')

    class Meta:
        unique_together = ['from_node', 'to_node']
        ordering = ['priority']

    def __str__(self):
        arrow = '-->' if not self.optional else '-?>'
        return f'{self.from_node.skill.title} {arrow} {self.to_node.skill.title}'


class SkillProgress(models.Model):
    """Tracks user progress on individual skills."""

    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', 'Not Started'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='skill_progress',
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    video_position = models.PositiveIntegerField(default=0, help_text='Position in seconds')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'skill']
        verbose_name_plural = 'Skill progress'

    def __str__(self):
        return f'{self.user.username}: {self.skill.title} ({self.status})'
