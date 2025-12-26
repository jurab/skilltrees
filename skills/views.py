import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import Node, Skill, Tree


def compute_dfs_sequence(nodes, goal_node):
    """
    Compute DFS sequence from goal node.
    - Traverse prerequisites with priorities reversed (highest priority first in DFS)
    - Reverse the final list to get learning order
    """
    node_by_id = {n.id: n for n in nodes}
    
    # Build adjacency: node_id -> list of (prereq_node_id, priority)
    prereqs_map = {}
    for node in nodes:
        prereqs = []
        for edge in node.incoming_edges.all():
            prereqs.append((edge.from_node_id, edge.priority))
        # Sort by priority ascending (lowest first = highest priority branch first)
        prereqs.sort(key=lambda x: x[1])
        prereqs_map[node.id] = [p[0] for p in prereqs]
    
    # DFS from goal
    sequence = []
    visited = set()
    
    def dfs(node_id):
        if node_id in visited:
            return
        visited.add(node_id)
        for prereq_id in prereqs_map.get(node_id, []):
            dfs(prereq_id)
        sequence.append(node_id)
    
    dfs(goal_node.id)
    
    # Post-order gives correct sequence: leaves first, goal last
    return sequence


def tree_detail(request, pk):
    tree = get_object_or_404(Tree, pk=pk)
    nodes = list(tree.nodes.select_related('skill').prefetch_related(
        'incoming_edges__from_node',
        'outgoing_edges__to_node',
    ))
    
    node_by_id = {n.id: n for n in nodes}
    node_ids = set(node_by_id.keys())

    # Find goal node
    goal_node = None
    for node in nodes:
        outgoing_ids = {e.to_node_id for e in node.outgoing_edges.all() if e.to_node_id in node_ids}
        if not outgoing_ids:
            goal_node = node
            break

    # Get user's completed/ignored skills and last node
    completed_skill_ids = set()
    ignored_skill_ids = set()
    last_node_id = None
    if request.user.is_authenticated:
        completed_skill_ids = set(request.user.completed_skills.values_list('id', flat=True))
        ignored_skill_ids = set(request.user.ignored_skills.values_list('id', flat=True))
        if request.user.last_node_id:
            last_node_id = request.user.last_node_id

    # Compute DFS sequence
    sequence = []
    if goal_node:
        sequence = compute_dfs_sequence(nodes, goal_node)

    # Find position in sequence based on last_node (the node user manually clicked)
    position = -1
    if last_node_id and last_node_id in sequence:
        position = sequence.index(last_node_id)
    else:
        # Fallback: find last completed node in sequence
        for i, node_id in enumerate(sequence):
            node = node_by_id[node_id]
            if node.skill_id in completed_skill_ids:
                position = i

    # Determine "next" node (first non-done after position)
    next_node_id = None
    for i in range(position + 1, len(sequence)):
        node_id = sequence[i]
        node = node_by_id[node_id]
        if node.skill_id not in completed_skill_ids:
            next_node_id = node_id
            break

    # Build sequence data for sidebar
    sequence_data = []
    for i, node_id in enumerate(sequence):
        node = node_by_id[node_id]
        is_done = node.skill_id in completed_skill_ids
        is_ignored = node.skill_id in ignored_skill_ids
        is_next = node_id == next_node_id
        is_skipped = not is_done and not is_ignored and i < position + 1 and not is_next
        
        sequence_data.append({
            'node_id': f'n{node_id}',
            'skill_id': node.skill_id,
            'name': node.skill.title,
            'done': is_done,
            'ignored': is_ignored,
            'next': is_next,
            'skipped': is_skipped,
        })

    # Build cytoscape elements
    elements = []

    # Add nodes
    for node in nodes:
        is_done = node.skill_id in completed_skill_ids
        is_ignored = node.skill_id in ignored_skill_ids
        is_next = node.id == next_node_id
        is_skipped = not is_done and not is_ignored and node.id in sequence[:position + 1] and not is_next
        
        elements.append({
            'data': {
                'id': f'n{node.id}',
                'name': node.skill.title,
                'skill_id': node.skill.id,
                'done': is_done,
                'ignored': is_ignored,
                'next': is_next,
                'skipped': is_skipped,
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
        'sequence_json': json.dumps(sequence_data),
    }
    return render(request, 'skills/tree_detail.html', context)


@require_POST
def toggle_skill(request, node_id):
    """Toggle a skill's completion status for the current user."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    node = get_object_or_404(Node, pk=node_id)
    skill = node.skill

    if skill in request.user.completed_skills.all():
        request.user.completed_skills.remove(skill)
        request.user.last_node = None
        done = False
    else:
        request.user.completed_skills.add(skill)
        request.user.last_node = node
        done = True
    
    request.user.save()

    return JsonResponse({'skill_id': skill.id, 'node_id': node.id, 'done': done})


@require_POST
def toggle_ignore(request, node_id):
    """Toggle a skill's ignored status for the current user."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    node = get_object_or_404(Node, pk=node_id)
    skill = node.skill

    if skill in request.user.ignored_skills.all():
        request.user.ignored_skills.remove(skill)
        ignored = False
    else:
        request.user.ignored_skills.add(skill)
        # Also remove from completed if ignoring
        request.user.completed_skills.remove(skill)
        ignored = True

    return JsonResponse({'skill_id': skill.id, 'node_id': node.id, 'ignored': ignored})
