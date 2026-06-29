---
name: program-structure-generator
description: Generate program directory/file structures from Markdown descriptions. Use when users want to create project scaffolding, directory structures, or file organization based on a description of their program. Works for any tech stack - reads Markdown files containing program descriptions, steps, architecture, and tech stack info, then proposes comprehensive directory/file structures with annotations. Always use this skill when users mention "project structure", "directory layout", "file organization", "scaffold", "generate structure", or want to plan how to organize a new project.
---

# Program Structure Generator

Generate comprehensive program directory/file structures from Markdown description files.

## Overview

This skill reads a Markdown file describing a program and generates:
1. A proposed directory/file structure as a tree
2. Annotations explaining what each directory/file is for
3. All standard project files based on the detected tech stack
4. A first-stage preview for user approval before any creation

## Workflow

### Step 1: Read and Parse Description

Read the Markdown description file. Extract:
- **Primary language(s)**: Look for language mentions, file extensions, or tech stack keywords
- **Framework(s)**: Web frameworks, libraries, tools mentioned
- **Architecture patterns**: MVC, microservices, monorepo, etc.
- **Special requirements**: Docker, CI/CD, testing frameworks, etc.
- **Project scope**: Simple script, web app, API, full-stack, etc.

If the description is vague:
- Ask clarifying questions about the tech stack
- Suggest common patterns based on what's mentioned
- Propose a reasonable default structure

### Step 2: Generate Structure

Use the extracted information to generate a comprehensive directory/file structure.

**Standard files to include (based on tech stack):**
- `.gitignore` - Language-appropriate ignore patterns
- `README.md` - Project overview with structure documentation
- `package.json` / `requirements.txt` / `Cargo.toml` / `go.mod` - Dependency manifest
- `tsconfig.json` / `tslint.json` / `.eslintrc` - Language-specific config
- `Dockerfile` / `docker-compose.yml` - If Docker mentioned
- `.github/workflows/` / `.gitlab-ci.yml` - If CI/CD mentioned
- `LICENSE` - Common license file
- `.env.example` - Environment variable template
- `Makefile` / `Taskfile.yml` - Build automation
- `tests/` / `__tests__/` - Test directory
- `docs/` - Documentation directory

**Directory structure patterns:**
- Follow conventional patterns for the detected tech stack
- Include source directories (`src/`, `app/`, `lib/`)
- Include configuration directories (`config/`, `configs/`)
- Include asset directories (`assets/`, `static/`, `public/`)
- Include documentation directories (`docs/`, `doc/`)
- Include test directories (`tests/`, `test/`, `__tests__/`)

### Step 3: Present for Approval

Show the proposed structure as a tree with annotations:

```
project-name/
├── src/                    # Source code directory
│   ├── components/         # React components
│   │   ├── Header.tsx      # Header component
│   │   └── Footer.tsx      # Footer component
│   ├── pages/              # Page components
│   ├── utils/              # Utility functions
│   └── index.tsx           # Entry point
├── public/                 # Static assets
│   ├── index.html          # HTML template
│   └── favicon.ico         # Favicon
├── tests/                  # Test files
│   ├── components/         # Component tests
│   └── utils/              # Utility tests
├── .gitignore              # Git ignore patterns
├── package.json            # Node.js dependencies
├── tsconfig.json           # TypeScript configuration
├── README.md               # Project documentation
└── LICENSE                 # MIT License
```

**IMPORTANT**: Do NOT create any files or directories yet. Only present the structure.

### Step 4: Handle Approval

After presenting the structure:
1. Ask user: "Do you approve this structure? (yes/no/modify)"
2. If yes: Proceed to Step 5
3. If modify: Ask what changes they want, regenerate, repeat
4. If no: Ask what they'd prefer, regenerate

### Step 5: Write to README.md

After approval, follow these steps to write the structure to README.md:

#### 5.1 Check for existing README.md
- Use `read` tool to check if README.md already exists at the project root
- If it exists, read its contents to preserve existing documentation
- If it doesn't exist, create a new README.md with a basic project title and description

#### 5.2 Add 'Project Structure' section
- If existing README has no "Project Structure" section, add it at the end
- If it already has a "Project Structure" section, update it with the new structure
- Use a level-2 heading: `## Project Structure`

#### 5.3 Format the structure properly
- Use a fenced code block with tree formatting for the directory structure
- Include the root directory name as the top-level entry
- Preserve the tree characters (├──, └──, │) for visual hierarchy
- Add inline comments after each entry explaining its purpose
- Group related files/directories logically

#### 5.4 Preserve existing content
- Keep all existing sections (Overview, Installation, Usage, etc.) intact
- Insert the "Project Structure" section in a logical position (typically after Overview, before Usage)
- If README already has structure documentation, replace it with the updated version

#### 5.5 Write the file
- Use the `write` tool to write the complete README.md content
- Ensure proper Markdown formatting with consistent heading levels
- Verify the file was written successfully

