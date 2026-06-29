# Tech Stack Patterns

This reference file contains patterns for different tech stacks to help generate appropriate directory structures.

## JavaScript/TypeScript

### React + TypeScript
```
project/
├── src/
│   ├── components/
│   ├── hooks/
│   ├── services/
│   ├── types/
│   ├── utils/
│   ├── App.tsx
│   └── index.tsx
├── public/
├── tests/
├── .env.example
├── .gitignore
├── package.json
├── tsconfig.json
├── README.md
└── LICENSE
```

### Next.js
```
project/
├── pages/
│   ├── api/
│   ├── _app.tsx
│   └── index.tsx
├── components/
├── lib/
├── styles/
├── public/
├── tests/
├── .env.example
├── .gitignore
├── next.config.js
├── package.json
├── tsconfig.json
├── README.md
└── LICENSE
```

### Vue.js + TypeScript
```
project/
├── src/
│   ├── components/
│   ├── views/
│   ├── router/
│   ├── store/
│   ├── services/
│   ├── types/
│   ├── App.vue
│   └── main.ts
├── public/
├── tests/
├── .env.example
├── .gitignore
├── package.json
├── tsconfig.json
├── vue.config.js
├── README.md
└── LICENSE
```

## Python

### Django
```
project/
├── app/
│   ├── migrations/
│   ├── templates/
│   ├── static/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── config/
│   ├── settings/
│   └── urls.py
├── tests/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

### Flask
```
project/
├── app/
│   ├── templates/
│   ├── static/
│   ├── __init__.py
│   └── routes.py
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

### FastAPI
```
project/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── __init__.py
│   └── main.py
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

## Go

### Standard Go Project
```
project/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── handler/
│   ├── service/
│   ├── repository/
│   └── model/
├── pkg/
├── api/
├── configs/
├── tests/
├── go.mod
├── go.sum
├── .gitignore
├── README.md
└── LICENSE
```

## Rust

### Standard Rust Project
```
project/
├── src/
│   ├── bin/
│   ├── lib/
│   ├── models/
│   ├── handlers/
│   ├── services/
│   └── main.rs
├── tests/
├── benches/
├── Cargo.toml
├── Cargo.lock
├── .gitignore
├── README.md
└── LICENSE
```

## Java

### Spring Boot
```
project/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/
│   │   │       ├── controller/
│   │   │       ├── service/
│   │   │       ├── repository/
│   │   │       ├── model/
│   │   │       └── Application.java
│   │   └── resources/
│   │       ├── application.properties
│   │       └── templates/
│   └── test/
├── pom.xml
├── .gitignore
├── README.md
└── LICENSE
```

## C# / .NET

### ASP.NET Core
```
project/
├── src/
│   ├── Controllers/
│   ├── Models/
│   ├── Services/
│   ├── Data/
│   ├── Program.cs
│   └── Startup.cs
├── tests/
├── project.csproj
├── .gitignore
├── README.md
└── LICENSE
```

## Mobile

### React Native
```
project/
├── src/
│   ├── components/
│   ├── screens/
│   ├── navigation/
│   ├── services/
│   ├── utils/
│   └── App.tsx
├── android/
├── ios/
├── tests/
├── .env.example
├── .gitignore
├── package.json
├── tsconfig.json
├── README.md
└── LICENSE
```

### Flutter
```
project/
├── lib/
│   ├── screens/
│   ├── widgets/
│   ├── models/
│   ├── services/
│   └── main.dart
├── test/
├── android/
├── ios/
├── pubspec.yaml
├── .gitignore
├── README.md
└── LICENSE
```

## Full-Stack

### MERN Stack (MongoDB, Express, React, Node.js)
```
project/
├── client/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.tsx
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
├── server/
│   ├── routes/
│   ├── controllers/
│   ├── models/
│   ├── middleware/
│   ├── config/
│   ├── server.js
│   └── package.json
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

## Common Files by Purpose

### Configuration Files
- `.gitignore` - Git ignore patterns
- `.env.example` - Environment variable template
- `.editorconfig` - Editor configuration
- `.prettierrc` - Code formatting
- `.eslintrc` - Linting rules
- `tsconfig.json` - TypeScript configuration

### Documentation
- `README.md` - Project overview
- `CONTRIBUTING.md` - Contribution guidelines
- `CHANGELOG.md` - Version history
- `LICENSE` - Legal license

### CI/CD
- `.github/workflows/` - GitHub Actions
- `.gitlab-ci.yml` - GitLab CI
- `Jenkinsfile` - Jenkins pipeline
- `.circleci/config.yml` - CircleCI

### Docker
- `Dockerfile` - Docker build instructions
- `docker-compose.yml` - Multi-container setup
- `.dockerignore` - Docker ignore patterns

### Testing
- `tests/` - Test directory
- `__tests__/` - Jest test directory
- `coverage/` - Test coverage reports
- `jest.config.js` - Jest configuration
- `pytest.ini` - Pytest configuration

### Build Tools
- `Makefile` - Build automation
- `Taskfile.yml` - Task runner
- `webpack.config.js` - Webpack configuration
- `vite.config.ts` - Vite configuration

## Detection Keywords

### Language Detection
- JavaScript: `javascript`, `js`, `node`, `npm`, `yarn`, `react`, `vue`, `angular`
- TypeScript: `typescript`, `ts`, `tsx`
- Python: `python`, `py`, `django`, `flask`, `fastapi`, `pip`
- Go: `golang`, `go`, `go.mod`
- Rust: `rust`, `cargo`, `rustc`
- Java: `java`, `spring`, `maven`, `gradle`
- C#: `csharp`, `.net`, `dotnet`, `blazor`

### Framework Detection
- React: `react`, `jsx`, `tsx`, `next.js`, `nextjs`
- Vue: `vue`, `nuxt`, `nuxtjs`
- Angular: `angular`, `ng`
- Django: `django`, `python`
- Flask: `flask`, `python`
- FastAPI: `fastapi`, `python`
- Express: `express`, `node.js`
- Spring: `spring`, `java`
- .NET: `dotnet`, `csharp`, `blazor`

### Architecture Detection
- Microservices: `microservice`, `service`, `api-gateway`
- Monorepo: `monorepo`, `workspace`, `lerna`, `turborepo`
- MVC: `mvc`, `model-view-controller`
- Clean Architecture: `clean`, `domain-driven`, `ddd`
- Serverless: `serverless`, `lambda`, `aws`, `cloud-function`