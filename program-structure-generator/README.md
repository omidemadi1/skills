# Program Structure Generator Skill

A skill that generates comprehensive program directory/file structures from Markdown description files.

## Features

- **Tech Stack Detection**: Automatically detects programming languages, frameworks, and architecture patterns from Markdown descriptions
- **Comprehensive Structure**: Generates complete directory/file structures with all standard project files
- **Clear Annotations**: Each directory and file includes purpose descriptions
- **Approval Workflow**: Presents structure for user approval before any creation
- **Language-Agnostic**: Works for any tech stack (JavaScript, Python, Go, Rust, Java, C#, etc.)

## Usage

1. Create a Markdown file describing your program (see example below)
2. Use the skill to parse the description and generate a structure
3. Review the proposed structure
4. Approve to have it written to README.md

## Example Input

```markdown
# Weather Dashboard App

A React + TypeScript web application that displays weather data from OpenWeatherMap API.

## Features
- Dashboard with interactive charts
- User authentication with JWT
- Location search and favorites

## Tech Stack
- Frontend: React, TypeScript, Chart.js
- Backend: Node.js, Express
- Database: PostgreSQL
- Deployment: Docker, GitHub Actions
```

## Example Output

```
weather-dashboard/
├── src/                        # Source code
│   ├── components/             # React components
│   │   ├── Dashboard/          # Dashboard components
│   │   ├── Weather/            # Weather display components
│   │   └── Auth/               # Authentication components
│   ├── hooks/                  # Custom React hooks
│   ├── services/               # API services
│   ├── types/                  # TypeScript types
│   ├── utils/                  # Utility functions
│   ├── App.tsx                 # Main App component
│   └── index.tsx               # Entry point
├── public/                     # Static assets
├── tests/                      # Test files
├── .github/workflows/          # CI/CD configuration
├── docker/                     # Docker configuration
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore patterns
├── docker-compose.yml          # Docker Compose configuration
├── package.json                # Node.js dependencies
├── tsconfig.json               # TypeScript configuration
├── README.md                   # Project documentation
└── LICENSE                     # MIT License
```

## Scripts

### parse_description.py
Parses Markdown description files and extracts tech stack information.

**Usage:**
```bash
python3 scripts/parse_description.py <markdown_file>
# or
cat <file> | python3 scripts/parse_description.py -
```

**Output:** JSON with detected languages, frameworks, architectures, features, and recommendations.

### generate_tree.py
Generates tree structures with annotations from JSON input.

**Usage:**
```bash
python3 scripts/generate_tree.py <json_file>
# or
echo '<json>' | python3 scripts/generate_tree.py -
```

**Input JSON format:**
```json
{
  "project_name": "my-project",
  "items": [
    {"path": "src/", "annotation": "Source code directory"},
    {"path": "src/index.ts", "annotation": "Entry point"},
    {"path": "package.json", "annotation": "Node.js dependencies"}
  ]
}
```

## Tech Stack Detection

The skill detects the following:

### Languages
- JavaScript/TypeScript (Node.js, React, Vue, Angular)
- Python (Django, Flask, FastAPI)
- Go (Golang)
- Rust (Cargo)
- Java (Spring Boot)
- C# (.NET)

### Features
- Docker support
- CI/CD pipelines
- Testing frameworks
- Authentication systems
- Database integration
- API development

### Architecture Patterns
- Microservices
- Monorepo
- MVC
- Clean Architecture
- Serverless

## Edge Cases

### Vague Descriptions
The skill will ask clarifying questions about the tech stack and suggest common patterns.

### Multiple Tech Stacks
The skill identifies the primary stack and asks for clarification on frontend/backend separation.

### Custom Requirements
Custom directories and files are included with clear annotations.

## Files

- `SKILL.md` - Main skill instructions
- `references/tech-stack-patterns.md` - Tech stack detection patterns
- `scripts/parse_description.py` - Markdown parser
- `scripts/generate_tree.py` - Tree generator
- `scripts/test_skill.py` - Test script
- `evals/evals.json` - Test cases
- `evals/test-descriptions/` - Example description files