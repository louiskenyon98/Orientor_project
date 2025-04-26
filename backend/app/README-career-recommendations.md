# Career Recommendations Implementation

This document outlines the implementation of the career recommendations feature in the Orientor project.

## Overview

The career recommendations feature automatically suggests jobs to users based on their profile embeddings without requiring a search query. Users can swipe left (skip) or swipe right (save) on the suggested careers, and saved careers are added to "My Space" just like when the user manually searches via vector search.

## Implementation Details

### Database Changes

- Added an `embedding` column of type `VECTOR(384)` to the `user_profiles` table to store user embeddings
- Created a new `user_recommendations` table to track which recommendations were shown to users and whether they were swiped left or right
- Added appropriate indexes for performance optimization

### Model Integration

- Integrated fine-tuned SentenceTransformer model into the backend
- Moved preprocessing models (PCA, scaler, OHE) into the backend
- Updated the embeddings.py file to use these models for generating user embeddings

### New Endpoints

- `GET /recommendations`: Returns job recommendations based on the user's profile embedding
- `POST /recommendations/swipe`: Records a swipe action (left/right) on a recommendation

## Setup Instructions

### Database Migration

Run the following command to add the required database columns and tables:

```bash
cd backend/app
python -m migrations.run_migrations --file add_embedding_column.sql
```

### Copy Models

Run the following command to copy the fine-tuned models to the backend:

```bash
cd backend/app/scripts
python copy_models.py
```

### Generate Embeddings

After setting up the database and copying the models, you need to generate embeddings for existing user profiles:

```bash
cd backend
python -c "from app.utils.embeddings import generate_and_store_embeddings; from app.utils.database import SessionLocal; db = SessionLocal(); generate_and_store_embeddings(db); db.close()"
```

## Testing

You can test the recommendations API with the following curl commands:

```bash
# Get recommendations
curl -X GET "http://localhost:8000/recommendations" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Record a swipe action
curl -X POST "http://localhost:8000/recommendations/swipe" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "oasis_code": "123456",
    "label": "Software Developer",
    "swiped_right": true,
    "lead_statement": "Software developers design and build computer programs...",
    "main_duties": "Writing code, testing applications..."
  }'
```

## Frontend Integration

The frontend needs to be updated to:

1. Add a new "Recommendations" tab in the navigation
2. Create a swipeable card interface for job recommendations
3. Implement left/right swipe actions
4. Connect swipe actions to the API endpoints

## Technical Notes

- User embeddings are 384-dimensional vectors created by processing both structured profile data (through PCA) and textual data
- The recommendation system queries the Pinecone "oasis-minilm-index" to find the most similar job embeddings
- The system tracks previously shown recommendations to avoid showing the same recommendation multiple times 