**Example README.md structure:**

```markdown
# Project Name

Brief description of the project.

## Installation

Instructions for installing dependencies...

## Usage

How to use the project...

## Project Structure

```
project-name/
├── src/                    # Source code directory
│   ├── components/         # React components
│   │   ├── Header.tsx      # Header component
│   │   └── Footer.tsx      # Footer component
│   ├── pages/              # Page components
│   ├── utils/              # Utility functions
│   └── index.tsx           # Entry point
├── public/                 # Static assets
│   ├── index.html          # HTML template
│   └── favicon.ico         # Favicon
├── tests/                  # Test files
│   ├── components/         # Component tests
│   └── utils/              # Utility tests
├── .gitignore              # Git ignore patterns
├── package.json            # Node.js dependencies
├── tsconfig.json           # TypeScript configuration
└── README.md               # Project documentation
```

## License

MIT License...
```

## Tech Stack Detection Rules

### Languages
- **JavaScript/TypeScript**: Look for `javascript`, `typescript`, `node`, `react`, `vue`, `angular`
- **Python**: Look for `python`, `django`, `flask`, `fastapi`, `pytest`
- **Go**: Look for `golang`, `go`, `gin`, `echo`
- **Rust**: Look for `rust`, `cargo`, `actix`, `rocket`
- **Java**: Look for `java`, `spring`, `maven`, `gradle`
- **C#**: Look for `csharp`, `.net`, `dotnet`, `blazor`

### Frameworks
- **Web**: React, Vue, Angular, Svelte, Next.js, Nuxt
- **Backend**: Express, Fastify, Django, Flask, FastAPI, Spring Boot
- **Mobile**: React Native, Flutter, SwiftUI
- **Desktop**: Electron, Tauri

### Architecture Patterns
- **Monorepo**: Multiple packages in one repository
- **Microservices**: Multiple independent services
- **MVC**: Model-View-Controller
- **Clean Architecture**: Domain-driven design
- **Serverless**: Lambda functions, cloud functions

## Example Output

### Input (description.md):
```
# Weather Dashboard App
A React + TypeScript web application that displays weather data.
Uses OpenWeatherMap API, has a dashboard with charts, and user authentication.
Docker for deployment, GitHub Actions for CI/CD.
```

### Output (proposed structure):
```
weather-dashboard/
├── src/                        # Source code
│   ├── components/             # React components
│   │   ├── Dashboard/          # Dashboard components
│   │   ├── Weather/            # Weather display components
│   │   ├── Auth/               # Authentication components
│   │   └── Charts/             # Chart components
│   ├── hooks/                  # Custom React hooks
│   ├── services/               # API services
│   ├── types/                  # TypeScript types
│   ├── utils/                  # Utility functions
│   ├── App.tsx                 # Main App component
│   └── index.tsx               # Entry point
├── public/                     # Static assets
│   ├── index.html              # HTML template
│   └── favicon.ico             # Favicon
├── tests/                      # Test files
│   ├── components/             # Component tests
│   ├── hooks/                  # Hook tests
│   └── services/               # Service tests
├── .github/                    # GitHub configuration
│   └── workflows/              # GitHub Actions
│       └── ci.yml              # CI/CD workflow
├── docker/                     # Docker configuration
│   └── Dockerfile              # Docker build file
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore patterns
├── docker-compose.yml          # Docker Compose configuration
├── package.json                # Node.js dependencies
├── tsconfig.json               # TypeScript configuration
├── README.md                   # Project documentation
└── LICENSE                     # MIT License
```

## Edge Cases

### Vague Description
- Ask: "What programming language/framework do you plan to use?"
- Suggest: "Would you like me to propose a structure for a common stack like React + Node.js?"

### Multiple Tech Stacks
- Identify the primary stack
- Ask: "I see you mentioned both React and Django. Which is the frontend and which is the backend?"
- Generate structure for both with clear separation

### Custom Requirements
- Include custom directories/files as requested
- Mark them clearly in annotations
- Ask for clarification on unusual requirements

### Non-Standard Projects
- For unique projects, suggest a flexible structure
- Include common directories that can be repurposed
- Add notes about customization options

## Quality Checks

Before presenting structure:
1. ✅ Includes all standard files for detected tech stack
2. ✅ Follows conventional patterns for the ecosystem
3. ✅ Has clear separation of concerns
4. ✅ Includes testing infrastructure
5. ✅ Has documentation structure
6. ✅ Includes configuration management
7. ✅ Has deployment configuration if mentioned
8. ✅ Uses appropriate naming conventions

## Notes

- Always present structure before creating anything
- Use clear, descriptive annotations
- Follow ecosystem conventions (e.g., `src/` for JavaScript, `app/` for Rails)
- Include both source and non-source directories
- Consider development workflow (linting, testing, building)
- Make structure scalable for future growth