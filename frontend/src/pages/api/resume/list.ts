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
    const response = await axios.get(`${BACKEND_API_URL}/resume/list`, {
      headers: {
        Authorization: req.headers.authorization,
      },
    });
    res.status(200).json(response.data);
  } catch (error: any) {
    console.error('Error proxying resume list:', error);
    res.status(error.response?.status || 500).json({
      message: error.response?.data?.message || 'Internal server error',
    });
  }
} 