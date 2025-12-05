import { useState, useRef } from 'react';
import './BackendTest.css';

interface TestResult {
  endpoint: string;
  status: 'success' | 'error' | 'pending';
  data?: any;
  error?: string;
  timestamp: string;
}

interface WebSocketMessage {
  type: string;
  timestamp: string;
  data: any;
}

export default function BackendTest() {
  const [backendUrl, setBackendUrl] = useState('http://localhost:8000');
  const [results, setResults] = useState<TestResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // WebSocket 相关状态
  const [wsConnected, setWsConnected] = useState(false);
  const [wsMessages, setWsMessages] = useState<WebSocketMessage[]>([]);
  const [wsMessageCount, setWsMessageCount] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);

  const testEndpoint = async (endpoint: string) => {
    const url = `${backendUrl}${endpoint}`;
    const timestamp = new Date().toLocaleTimeString();
    
    setIsLoading(true);
    
    try {
      const response = await fetch(url);
      const data = await response.json();
      
      setResults(prev => [{
        endpoint,
        status: response.ok ? 'success' : 'error',
        data,
        timestamp
      }, ...prev]);
    } catch (error) {
      setResults(prev => [{
        endpoint,
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp
      }, ...prev]);
    } finally {
      setIsLoading(false);
    }
  };

  const testAllEndpoints = async () => {
    setResults([]);
    await testEndpoint('/');
    await testEndpoint('/health');
  };

  const clearResults = () => {
    setResults([]);
  };

  // WebSocket 连接测试
  const connectWebSocket = () => {
    const wsUrl = backendUrl.replace('http://', 'ws://').replace('https://', 'wss://');
    const fullWsUrl = `${wsUrl}/api/sensor/stream`;
    
    try {
      const ws = new WebSocket(fullWsUrl);
      wsRef.current = ws;
      
      ws.onopen = () => {
        setWsConnected(true);
        setWsMessages([]);
        setWsMessageCount(0);
        console.log('WebSocket 已连接:', fullWsUrl);
      };
      
      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setWsMessageCount(prev => prev + 1);
          
          // 只保留最近的20条消息
          setWsMessages(prev => {
            const newMessages = [message, ...prev];
            return newMessages.slice(0, 20);
          });
        } catch (error) {
          console.error('解析 WebSocket 消息失败:', error);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket 错误:', error);
        setWsConnected(false);
      };
      
      ws.onclose = () => {
        console.log('WebSocket 已断开');
        setWsConnected(false);
      };
    } catch (error) {
      console.error('创建 WebSocket 连接失败:', error);
      setWsConnected(false);
    }
  };

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
      setWsConnected(false);
      setWsMessages([]);
      setWsMessageCount(0);
    }
  };

  const clearWsMessages = () => {
    setWsMessages([]);
    setWsMessageCount(0);
  };

  return (
    <div className="backend-test">
      <h2>后端通信测试</h2>
      
      <div className="test-controls">
        <div className="url-input">
          <label>后端地址:</label>
          <input
            type="text"
            value={backendUrl}
            onChange={(e) => setBackendUrl(e.target.value)}
            placeholder="http://localhost:8000"
          />
        </div>
        
        <div className="test-buttons">
          <button 
            onClick={() => testEndpoint('/')}
            disabled={isLoading}
          >
            测试根路径 (/)
          </button>
          <button 
            onClick={() => testEndpoint('/health')}
            disabled={isLoading}
          >
            测试健康检查 (/health)
          </button>
          <button 
            onClick={testAllEndpoints}
            disabled={isLoading}
            className="primary"
          >
            测试所有接口
          </button>
          <button 
            onClick={clearResults}
            disabled={isLoading}
            className="secondary"
          >
            清空结果
          </button>
        </div>
      </div>

      {isLoading && <div className="loading">测试中...</div>}

      <div className="test-results">
        <h3>HTTP 测试结果</h3>
        {results.length === 0 ? (
          <p className="no-results">暂无测试结果</p>
        ) : (
          results.map((result, index) => (
            <div key={index} className={`result-item ${result.status}`}>
              <div className="result-header">
                <span className="endpoint">{result.endpoint}</span>
                <span className="status">{result.status}</span>
                <span className="timestamp">{result.timestamp}</span>
              </div>
              <div className="result-body">
                {result.data && (
                  <pre>{JSON.stringify(result.data, null, 2)}</pre>
                )}
                {result.error && (
                  <div className="error-message">{result.error}</div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* WebSocket 测试区域 */}
      <div className="websocket-test">
        <h3>WebSocket 传感器流测试</h3>
        
        <div className="ws-controls">
          <div className="ws-status">
            <span className={`status-indicator ${wsConnected ? 'connected' : 'disconnected'}`}>
              {wsConnected ? '● 已连接' : '○ 未连接'}
            </span>
            {wsConnected && (
              <span className="message-count">
                已接收: {wsMessageCount} 条消息
              </span>
            )}
          </div>
          
          <div className="ws-buttons">
            {!wsConnected ? (
              <button 
                onClick={connectWebSocket}
                className="primary"
              >
                连接 WebSocket
              </button>
            ) : (
              <>
                <button 
                  onClick={disconnectWebSocket}
                  className="danger"
                >
                  断开连接
                </button>
                <button 
                  onClick={clearWsMessages}
                  className="secondary"
                >
                  清空消息
                </button>
              </>
            )}
          </div>
        </div>

        <div className="ws-endpoint-info">
          <strong>端点:</strong> {backendUrl.replace('http://', 'ws://').replace('https://', 'wss://')}/api/sensor/stream
        </div>

        <div className="ws-messages">
          <h4>实时消息流 (最近20条)</h4>
          {wsMessages.length === 0 ? (
            <p className="no-results">
              {wsConnected ? '等待消息...' : '未连接到 WebSocket'}
            </p>
          ) : (
            <div className="message-list">
              {wsMessages.map((msg, index) => (
                <div key={index} className={`ws-message ${msg.type}`}>
                  <div className="message-header">
                    <span className="message-type">{msg.type}</span>
                    <span className="message-time">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="message-body">
                    {msg.type === 'sensor_data' && msg.data && (
                      <div className="sensor-data-grid">
                        <div className="data-group">
                          <strong>加速度 (g):</strong>
                          <div>X: {msg.data.acceleration?.x?.toFixed(3)}</div>
                          <div>Y: {msg.data.acceleration?.y?.toFixed(3)}</div>
                          <div>Z: {msg.data.acceleration?.z?.toFixed(3)}</div>
                        </div>
                        <div className="data-group">
                          <strong>角速度 (°/s):</strong>
                          <div>X: {msg.data.angularVelocity?.x?.toFixed(2)}</div>
                          <div>Y: {msg.data.angularVelocity?.y?.toFixed(2)}</div>
                          <div>Z: {msg.data.angularVelocity?.z?.toFixed(2)}</div>
                        </div>
                        <div className="data-group">
                          <strong>角度 (°):</strong>
                          <div>X: {msg.data.angles?.x?.toFixed(2)}</div>
                          <div>Y: {msg.data.angles?.y?.toFixed(2)}</div>
                          <div>Z: {msg.data.angles?.z?.toFixed(2)}</div>
                        </div>
                      </div>
                    )}
                    {msg.type === 'motion_command' && msg.data && (
                      <div className="motion-command">
                        <div><strong>指令:</strong> {msg.data.command}</div>
                        <div><strong>线性强度:</strong> {msg.data.intensity?.toFixed(4)}</div>
                        <div><strong>角度强度:</strong> {msg.data.angularIntensity?.toFixed(4)}</div>
                        {msg.data.isMotionStart && (
                          <div className="motion-start">🚀 运动开始</div>
                        )}
                      </div>
                    )}
                    {msg.type === 'error' && msg.data && (
                      <div className="error-data">
                        <strong>错误:</strong> {msg.data.error}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
