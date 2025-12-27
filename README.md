# Skill Trees

A visual learning platform with interactive skill trees, progress tracking, and engaging course previews.

**Live:** [comamkurvadelat.cz](https://comamkurvadelat.cz)

## Features

### Interactive Skill Tree Visualization
- DAG-based skill trees rendered with Cytoscape.js
- Visual progress tracking (completed, skipped, ignored states)
- DFS-computed learning sequences
- Click to view skill details, double-click to mark complete

### Smart Progress Tracking
- localStorage persistence for anonymous users (no login required for free courses)
- Server-side persistence for authenticated users
- Automatic "next skill" detection based on prerequisites

### Engaging Course Previews
- **Strudel.cc Integration:** Live-coding music previews with interactive sliders and visualizations
- **AI Dashboard Animation:** Simulated lead qualification with live counters, confidence bars, and Telegram notifications

### Video Learning with Pause Points
- YouTube integration with timed pause points
- Clipboard actions (copy code snippets)
- File attachments at specific timestamps
- "Continue" prompts for reflection moments

### Theming
- 5 built-in themes: Claude (default), Matrix, Ocean, Amber, Flashbang
- Theme preference persisted in localStorage
- Consistent theming across all views

## Tech Stack

- **Backend:** Django 5.x
- **Frontend:** Vanilla JS, Cytoscape.js, CSS custom properties
- **Database:** SQLite (dev), PostgreSQL (prod)
- **Deployment:** Railway

## Project Structure

```
skilltrees/
├── skills/                    # Main app
│   ├── models.py              # Tree, Skill, Node, Edge, Pause, etc.
│   ├── views.py               # Homepage, tree detail, toggle endpoints
│   ├── templates/skills/
│   │   ├── homepage.html      # Carousel with course previews
│   │   └── tree_detail.html   # Interactive skill tree view
│   └── fixtures/
│       └── initial_data.json  # Sample course data
├── users/                     # Custom user model with progress tracking
└── skilltrees/                # Django project settings
```

## Data Model

```
Tree
 └── Node (position in tree)
      └── Skill (reusable across trees)
           └── Pause (timed video interactions)

Edge (Node → Node with priority for DFS ordering)
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Load sample data
python manage.py loaddata skills/fixtures/initial_data.json

# Start server
python manage.py runserver
```

## Sample Courses

1. **Leads Sentinel with n8n** - Build an AI-powered LinkedIn lead qualification system
2. **Strudel.cc Basics** - Learn live-coding music in your browser

## Screenshots

*Homepage carousel with live Strudel preview and AI dashboard animation*

## License

MIT
