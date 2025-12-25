from django.shortcuts import get_object_or_404, render

from .models import Tree


def tree_detail(request, pk):
    tree = get_object_or_404(Tree, pk=pk)
    nodes = list(tree.nodes.select_related('skill').prefetch_related(
        'incoming_edges__from_node',
        'outgoing_edges__to_node',
    ))

    # Build cytoscape elements
    elements = []

    # Add nodes
    for node in nodes:
        elements.append({
            'data': {
                'id': f'n{node.id}',
                'name': node.skill.title,
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
        'elements_json': elements,
    }
    return render(request, 'skills/tree_detail.html', context)
