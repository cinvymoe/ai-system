/**
 * Camera Store - Zustand State Management
 * ViewModel layer for camera data management
 * 需求: 2.1, 3.2, 4.2, 4.3, 4.4, 5.1, 5.2, 6.1, 6.2, 6.3, 7.5
 */

import { create } from 'zustand';
import { cameraService, Camera, CameraCreate, CameraUpdate } from '../services/cameraService';

/**
 * Camera store state interface
 */
interface CameraState {
  // State
  cameras: Camera[];
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchCameras: () => Promise<void>;
  fetchCamerasByDirection: (direction: string) => Promise<void>;
  addCamera: (cameraData: CameraCreate) => Promise<void>;
  updateCamera: (cameraId: string, updates: CameraUpdate) => Promise<void>;
  deleteCamera: (cameraId: string) => Promise<void>;
  toggleCameraEnabled: (cameraId: string) => Promise<void>;
  updateCameraStatus: (cameraId: string, status: 'online' | 'offline') => Promise<void>;
  clearError: () => void;
}

/**
 * Zustand camera store
 * Manages camera state and provides actions for CRUD operations
 */
export const useCameraStore = create<CameraState>((set, get) => ({
  // Initial state
  cameras: [],
  loading: false,
  error: null,

  /**
   * Fetch all cameras from the database
   * 需求: 2.1
   */
  fetchCameras: async () => {
    console.log('[CameraStore] fetchCameras called');
    set({ loading: true, error: null });
    try {
      console.log('[CameraStore] Calling cameraService.getAllCameras()...');
      const cameras = await cameraService.getAllCameras();
      console.log('[CameraStore] Received cameras:', cameras);
      console.log('[CameraStore] Number of cameras:', cameras.length);
      if (cameras.length > 0) {
        console.log('[CameraStore] First camera:', cameras[0]);
        console.log('[CameraStore] First camera directions:', cameras[0].directions);
      }
      set({ cameras, loading: false });
    } catch (error: any) {
      console.error('[CameraStore] Error fetching cameras:', error);
      set({ error: error.message, loading: false });
    }
  },

  /**
   * Fetch cameras filtered by direction
   * 需求: 2.4
   * @param direction - The direction to filter by
   */
  fetchCamerasByDirection: async (direction: string) => {
    set({ loading: true, error: null });
    try {
      const cameras = await cameraService.getCamerasByDirection(direction);
      set({ cameras, loading: false });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  /**
   * Add a new camera
   * 需求: 3.1, 3.2, 3.3, 3.5
   * @param cameraData - The camera data to create
   * @throws Error if creation fails (e.g., duplicate name)
   */
  addCamera: async (cameraData: CameraCreate) => {
    set({ loading: true, error: null });
    try {
      const newCamera = await cameraService.createCamera(cameraData);
      set(state => ({
        cameras: [...state.cameras, newCamera],
        loading: false,
      }));
    } catch (error: any) {
      set({ error: error.message, loading: false });
      throw error; // Re-throw so UI can handle it
    }
  },

  /**
   * Update an existing camera
   * 需求: 4.1, 4.2, 4.3
   * Implements optimistic update with rollback on failure
   * @param cameraId - The ID of the camera to update
   * @param updates - The fields to update
   * @throws Error if update fails
   */
  updateCamera: async (cameraId: string, updates: CameraUpdate) => {
    // Store original camera for rollback
    const originalCamera = get().cameras.find(cam => cam.id === cameraId);
    if (!originalCamera) {
      set({ error: 'Camera not found' });
      throw new Error('Camera not found');
    }

    // Optimistic update
    set(state => ({
      cameras: state.cameras.map(cam =>
        cam.id === cameraId ? { ...cam, ...updates } : cam
      ),
      loading: true,
      error: null,
    }));

    try {
      const updatedCamera = await cameraService.updateCamera(cameraId, updates);
      set(state => ({
        cameras: state.cameras.map(cam =>
          cam.id === cameraId ? updatedCamera : cam
        ),
        loading: false,
      }));
    } catch (error: any) {
      // Rollback on failure (需求: 4.4, 6.3)
      set(state => ({
        cameras: state.cameras.map(cam =>
          cam.id === cameraId ? originalCamera : cam
        ),
        error: error.message,
        loading: false,
      }));
      throw error; // Re-throw so UI can handle it
    }
  },

  /**
   * Delete a camera
   * 需求: 5.1, 5.2
   * Implements optimistic delete with rollback on failure
   * @param cameraId - The ID of the camera to delete
   * @throws Error if deletion fails
   */
  deleteCamera: async (cameraId: string) => {
    // Store original camera for rollback
    const originalCamera = get().cameras.find(cam => cam.id === cameraId);
    if (!originalCamera) {
      set({ error: 'Camera not found' });
      throw new Error('Camera not found');
    }

    // Optimistic delete
    set(state => ({
      cameras: state.cameras.filter(cam => cam.id !== cameraId),
      loading: true,
      error: null,
    }));

    try {
      await cameraService.deleteCamera(cameraId);
      set({ loading: false });
    } catch (error: any) {
      // Rollback on failure
      set(state => ({
        cameras: [...state.cameras, originalCamera].sort((a, b) => 
          a.created_at.localeCompare(b.created_at)
        ),
        error: error.message,
        loading: false,
      }));
      throw error; // Re-throw so UI can handle it
    }
  },

  /**
   * Toggle camera enabled status
   * 需求: 6.1, 6.2, 6.3
   * Implements optimistic update with rollback on failure
   * @param cameraId - The ID of the camera to toggle
   */
  toggleCameraEnabled: async (cameraId: string) => {
    const camera = get().cameras.find(cam => cam.id === cameraId);
    if (!camera) {
      set({ error: 'Camera not found' });
      return;
    }
    
    const newEnabled = !camera.enabled;
    
    // Optimistic update
    set(state => ({
      cameras: state.cameras.map(cam =>
        cam.id === cameraId ? { ...cam, enabled: newEnabled } : cam
      ),
      loading: true,
      error: null,
    }));
    
    try {
      const updatedCamera = await cameraService.updateCamera(cameraId, { enabled: newEnabled });
      set(state => ({
        cameras: state.cameras.map(cam =>
          cam.id === cameraId ? updatedCamera : cam
        ),
        loading: false,
      }));
    } catch (error: any) {
      // Rollback on failure (需求: 6.3)
      set(state => ({
        cameras: state.cameras.map(cam =>
          cam.id === cameraId ? { ...cam, enabled: camera.enabled } : cam
        ),
        error: error.message,
        loading: false,
      }));
    }
  },

  /**
   * Update camera status (online/offline)
   * 需求: 9.1, 7.5
   * @param cameraId - The ID of the camera
   * @param status - The new status
   */
  updateCameraStatus: async (cameraId: string, status: 'online' | 'offline') => {
    set({ loading: true, error: null });
    try {
      const updatedCamera = await cameraService.updateCameraStatus(cameraId, status);
      set(state => ({
        cameras: state.cameras.map(cam =>
          cam.id === cameraId ? updatedCamera : cam
        ),
        loading: false,
      }));
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  /**
   * Clear error state
   * Allows UI to dismiss error messages
   */
  clearError: () => set({ error: null }),
}));
