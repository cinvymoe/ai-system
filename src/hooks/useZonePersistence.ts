/**
 * Zone Persistence Hook
 * Handles saving and loading zones from the backend via AI Settings service
 */

import { useCallback } from 'react';
import { Zone } from '../types/zone';
import { Point, aiSettingsService, AISettings } from '../services/aiSettingsService';
import { retryZoneSave } from '../utils/networkRetry';

/**
 * Zone persistence hook return type
 */
export interface UseZonePersistenceReturn {
  saveZones: (zones: Zone[], settingsId: number) => Promise<void>;
  loadZones: (settings: AISettings) => Zone[];
  convertZonesToApiFormat: (zones: Zone[]) => { danger_zone: Point[] | null; warning_zone: Point[] | null };
}

/**
 * Zone persistence hook
 */
export function useZonePersistence(): UseZonePersistenceReturn {
  /**
   * Convert zones to API format for backend
   */
  const convertZonesToApiFormat = useCallback((zones: Zone[]) => {
    const warningZones = zones.filter(zone => zone.type === 'warning');
    const alarmZones = zones.filter(zone => zone.type === 'alarm');

    // For now, we only support one zone of each type
    // This matches the current backend schema
    const warning_zone = warningZones.length > 0 ? warningZones[0].points : null;
    const danger_zone = alarmZones.length > 0 ? alarmZones[0].points : null;

    return {
      warning_zone,
      danger_zone
    };
  }, []);

  /**
   * Convert API format to zones
   */
  const convertApiFormatToZones = useCallback((settings: AISettings): Zone[] => {
    const zones: Zone[] = [];

    // Convert warning zone
    if (settings.warning_zone && settings.warning_zone.length === 4) {
      zones.push({
        id: `warning-zone-${settings.camera_id || settings.id}`,
        type: 'warning',
        points: settings.warning_zone,
        visible: true,
        selected: false,
        zIndex: 1
      });
    }

    // Convert danger/alarm zone
    if (settings.danger_zone && settings.danger_zone.length === 4) {
      zones.push({
        id: `alarm-zone-${settings.camera_id || settings.id}`,
        type: 'alarm',
        points: settings.danger_zone,
        visible: true,
        selected: false,
        zIndex: 2
      });
    }

    return zones;
  }, []);

  /**
   * Save zones to backend with retry logic
   */
  const saveZones = useCallback(async (zones: Zone[], settingsId: number): Promise<void> => {
    const apiFormat = convertZonesToApiFormat(zones);
    
    try {
      await retryZoneSave(
        () => aiSettingsService.updateSettings(settingsId, {
          warning_zone: apiFormat.warning_zone,
          danger_zone: apiFormat.danger_zone
        }),
        (attempt, error) => {
          console.warn(`Zone save attempt ${attempt} failed:`, error.message);
        }
      );
    } catch (error) {
      console.error('Failed to save zones after retries:', error);
      
      // Provide more specific error messages based on error type
      if (error instanceof Error) {
        if (error.message.includes('fetch') || error.message.includes('network')) {
          throw new Error('Network error: Unable to connect to server. Please check your connection and try again.');
        } else if (error.message.includes('timeout')) {
          throw new Error('Request timeout: Server response too slow. Please try again.');
        } else if (error.message.includes('401') || error.message.includes('unauthorized')) {
          throw new Error('Authentication error: Please log in again');
        } else if (error.message.includes('403') || error.message.includes('forbidden')) {
          throw new Error('Permission error: You cannot modify zone settings');
        } else if (error.message.includes('404')) {
          throw new Error('Configuration not found: AI settings may have been deleted');
        } else if (error.message.includes('500')) {
          throw new Error('Server error: Please try again later');
        } else {
          throw new Error(`Save failed: ${error.message}`);
        }
      }
      
      throw new Error('Failed to save zone configuration after multiple attempts');
    }
  }, [convertZonesToApiFormat]);

  /**
   * Load zones from AI settings
   */
  const loadZones = useCallback((settings: AISettings): Zone[] => {
    return convertApiFormatToZones(settings);
  }, [convertApiFormatToZones]);

  return {
    saveZones,
    loadZones,
    convertZonesToApiFormat
  };
}