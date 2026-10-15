#!/usr/bin/env python3
"""
Parse Markdown description files to extract tech stack information.
"""

import re
import json
import sys
from typing import Dict, List, Any


# Keywords for detection
LANGUAGE_KEYWORDS = {
    "javascript": ["javascript", "js", "node", "npm", "yarn", "react", "vue", "angular"],
    "typescript": ["typescript", "ts", "tsx"],
    "python": ["python", "py", "django", "flask", "fastapi", "pip"],
    "go": ["golang", "go", "go.mod"],
    "rust": ["rust", "cargo", "rustc"],
    "java": ["java", "spring", "maven", "gradle"],
    "csharp": ["csharp", ".net", "dotnet", "blazor"]
}

FRAMEWORK_KEYWORDS = {
    "react": ["react", "jsx", "tsx", "next.js", "nextjs"],
    "vue": ["vue", "nuxt", "nuxtjs"],
    "angular": ["angular", "ng"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "express": ["express", "node.js"],
    "spring": ["spring"],
    "dotnet": ["dotnet", "blazor"]
}

ARCHITECTURE_KEYWORDS = {
    "microservices": ["microservice", "service", "api-gateway"],
    "monorepo": ["monorepo", "workspace", "lerna", "turborepo"],
    "mvc": ["mvc", "model-view-controller"],
    "clean": ["clean", "domain-driven", "ddd"],
    "serverless": ["serverless", "lambda", "aws", "cloud-function"]
}

FEATURE_KEYWORDS = {
    "docker": ["docker", "dockerfile", "docker-compose", "container"],
    "ci_cd": ["ci/cd", "github actions", "gitlab ci", "jenkins", "circleci"],
    "testing": ["test", "testing", "jest", "pytest", "unittest"],
    "authentication": ["auth", "authentication", "login", "jwt", "oauth"],
    "database": ["database", "db", "sql", "nosql", "mongodb", "postgres", "mysql"],
    "api": ["api", "rest", "graphql", "grpc"],
    "frontend": ["frontend", "front-end", "ui", "user interface"],
    "backend": ["backend", "back-end", "server"],
    "mobile": ["mobile", "android", "ios", "react native", "flutter"]
}


def detect_keywords(text: str, keyword_dict: Dict[str, List[str]]) -> List[str]:
    """
    Detect keywords in text and return matched categories.
    
    Args:
        text: Text to search
        keyword_dict: Dictionary of categories to keywords
        
    Returns:
        List of matched categories
    """
    text_lower = text.lower()
    matches = []
    
    for category, keywords in keyword_dict.items():
        for keyword in keywords:
            if keyword in text_lower:
                matches.append(category)
                break
    
    return matches


def parse_description(content: str) -> Dict[str, Any]:
    """
    Parse a Markdown description file and extract tech stack information.
    
    Args:
        content: Markdown content
        
    Returns:
        Dictionary with extracted information
    """
    result = {
        "languages": [],
        "frameworks": [],
        "architectures": [],
        "features": [],
        "project_name": "",
        "description": "",
        "title": ""
    }
    
    # Extract title (first heading)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        result["title"] = title_match.group(1).strip()
        # Use title as project name (sanitize for directory name)
        project_name = re.sub(r'[^a-zA-Z0-9_-]', '-', result["title"].lower())
        project_name = re.sub(r'-+', '-', project_name).strip('-')
        result["project_name"] = project_name
    
    # Extract description (first paragraph after title)
    lines = content.split('\n')
    description_lines = []
    found_title = False
    for line in lines:
        if line.startswith('#'):
            found_title = True
            continue
        if found_title and line.strip():
            description_lines.append(line.strip())
            if len(description_lines) >= 3:  # Limit to first few lines
                break
    
    result["description"] = ' '.join(description_lines)
    
    # Detect languages
    result["languages"] = detect_keywords(content, LANGUAGE_KEYWORDS)
    
    # Detect frameworks
    result["frameworks"] = detect_keywords(content, FRAMEWORK_KEYWORDS)
    
    # Detect architectures
    result["architectures"] = detect_keywords(content, ARCHITECTURE_KEYWORDS)
    
    # Detect features
    result["features"] = detect_keywords(content, FEATURE_KEYWORDS)
    
    return result


def generate_recommendations(detected: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate recommendations based on detected tech stack.
    
    Args:
        detected: Detected tech stack information
        
    Returns:
        Recommendations for structure generation
    """
    recommendations = {
        "standard_files": [],
        "directories": [],
        "config_files": [],
        "notes": []
    }
    
    # Add standard files based on languages
    if "javascript" in detected["languages"] or "typescript" in detected["languages"]:
        recommendations["standard_files"].extend([
            "package.json",
            ".gitignore",
            "README.md",
            "LICENSE"
        ])
        if "typescript" in detected["languages"]:
            recommendations["config_files"].append("tsconfig.json")
    
    if "python" in detected["languages"]:
        recommendations["standard_files"].extend([
            "requirements.txt",
            ".gitignore",
            "README.md",
            "LICENSE"
        ])
    
    if "go" in detected["languages"]:
        recommendations["standard_files"].extend([
            "go.mod",
            ".gitignore",
            "README.md",
            "LICENSE"
        ])
    
    if "rust" in detected["languages"]:
        recommendations["standard_files"].extend([
            "Cargo.toml",
            ".gitignore",
            "README.md",
            "LICENSE"
        ])
    
    if "java" in detected["languages"]:
        recommendations["standard_files"].extend([
            "pom.xml",
            ".gitignore",
            "README.md",
            "LICENSE"
        ])
    
    if "csharp" in detected["languages"]:
        recommendations["standard_files"].extend([
            ".csproj",
            ".gitignore",
            "README.md",
            "LICENSE"
        ])
    
    # Add framework-specific files
    if "react" in detected["frameworks"]:
        recommendations["config_files"].extend([
            "vite.config.ts",
            ".eslintrc.cjs"
        ])
        recommendations["directories"].extend([
            "src/components/",
            "src/hooks/",
            "src/services/"
        ])
    
    if "vue" in detected["frameworks"]:
        recommendations["config_files"].extend([
            "vue.config.js",
            ".eslintrc.js"
        ])
        recommendations["directories"].extend([
            "src/components/",
            "src/views/",
            "src/router/"
        ])
    
    if "django" in detected["frameworks"]:
        recommendations["directories"].extend([
            "app/templates/",
            "app/static/",
            "config/settings/"
        ])
    
    if "flask" in detected["frameworks"]:
        recommendations["directories"].extend([
            "app/templates/",
            "app/static/"
        ])
    
    # Add feature-specific files
    if "docker" in detected["features"]:
        recommendations["standard_files"].extend([
            "Dockerfile",
            "docker-compose.yml",
            ".dockerignore"
        ])
    
    if "ci_cd" in detected["features"]:
        recommendations["directories"].append(".github/workflows/")
        recommendations["config_files"].append("ci.yml")
    
    if "testing" in detected["features"]:
        recommendations["directories"].append("tests/")
    
    if "authentication" in detected["features"]:
        recommendations["directories"].extend([
            "src/auth/",
            "src/middleware/"
        ])
    
    if "database" in detected["features"]:
        recommendations["directories"].extend([
            "src/models/",
            "src/repositories/",
            "migrations/"
        ])
    
    # Add common directories
    recommendations["directories"].extend([
        "src/",
        "tests/",
        "docs/"
    ])
    
    # Add environment file
    recommendations["standard_files"].append(".env.example")
    
    return recommendations


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: parse_description.py <markdown_file>")
        print("  or: cat <file> | parse_description.py -")
        sys.exit(1)
    
    if sys.argv[1] == "-":
        # Read from stdin
        content = sys.stdin.read()
    else:
        # Read from file
        with open(sys.argv[1], 'r') as f:
            content = f.read()
    
    # Parse description
    detected = parse_description(content)
    
    # Generate recommendations
    recommendations = generate_recommendations(detected)
    
    # Output results
    output = {
        "detected": detected,
        "recommendations": recommendations
    }
    
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()