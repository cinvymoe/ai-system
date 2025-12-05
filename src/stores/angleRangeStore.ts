/**
 * Angle Range Store - Zustand State Management
 */

import { create } from 'zustand';
import { angleRangeService, AngleRange, AngleRangeCreate, AngleRangeUpdate } from '../services/angleRangeService';

interface AngleRangeState {
  // State
  angleRanges: AngleRange[];
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchAngleRanges: () => Promise<void>;
  addAngleRange: (data: AngleRangeCreate) => Promise<void>;
  updateAngleRange: (id: string, data: AngleRangeUpdate) => Promise<void>;
  deleteAngleRange: (id: string) => Promise<void>;
  toggleAngleRangeEnabled: (id: string) => Promise<void>;
  clearError: () => void;
}

export const useAngleRangeStore = create<AngleRangeState>((set, get) => ({
  // Initial state
  angleRanges: [],
  loading: false,
  error: null,

  /**
   * Fetch all angle ranges
   */
  fetchAngleRanges: async () => {
    set({ loading: true, error: null });
    try {
      const angleRanges = await angleRangeService.getAllAngleRanges();
      set({ angleRanges, loading: false });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  /**
   * Add a new angle range
   */
  addAngleRange: async (data: AngleRangeCreate) => {
    set({ loading: true, error: null });
    try {
      const newAngleRange = await angleRangeService.createAngleRange(data);
      set(state => ({
        angleRanges: [...state.angleRanges, newAngleRange],
        loading: false,
      }));
    } catch (error: any) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  /**
   * Update an existing angle range
   */
  updateAngleRange: async (id: string, data: AngleRangeUpdate) => {
    const original = get().angleRanges.find(ar => ar.id === id);
    if (!original) {
      set({ error: 'Angle range not found' });
      throw new Error('Angle range not found');
    }

    // Optimistic update
    set(state => ({
      angleRanges: state.angleRanges.map(ar =>
        ar.id === id ? { ...ar, ...data } : ar
      ),
      loading: true,
      error: null,
    }));

    try {
      const updated = await angleRangeService.updateAngleRange(id, data);
      set(state => ({
        angleRanges: state.angleRanges.map(ar =>
          ar.id === id ? updated : ar
        ),
        loading: false,
      }));
    } catch (error: any) {
      // Rollback on failure
      set(state => ({
        angleRanges: state.angleRanges.map(ar =>
          ar.id === id ? original : ar
        ),
        error: error.message,
        loading: false,
      }));
      throw error;
    }
  },

  /**
   * Delete an angle range
   */
  deleteAngleRange: async (id: string) => {
    const original = get().angleRanges.find(ar => ar.id === id);
    if (!original) {
      set({ error: 'Angle range not found' });
      throw new Error('Angle range not found');
    }

    // Optimistic delete
    set(state => ({
      angleRanges: state.angleRanges.filter(ar => ar.id !== id),
      loading: true,
      error: null,
    }));

    try {
      await angleRangeService.deleteAngleRange(id);
      set({ loading: false });
    } catch (error: any) {
      // Rollback on failure
      set(state => ({
        angleRanges: [...state.angleRanges, original],
        error: error.message,
        loading: false,
      }));
      throw error;
    }
  },

  /**
   * Toggle angle range enabled status
   */
  toggleAngleRangeEnabled: async (id: string) => {
    const angleRange = get().angleRanges.find(ar => ar.id === id);
    if (!angleRange) {
      set({ error: 'Angle range not found' });
      return;
    }
    
    const newEnabled = !angleRange.enabled;
    
    // Optimistic update
    set(state => ({
      angleRanges: state.angleRanges.map(ar =>
        ar.id === id ? { ...ar, enabled: newEnabled } : ar
      ),
      loading: true,
      error: null,
    }));
    
    try {
      const updated = await angleRangeService.updateAngleRange(id, { enabled: newEnabled });
      set(state => ({
        angleRanges: state.angleRanges.map(ar =>
          ar.id === id ? updated : ar
        ),
        loading: false,
      }));
    } catch (error: any) {
      // Rollback on failure
      set(state => ({
        angleRanges: state.angleRanges.map(ar =>
          ar.id === id ? { ...ar, enabled: angleRange.enabled } : ar
        ),
        error: error.message,
        loading: false,
      }));
    }
  },

  /**
   * Clear error state
   */
  clearError: () => set({ error: null }),
}));
