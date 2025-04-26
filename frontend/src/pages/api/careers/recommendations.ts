import type { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://localhost:8000';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const { limit = 10 } = req.query;
    const response = await axios.get(`${BACKEND_API_URL}/careers/recommendations`, {
      params: { limit },
      headers: {
        Authorization: req.headers.authorization,
      },
    });
    res.status(200).json(response.data);
  } catch (error: any) {
    console.error('Error proxying career recommendations:', error);
    res.status(error.response?.status || 500).json({
      message: error.response?.data?.message || 'Internal server error',
    });
  }
} 