/**
 * AI Settings Service - Frontend API Client
 * Handles communication with backend AI settings API
 */

/**
 * 坐标点接口
 */
export interface Point {
  x: number; // 0-1
  y: number; // 0-1
}

/**
 * AI 设置接口
 */
export interface AISettings {
  id: number;
  enabled: boolean;
  camera_id: string | null;
  camera_name: string | null;
  camera_url: string | null;
  confidence_threshold: number; // 0-100
  danger_zone: Point[] | null; // 4个点
  warning_zone: Point[] | null; // 4个点
  sound_alarm: boolean;
  visual_alarm: boolean;
  auto_screenshot: boolean;
  alarm_cooldown: number; // 秒
  created_at: string;
  updated_at: string;
}

/**
 * 创建 AI 设置数据
 */
export interface AISettingsCreate {
  enabled?: boolean;
  camera_id?: string | null;
  confidence_threshold?: number;
  danger_zone?: Point[] | null;
  warning_zone?: Point[] | null;
  sound_alarm?: boolean;
  visual_alarm?: boolean;
  auto_screenshot?: boolean;
  alarm_cooldown?: number;
}

/**
 * 更新 AI 设置数据
 */
export interface AISettingsUpdate {
  enabled?: boolean;
  camera_id?: string | null;
  confidence_threshold?: number;
  danger_zone?: Point[] | null;
  warning_zone?: Point[] | null;
  sound_alarm?: boolean;
  visual_alarm?: boolean;
  auto_screenshot?: boolean;
  alarm_cooldown?: number;
}

/**
 * AI Settings Service class
 */
export class AISettingsService {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://127.0.0.1:8000') {
    this.baseUrl = baseUrl;
  }

  /**
   * 获取 AI 设置
   */
  async getSettings(): Promise<AISettings> {
    const response = await fetch(`${this.baseUrl}/api/ai-settings`);
    if (!response.ok) {
      throw new Error(`Failed to fetch AI settings: ${response.statusText}`);
    }
    return await response.json();
  }

  /**
   * 创建 AI 设置
   */
  async createSettings(data: AISettingsCreate): Promise<AISettings> {
    const response = await fetch(`${this.baseUrl}/api/ai-settings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create AI settings');
    }
    return await response.json();
  }

  /**
   * 更新 AI 设置
   */
  async updateSettings(settingsId: number, data: AISettingsUpdate): Promise<AISettings> {
    const response = await fetch(`${this.baseUrl}/api/ai-settings/${settingsId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update AI settings');
    }
    return await response.json();
  }

  /**
   * 删除 AI 设置
   */
  async deleteSettings(settingsId: number): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/ai-settings/${settingsId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete AI settings');
    }
  }

  /**
   * 绑定摄像头
   */
  async bindCamera(settingsId: number, cameraId: string): Promise<AISettings> {
    const response = await fetch(
      `${this.baseUrl}/api/ai-settings/${settingsId}/bind-camera/${cameraId}`,
      {
        method: 'POST',
      }
    );
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to bind camera');
    }
    return await response.json();
  }

  /**
   * 解绑摄像头
   */
  async unbindCamera(settingsId: number): Promise<AISettings> {
    const response = await fetch(
      `${this.baseUrl}/api/ai-settings/${settingsId}/unbind-camera`,
      {
        method: 'POST',
      }
    );
    if (!response.ok) {
      throw new Error('Failed to unbind camera');
    }
    return await response.json();
  }
}

/**
 * Singleton instance
 */
export const aiSettingsService = new AISettingsService();
