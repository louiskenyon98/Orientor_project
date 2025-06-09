# LLM Analysis Setup and Testing Guide

## Overview
The LLM analysis feature generates personalized job recommendation analyses for each user based on their profile, skills, and personality assessments.

## Setup Requirements

### 1. Environment Variable
You must set the OpenAI API key:
```bash
export OPENAI_API_KEY='your-openai-api-key-here'
```

Add this to your `.env` file in the backend directory:
```
OPENAI_API_KEY=your-openai-api-key-here
```

### 2. Database Migration
The migration should already be applied, but if not:
```bash
cd backend
alembic upgrade head
```

## Testing the Feature

### Option 1: Simple Test (Recommended)
This test doesn't require the API server to be running:

```bash
cd backend
python test_llm_analysis_simple.py
```

This will:
- Generate analysis for new job recommendations
- Update existing recommendations without analysis
- Show personalized analysis based on user profile

### Option 2: Comprehensive Test
This requires the FastAPI server to be running:

1. Start the server:
```bash
cd backend
python run.py
```

2. In another terminal, run:
```bash
cd backend
python test_llm_analysis_comprehensive.py
```

This will test:
- Direct service functionality
- API endpoint with auto-generation
- Manual analysis generation endpoint
- Personalization across different users

### Option 3: Quick Test
For a quick verification:

```bash
cd backend
python test_llm_analysis.py
```

## How It Works

### Automatic Generation
When a user saves a new job recommendation via the API:
1. The job is saved to the database
2. LLM analysis is automatically generated based on the user's profile
3. The analysis includes:
   - **Personal Analysis**: How well the user matches the job
   - **Entry Qualifications**: Key requirements for the role
   - **Suggested Improvements**: Actionable steps to improve fit

### Manual Generation
For existing recommendations without analysis:
- POST to `/space/recommendations/{id}/generate-analysis`
- The endpoint generates or regenerates the analysis

### Personalization Factors
The analysis considers:
- User's 13 tracked skills (creativity, leadership, etc.)
- User's cognitive traits (analytical thinking, adaptability, etc.)
- User's profile (experience, education, interests)
- User's personality assessments (HEXACO, Holland)
- Job requirements and description

## Troubleshooting

### "OPENAI_API_KEY not set"
Make sure to export the environment variable or add it to your .env file.

### "Failed to generate analysis"
1. Check your OpenAI API key is valid
2. Ensure you have API credits
3. Check the logs for specific error messages

### Analysis not showing in frontend
Verify that:
1. The backend is returning the analysis fields
2. The frontend is displaying the fields correctly
3. The recommendation has been analyzed (check database)

## API Endpoints

### Save Recommendation (with auto-analysis)
```
POST /space/recommendations
Authorization: Bearer <token>
Body: {
  "oasis_code": "1234",
  "label": "Software Developer",
  "description": "...",
  // ... other fields
}
```

### Generate/Regenerate Analysis
```
POST /space/recommendations/{id}/generate-analysis
Authorization: Bearer <token>
```

### Get Recommendations (includes analysis)
```
GET /space/recommendations
Authorization: Bearer <token>
```

## Database Check
To verify analysis in the database:
```sql
SELECT id, label, 
       CASE WHEN personal_analysis IS NOT NULL THEN 'Yes' ELSE 'No' END as has_analysis
FROM saved_recommendations
WHERE user_id = <user_id>;
```