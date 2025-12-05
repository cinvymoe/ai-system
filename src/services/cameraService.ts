/**
 * Camera Service - Frontend API Client
 * Handles communication with backend through Electron IPC
 * 需求: 8.1, 8.3
 */

/**
 * IPC Response format
 */
interface IPCResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

/**
 * Camera API interface exposed by Electron
 */
interface CameraAPI {
  getAll: () => Promise<IPCResponse>;
  getById: (cameraId: string) => Promise<IPCResponse>;
  getByDirection: (direction: string) => Promise<IPCResponse>;
  create: (cameraData: any) => Promise<IPCResponse>;
  update: (cameraId: string, updates: any) => Promise<IPCResponse>;
  delete: (cameraId: string) => Promise<IPCResponse>;
  updateStatus: (cameraId: string, status: string) => Promise<IPCResponse>;
}

/**
 * Extend Window interface to include cameraAPI
 */
declare global {
  interface Window {
    cameraAPI: CameraAPI;
  }
}

/**
 * Camera entity interface
 */
export interface Camera {
  id: string;
  name: string;
  address: string;
  username: string;
  password: string;
  channel: number;
  directions: ('forward' | 'backward' | 'left' | 'right' | 'idle')[];
  stream_type: 'main' | 'sub';
  url: string;
  enabled: boolean;
  resolution: string;
  fps: number;
  brightness: number;
  contrast: number;
  status: 'online' | 'offline';
  created_at: string;
  updated_at: string;
}

/**
 * Camera creation data interface
 */
export interface CameraCreate {
  name: string;
  address: string;
  username: string;
  password: string;
  channel?: number;
  directions?: ('forward' | 'backward' | 'left' | 'right' | 'idle')[];
  stream_type?: 'main' | 'sub';
  enabled?: boolean;
  resolution?: string;
  fps?: number;
  brightness?: number;
  contrast?: number;
  status?: 'online' | 'offline';
}

/**
 * Camera update data interface
 */
export interface CameraUpdate {
  name?: string;
  address?: string;
  username?: string;
  password?: string;
  channel?: number;
  directions?: ('forward' | 'backward' | 'left' | 'right' | 'idle')[];
  stream_type?: 'main' | 'sub';
  enabled?: boolean;
  resolution?: string;
  fps?: number;
  brightness?: number;
  contrast?: number;
  status?: 'online' | 'offline';
}

/**
 * CameraService class
 * Provides methods to interact with camera backend API
 */
export class CameraService {
  /**
   * Get all cameras from the database
   * 需求: 2.1
   * @returns Promise<Camera[]> Array of all cameras
   * @throws Error if the request fails
   */
  async getAllCameras(): Promise<Camera[]> {
    try {
      console.log('[CameraService] Calling window.cameraAPI.getAll()...');
      const result = await window.cameraAPI.getAll();
      console.log('[CameraService] IPC result:', result);
      
      if (!result.success) {
        console.error('[CameraService] IPC returned error:', result.error);
        throw new Error(result.error || 'Failed to fetch cameras');
      }
      
      console.log('[CameraService] IPC data:', result.data);
      console.log('[CameraService] Data type:', typeof result.data);
      console.log('[CameraService] Is array:', Array.isArray(result.data));
      
      return result.data as Camera[];
    } catch (error: any) {
      console.error('[CameraService] Exception:', error);
      throw new Error(`Failed to get all cameras: ${error.message}`);
    }
  }

  /**
   * Get a single camera by ID
   * 需求: 2.1
   * @param cameraId - The ID of the camera to retrieve
   * @returns Promise<Camera> The camera object
   * @throws Error if the camera is not found or request fails
   */
  async getCameraById(cameraId: string): Promise<Camera> {
    try {
      if (!cameraId) {
        throw new Error('Camera ID is required');
      }

      const result = await window.cameraAPI.getById(cameraId);
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch camera');
      }
      
      return result.data as Camera;
    } catch (error: any) {
      throw new Error(`Failed to get camera by ID: ${error.message}`);
    }
  }

  /**
   * Get cameras filtered by direction
   * 需求: 2.4
   * @param direction - The direction to filter by
   * @returns Promise<Camera[]> Array of cameras with the specified direction
   * @throws Error if the request fails
   */
  async getCamerasByDirection(direction: string): Promise<Camera[]> {
    try {
      if (!direction) {
        throw new Error('Direction is required');
      }

      const result = await window.cameraAPI.getByDirection(direction);
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch cameras by direction');
      }
      
      return result.data as Camera[];
    } catch (error: any) {
      throw new Error(`Failed to get cameras by direction: ${error.message}`);
    }
  }

  /**
   * Create a new camera
   * 需求: 3.1, 3.2, 3.3
   * @param cameraData - The camera data to create
   * @returns Promise<Camera> The created camera object
   * @throws Error if validation fails or creation fails
   */
  async createCamera(cameraData: CameraCreate): Promise<Camera> {
    try {
      // Validate required fields
      if (!cameraData.name || !cameraData.address || !cameraData.username || !cameraData.password) {
        throw new Error('Name, address, username, and password are required fields');
      }

      const result = await window.cameraAPI.create(cameraData);
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to create camera');
      }
      
      return result.data as Camera;
    } catch (error: any) {
      throw new Error(`Failed to create camera: ${error.message}`);
    }
  }

  /**
   * Update an existing camera
   * 需求: 4.1, 4.2
   * @param cameraId - The ID of the camera to update
   * @param updates - The fields to update
   * @returns Promise<Camera> The updated camera object
   * @throws Error if the camera is not found or update fails
   */
  async updateCamera(cameraId: string, updates: CameraUpdate): Promise<Camera> {
    try {
      if (!cameraId) {
        throw new Error('Camera ID is required');
      }

      if (!updates || Object.keys(updates).length === 0) {
        throw new Error('Update data is required');
      }

      const result = await window.cameraAPI.update(cameraId, updates);
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to update camera');
      }
      
      return result.data as Camera;
    } catch (error: any) {
      throw new Error(`Failed to update camera: ${error.message}`);
    }
  }

  /**
   * Delete a camera
   * 需求: 5.1
   * @param cameraId - The ID of the camera to delete
   * @returns Promise<void>
   * @throws Error if the camera is not found or deletion fails
   */
  async deleteCamera(cameraId: string): Promise<void> {
    try {
      if (!cameraId) {
        throw new Error('Camera ID is required');
      }

      const result = await window.cameraAPI.delete(cameraId);
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to delete camera');
      }
    } catch (error: any) {
      throw new Error(`Failed to delete camera: ${error.message}`);
    }
  }

  /**
   * Update camera status (online/offline)
   * 需求: 9.1
   * @param cameraId - The ID of the camera
   * @param status - The new status ('online' or 'offline')
   * @returns Promise<Camera> The updated camera object
   * @throws Error if the camera is not found or update fails
   */
  async updateCameraStatus(cameraId: string, status: 'online' | 'offline'): Promise<Camera> {
    try {
      if (!cameraId) {
        throw new Error('Camera ID is required');
      }

      if (!status || (status !== 'online' && status !== 'offline')) {
        throw new Error('Status must be either "online" or "offline"');
      }

      const result = await window.cameraAPI.updateStatus(cameraId, status);
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to update camera status');
      }
      
      return result.data as Camera;
    } catch (error: any) {
      throw new Error(`Failed to update camera status: ${error.message}`);
    }
  }
}

/**
 * Singleton instance of CameraService
 * Export for use throughout the application
 */
export const cameraService = new CameraService();
