/**
 * Angle Range Service - API communication layer
 * Handles all HTTP requests for angle range management
 */

const API_BASE_URL = 'http://localhost:8000/api';

export interface AngleRange {
  id: string;
  name: string;
  min_angle: number;
  max_angle: number;
  enabled: boolean;
  camera_ids: string[];
  created_at: string;
  updated_at: string;
}

export interface AngleRangeCreate {
  name: string;
  min_angle: number;
  max_angle: number;
  enabled?: boolean;
  camera_ids?: string[];
}

export interface AngleRangeUpdate {
  name?: string;
  min_angle?: number;
  max_angle?: number;
  enabled?: boolean;
  camera_ids?: string[];
}

class AngleRangeService {
  /**
   * Get all angle ranges
   */
  async getAllAngleRanges(): Promise<AngleRange[]> {
    const response = await fetch(`${API_BASE_URL}/angle-ranges`);
    if (!response.ok) {
      throw new Error('Failed to fetch angle ranges');
    }
    return response.json();
  }

  /**
   * Get angle range by ID
   */
  async getAngleRange(id: string): Promise<AngleRange> {
    const response = await fetch(`${API_BASE_URL}/angle-ranges/${id}`);
    if (!response.ok) {
      throw new Error('Failed to fetch angle range');
    }
    return response.json();
  }

  /**
   * Create a new angle range
   */
  async createAngleRange(data: AngleRangeCreate): Promise<AngleRange> {
    const response = await fetch(`${API_BASE_URL}/angle-ranges`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create angle range');
    }
    
    return response.json();
  }

  /**
   * Update an existing angle range
   */
  async updateAngleRange(id: string, data: AngleRangeUpdate): Promise<AngleRange> {
    const response = await fetch(`${API_BASE_URL}/angle-ranges/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update angle range');
    }
    
    return response.json();
  }

  /**
   * Delete an angle range
   */
  async deleteAngleRange(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/angle-ranges/${id}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete angle range');
    }
  }
}

export const angleRangeService = new AngleRangeService();
