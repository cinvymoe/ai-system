/**
 * WebSocket 连接诊断工具
 * 用于调试 WebSocket 连接问题
 */

export interface DiagnosticResult {
  success: boolean;
  message: string;
  details?: any;
}

/**
 * 测试 WebSocket 连接
 */
export async function testWebSocketConnection(url: string): Promise<DiagnosticResult> {
  return new Promise((resolve) => {
    console.log('[WebSocket Diagnostics] Testing connection to:', url);
    
    try {
      const ws = new WebSocket(url);
      const timeout = setTimeout(() => {
        ws.close();
        resolve({
          success: false,
          message: '连接超时（5秒）',
          details: { url, timeout: 5000 }
        });
      }, 5000);

      ws.onopen = () => {
        clearTimeout(timeout);
        console.log('[WebSocket Diagnostics] ✓ Connection successful');
        ws.close();
        resolve({
          success: true,
          message: '连接成功',
          details: { url, readyState: ws.readyState }
        });
      };

      ws.onerror = (error) => {
        clearTimeout(timeout);
        console.error('[WebSocket Diagnostics] ✗ Connection error:', error);
        resolve({
          success: false,
          message: '连接错误',
          details: { url, error: error.toString() }
        });
      };

      ws.onclose = (event) => {
        clearTimeout(timeout);
        if (event.code !== 1000) {
          console.error('[WebSocket Diagnostics] ✗ Connection closed unexpectedly:', event);
          resolve({
            success: false,
            message: `连接关闭 (code: ${event.code})`,
            details: { url, code: event.code, reason: event.reason }
          });
        }
      };
    } catch (error) {
      console.error('[WebSocket Diagnostics] ✗ Failed to create WebSocket:', error);
      resolve({
        success: false,
        message: '无法创建 WebSocket',
        details: { url, error: error instanceof Error ? error.message : String(error) }
      });
    }
  });
}

/**
 * 检查 WebSocket API 是否可用
 */
export function checkWebSocketAvailability(): DiagnosticResult {
  if (typeof WebSocket === 'undefined') {
    return {
      success: false,
      message: 'WebSocket API 不可用',
      details: { available: false }
    };
  }

  return {
    success: true,
    message: 'WebSocket API 可用',
    details: { 
      available: true,
      constructor: WebSocket.name,
      prototype: Object.getOwnPropertyNames(WebSocket.prototype)
    }
  };
}

/**
 * 运行完整的诊断
 */
export async function runFullDiagnostics(url: string): Promise<{
  availability: DiagnosticResult;
  connection: DiagnosticResult;
}> {
  console.log('[WebSocket Diagnostics] Running full diagnostics...');
  
  const availability = checkWebSocketAvailability();
  console.log('[WebSocket Diagnostics] Availability check:', availability);
  
  let connection: DiagnosticResult;
  if (availability.success) {
    connection = await testWebSocketConnection(url);
    console.log('[WebSocket Diagnostics] Connection test:', connection);
  } else {
    connection = {
      success: false,
      message: '跳过连接测试（WebSocket API 不可用）'
    };
  }

  return { availability, connection };
}
