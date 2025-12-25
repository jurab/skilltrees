from django.contrib import admin

from .models import Edge, File, Node, Pause, Skill, SkillProgress, Tree


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'uploaded_at']
    list_filter = ['category']
    search_fields = ['title', 'description']


class PauseInline(admin.TabularInline):
    model = Pause
    extra = 1


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['title', 'duration', 'creator', 'created_at']
    list_filter = ['creator', 'created_at']
    search_fields = ['title', 'text']
    filter_horizontal = ['resources']
    inlines = [PauseInline]


@admin.register(Pause)
class PauseAdmin(admin.ModelAdmin):
    list_display = ['skill', 'time', 'title', 'attachment']
    list_filter = ['skill']
    search_fields = ['title']


class NodeInline(admin.TabularInline):
    model = Node
    extra = 1


class EdgeInline(admin.TabularInline):
    model = Edge
    fk_name = 'from_node'
    extra = 1


@admin.register(Tree)
class TreeAdmin(admin.ModelAdmin):
    list_display = ['title', 'goal_skill', 'is_free', 'created_at']
    list_filter = ['is_free', 'created_at']
    search_fields = ['title', 'description']
    inlines = [NodeInline]


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ['tree', 'skill']
    list_filter = ['tree']
    search_fields = ['skill__title']
    inlines = [EdgeInline]


@admin.register(Edge)
class EdgeAdmin(admin.ModelAdmin):
    list_display = ['from_node', 'to_node', 'optional', 'priority']
    list_filter = ['optional', 'from_node__tree']


@admin.register(SkillProgress)
class SkillProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill', 'status', 'video_position', 'started_at', 'completed_at']
    list_filter = ['status', 'skill']
    search_fields = ['user__username', 'skill__title']
