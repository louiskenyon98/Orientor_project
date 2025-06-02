# Competence Tree Service Documentation

## Overview
The Competence Tree Service is responsible for generating and analyzing skill trees based on user input and predefined skill dependencies. It leverages graph-based algorithms to create personalized skill development paths for users.

## Key Features
- **Skill Tree Generation**: Automatically generates a personalized skill tree based on user skills, career goals, and Holland Code results.
- **Skill Dependency Analysis**: Identifies prerequisite skills and recommended learning paths.
- **Skill Proficiency Assessment**: Analyzes user skill levels and suggests areas for improvement.
- **Career Path Recommendations**: Integrates with the LLM-based Career Recommendations Service to provide tailored career suggestions.

## Architecture
The service is built using Python and FastAPI, with the following components:

### Core Modules
- **SkillTreeGenerator**: Generates skill trees based on user input and predefined skill dependencies.
- **SkillDependencyAnalyzer**: Analyzes skill dependencies and recommends learning paths.
- **ProficiencyAssessor**: Assesses user skill proficiency levels.

### Data Sources
- **ESCO Database**: Integrated with the European Skills, Competences, and Occupations (ESCO) framework.
- **User Skill Profiles**: Retrieved from the user database.
- **Holland Code Results**: Integrated from the Holland Code Service.

### Data Flow
1. **Input**: User skill profiles and career goals.
2. **Processing**:
   - Skill dependencies are analyzed using graph-based algorithms.
   - Skill proficiency levels are assessed.
   - Personalized skill trees are generated.
3. **Output**: Skill trees and recommendations are sent to the frontend and LLM-based Career Recommendations Service.

## API Endpoints
### 1. Generate Skill Tree
```http
POST /api/competence-tree/generate
```
#### Request Body
```json
{
  "user_id": "string",
  "skills": ["string"],
  "career_goals": ["string"]
}
```
#### Response
```json
{
  "skill_tree": {
    "nodes": [
      {
        "id": "string",
        "skill": "string",
        "prerequisites": ["string"],
        "dependencies": ["string"]
      }
    ],
    "recommendations": ["string"]
  }
}
```

### 2. Analyze Skill Dependencies
```http
POST /api/competence-tree/analyze
```
#### Request Body
```json
{
  "skills": ["string"]
}
```
#### Response
```json
{
  "dependencies": {
    "skill": {
      "prerequisites": ["string"],
      "recommended": ["string"]
    }
  }
}
```

## Integration Points
- **Frontend**: Provides skill tree visualization and user interaction.
- **Holland Code Service**: Integrates Holland Code results into skill tree generation.
- **LLM-based Career Recommendations Service**: Provides career path suggestions based on skill trees.
- **User Database**: Stores user skill profiles and career goals.

## Technical Specifications
- **Language**: Python
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Graph Library**: NetworkX