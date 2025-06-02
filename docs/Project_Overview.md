# Orientor Project Overview

## Description
Orientor is a comprehensive career guidance platform that leverages advanced machine learning models, graph-based algorithms, and natural language processing to provide personalized career recommendations and skill development paths. The platform integrates multiple psychological models (e.g., Holland Code, Competence Tree) with real-world job market data to offer users actionable insights into their career growth.

## Key Features
- **Skill Tree Visualization**: Interactive visualization of skill dependencies and career paths using graph-based models.
- **Peer Matching**: Algorithm-driven recommendations for peer connections based on shared skills and career goals.
- **LLM-based Career Recommendations**: AI-generated career path suggestions using large language models.
- **Competence Tree Analysis**: Detailed assessment of user skills and potential career growth opportunities.
- **Job Recommendations**: Personalized job suggestions based on skill profiles and career aspirations.

## Architecture Overview
The Orientor platform is built on a microservices architecture, with the following core components:

### Backend Services
- **Competence Tree Service**: Manages skill tree generation and analysis.
- **LLM Service**: Handles AI-driven career recommendations.
- **Peer Matching Service**: Implements algorithms for peer connection recommendations.
- **Job Recommendation Service**: Provides personalized job suggestions.

### Data Pipelines
- **ESCO Data Integration**: Integration with the European Skills, Competences, and Occupations (ESCO) framework.
- **LLM Model Training**: Continuous training of language models for career recommendations.
- **Skill Embedding**: Generation of vector embeddings for skills and job descriptions.

### Frontend
- **React Components**: Interactive UI components for skill tree visualization, Holland Code assessment, and job recommendations.
- **Graph Visualization**: Custom components for displaying skill dependencies and career paths.
- **User Profile Management**: Dashboard for managing user skills, career goals, and peer connections.

### Machine Learning Models
- **Graph Neural Networks (GNN)**: For skill tree analysis and peer matching.
- **Large Language Models (LLM)**: For career recommendations and natural language processing.
- **Siamese Networks**: For skill similarity calculations in peer matching.

## Data Flow
1. **User Input**: Users input their skills, career goals, and preferences through the frontend UI.
2. **Skill Analysis**: The Competence Tree Service analyzes skills and generates a personalized skill tree.
3. **LLM Recommendations**: The LLM Service generates career path suggestions based on skill profiles.
4. **Peer Matching**: The Peer Matching Service recommends peers with similar skills and career goals.
5. **Job Recommendations**: The Job Recommendation Service provides personalized job suggestions.

## Technology Stack
- **Backend**: Python, FastAPI, PyTorch, GNN
- **Frontend**: React, TypeScript, Next.js
- **Data Storage**: PostgreSQL, Redis, Pinecone
- **Machine Learning**: Hugging Face Transformers, GNN frameworks, Siamese Networks
- **DevOps**: Docker, Vercel, AWS

This architecture ensures scalable, efficient, and personalized career guidance for users.