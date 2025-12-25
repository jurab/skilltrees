import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import Node, Skill, Tree


def tree_detail(request, pk):
    tree = get_object_or_404(Tree, pk=pk)
    nodes = list(tree.nodes.select_related('skill').prefetch_related(
        'incoming_edges__from_node',
        'outgoing_edges__to_node',
    ))

    # Get user's completed skills
    completed_skill_ids = set()
    if request.user.is_authenticated:
        completed_skill_ids = set(request.user.completed_skills.values_list('id', flat=True))

    # Build cytoscape elements
    elements = []

    # Add nodes
    for node in nodes:
        elements.append({
            'data': {
                'id': f'n{node.id}',
                'name': node.skill.title,
                'skill_id': node.skill.id,
                'done': node.skill.id in completed_skill_ids,
            }
        })

    # Add edges
    for node in nodes:
        for edge in node.incoming_edges.all():
            elements.append({
                'data': {
                    'source': f'n{edge.from_node_id}',
                    'target': f'n{node.id}',
                }
            })

    context = {
        'tree': tree,
        'elements_json': json.dumps(elements),
    }
    return render(request, 'skills/tree_detail.html', context)


@require_POST
def toggle_skill(request, pk):
    """Toggle a skill's completion status for the current user."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    skill = get_object_or_404(Skill, pk=pk)

    if skill in request.user.completed_skills.all():
        request.user.completed_skills.remove(skill)
        done = False
    else:
        request.user.completed_skills.add(skill)
        done = True

    return JsonResponse({'skill_id': skill.id, 'done': done})
