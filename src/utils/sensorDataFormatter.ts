/**
 * Sensor Data Formatting Utilities
 * Requirements: 2.2, 2.3, 2.4, 2.5, 2.6, 5.1, 7.2, 7.3
 * 
 * This module provides formatting functions for sensor data display:
 * - Number formatting (2 decimal places)
 * - Motion direction Chinese labels
 * - Color coding for motion states
 * - Timestamp formatting
 */

import type { MotionCommand } from '../types/sensor';

/**
 * 格式化数值为2位小数
 * Requirements: 7.2
 * 
 * @param value - 要格式化的数值
 * @returns 格式化后的字符串（保留2位小数）
 * 
 * @example
 * formatNumber(1.23456) // "1.23"
 * formatNumber(10) // "10.00"
 * formatNumber(-5.678) // "-5.68"
 */
export function formatNumber(value: number): string {
  return value.toFixed(2);
}

/**
 * 运动方向到中文标签的映射
 * Requirements: 2.2, 2.3, 2.4, 2.5, 2.6
 */
const MOTION_DIRECTION_LABELS: Record<MotionCommand['command'], string> = {
  forward: '前进',
  backward: '后退',
  turn_left: '左转',
  turn_right: '右转',
  stationary: '静止',
};

/**
 * 将运动方向转换为中文标签
 * Requirements: 2.2, 2.3, 2.4, 2.5, 2.6
 * 
 * @param command - 运动指令
 * @returns 中文标签
 * 
 * @example
 * getMotionLabel('forward') // "前进"
 * getMotionLabel('turn_left') // "左转"
 */
export function getMotionLabel(command: MotionCommand['command']): string {
  return MOTION_DIRECTION_LABELS[command] || '未知';
}

/**
 * 颜色编码配置
 * Requirements: 7.3
 * 
 * 定义不同运动状态的颜色方案：
 * - 前进: 绿色
 * - 后退: 红色
 * - 左转/右转: 蓝色
 * - 静止: 灰色
 */
export interface ColorScheme {
  text: string;      // 文字颜色类名
  bg: string;        // 背景颜色类名
  border: string;    // 边框颜色类名
}

const MOTION_COLOR_SCHEMES: Record<MotionCommand['command'], ColorScheme> = {
  forward: {
    text: 'text-green-500',
    bg: 'bg-green-950',
    border: 'border-green-500',
  },
  backward: {
    text: 'text-red-500',
    bg: 'bg-red-950',
    border: 'border-red-500',
  },
  turn_left: {
    text: 'text-blue-500',
    bg: 'bg-blue-950',
    border: 'border-blue-500',
  },
  turn_right: {
    text: 'text-blue-500',
    bg: 'bg-blue-950',
    border: 'border-blue-500',
  },
  stationary: {
    text: 'text-slate-500',
    bg: 'bg-slate-800',
    border: 'border-slate-500',
  },
};

/**
 * 获取运动方向的颜色编码
 * Requirements: 7.3
 * 
 * @param command - 运动指令
 * @returns 颜色方案对象
 * 
 * @example
 * getMotionColorScheme('forward') 
 * // { text: 'text-green-500', bg: 'bg-green-950', border: 'border-green-500' }
 */
export function getMotionColorScheme(command: MotionCommand['command']): ColorScheme {
  return MOTION_COLOR_SCHEMES[command] || MOTION_COLOR_SCHEMES.stationary;
}

/**
 * 格式化时间戳为可读格式
 * Requirements: 5.1
 * 
 * @param timestamp - ISO 8601格式的时间戳字符串
 * @returns 格式化后的时间字符串 (HH:MM:SS.mmm)
 * 
 * @example
 * formatTimestamp('2024-01-01T12:34:56.789Z') // "12:34:56.789"
 */
export function formatTimestamp(timestamp: string): string {
  try {
    const date = new Date(timestamp);
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');
    const milliseconds = date.getMilliseconds().toString().padStart(3, '0');
    
    return `${hours}:${minutes}:${seconds}.${milliseconds}`;
  } catch (error) {
    return timestamp; // 如果解析失败，返回原始字符串
  }
}

/**
 * 格式化相对时间（距离现在多久）
 * Requirements: 5.1
 * 
 * @param timestamp - ISO 8601格式的时间戳字符串
 * @returns 相对时间描述
 * 
 * @example
 * formatRelativeTime('2024-01-01T12:34:56.789Z') // "2秒前"
 */
export function formatRelativeTime(timestamp: string): string {
  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSeconds = Math.floor(diffMs / 1000);
    
    if (diffSeconds < 1) {
      return '刚刚';
    } else if (diffSeconds < 60) {
      return `${diffSeconds}秒前`;
    } else if (diffSeconds < 3600) {
      const minutes = Math.floor(diffSeconds / 60);
      return `${minutes}分钟前`;
    } else {
      const hours = Math.floor(diffSeconds / 3600);
      return `${hours}小时前`;
    }
  } catch (error) {
    return '未知';
  }
}

/**
 * 检查时间戳是否过期（超过指定毫秒数）
 * Requirements: 5.1
 * 
 * @param timestamp - ISO 8601格式的时间戳字符串
 * @param thresholdMs - 过期阈值（毫秒）
 * @returns 是否过期
 * 
 * @example
 * isTimestampStale('2024-01-01T12:34:56.789Z', 2000) // true if more than 2s old
 */
export function isTimestampStale(timestamp: string, thresholdMs: number): boolean {
  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    
    return diffMs > thresholdMs;
  } catch (error) {
    return true; // 如果解析失败，认为已过期
  }
}
