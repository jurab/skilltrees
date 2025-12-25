from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from skills.models import Edge, Node, Skill, Tree

User = get_user_model()


SKILLS = [
    'n8n basics',
    'setup botfather',
    'botfather',
    'web basics',
    'telegram - n8n',
    'data basics',
    'db basics',
    'setup airtable',
    'read/write n8n',
    'airtable - n8n',
    'setup actors',
    'actors',
    'pull to n8n',
    'apify - n8n',
    'ai intro',
    'prompting',
    'agentic',
    'implement a tool',
    'AI - n8n',
    'leads sentinel - n8n',
]


class Command(BaseCommand):
    help = 'Seeds the database with sample n8n course data'

    def handle(self, *args, **options):
        # Get or create admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'is_staff': True,
                'is_superuser': True,
                'email': 'admin@example.com',
            }
        )
        if created:
            admin.set_password('admin')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Created admin user (password: admin)'))

        # Create skills
        skills = {}
        for title in SKILLS:
            skill, created = Skill.objects.get_or_create(
                title=title,
                defaults={
                    'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
                    'text': f'# {title}\n\nPlaceholder content for {title}.',
                    'duration': 300,
                    'creator': admin,
                }
            )
            skills[title] = skill
            if created:
                self.stdout.write(f'  Created skill: {title}')

        # Create tree
        tree, created = Tree.objects.get_or_create(
            title='Leads Sentinel with n8n',
            defaults={
                'description': 'Build a leads monitoring system using n8n, Telegram, Airtable, Apify, and AI.',
                'goal_skill': skills['leads sentinel - n8n'],
                'is_free': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created tree: Leads Sentinel with n8n'))
        else:
            # Clear existing nodes/edges for re-seeding
            tree.nodes.all().delete()
            self.stdout.write('Cleared existing nodes for re-seeding')

        # Create nodes (some skills appear multiple times)
        nodes = {}

        def make_node(key, skill_title):
            node = Node.objects.create(tree=tree, skill=skills[skill_title])
            nodes[key] = node
            return node

        # Telegram branch
        make_node('n8n_basics_1', 'n8n basics')
        make_node('setup_botfather', 'setup botfather')
        make_node('botfather', 'botfather')
        make_node('web_basics_1', 'web basics')
        make_node('telegram_n8n', 'telegram - n8n')

        # Airtable branch
        make_node('web_basics_2', 'web basics')
        make_node('data_basics_1', 'data basics')
        make_node('db_basics', 'db basics')
        make_node('setup_airtable', 'setup airtable')
        make_node('read_write_n8n', 'read/write n8n')
        make_node('airtable_n8n', 'airtable - n8n')

        # Apify branch
        make_node('web_basics_3', 'web basics')
        make_node('data_basics_2', 'data basics')
        make_node('setup_actors', 'setup actors')
        make_node('actors', 'actors')
        make_node('n8n_basics_2', 'n8n basics')
        make_node('pull_to_n8n', 'pull to n8n')
        make_node('apify_n8n', 'apify - n8n')

        # AI branch
        make_node('web_basics_4', 'web basics')
        make_node('n8n_basics_3', 'n8n basics')
        make_node('ai_intro', 'ai intro')
        make_node('prompting', 'prompting')
        make_node('agentic', 'agentic')
        make_node('implement_tool', 'implement a tool')
        make_node('ai_n8n', 'AI - n8n')

        # Goal node
        make_node('leads_sentinel', 'leads sentinel - n8n')

        self.stdout.write(f'  Created {len(nodes)} nodes')

        # Create edges
        edges_data = [
            # Telegram branch
            ('n8n_basics_1', 'setup_botfather', 0),
            ('setup_botfather', 'botfather', 0),
            ('botfather', 'telegram_n8n', 0),
            ('web_basics_1', 'telegram_n8n', 1),
            ('telegram_n8n', 'leads_sentinel', 0),

            # Airtable branch
            ('web_basics_2', 'setup_airtable', 0),
            ('data_basics_1', 'setup_airtable', 1),
            ('db_basics', 'setup_airtable', 2),
            ('setup_airtable', 'read_write_n8n', 0),
            ('read_write_n8n', 'airtable_n8n', 0),
            ('airtable_n8n', 'leads_sentinel', 1),

            # Apify branch
            ('web_basics_3', 'setup_actors', 0),
            ('data_basics_2', 'setup_actors', 1),
            ('setup_actors', 'actors', 0),
            ('n8n_basics_2', 'pull_to_n8n', 0),
            ('actors', 'pull_to_n8n', 1),
            ('pull_to_n8n', 'apify_n8n', 0),
            ('apify_n8n', 'leads_sentinel', 2),

            # AI branch
            ('web_basics_4', 'n8n_basics_3', 0),
            ('n8n_basics_3', 'implement_tool', 0),
            ('ai_intro', 'prompting', 0),
            ('prompting', 'agentic', 0),
            ('agentic', 'implement_tool', 1),
            ('implement_tool', 'ai_n8n', 0),
            ('ai_n8n', 'leads_sentinel', 3),
        ]

        edge_count = 0
        for from_key, to_key, priority in edges_data:
            Edge.objects.create(
                from_node=nodes[from_key],
                to_node=nodes[to_key],
                priority=priority,
            )
            edge_count += 1

        self.stdout.write(f'  Created {edge_count} edges')
        self.stdout.write(self.style.SUCCESS('Sample data seeded successfully!'))
