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
  
  // WebSocket 相关状态 - 传感器流
  const [wsConnected, setWsConnected] = useState(false);
  const [wsMessages, setWsMessages] = useState<WebSocketMessage[]>([]);
  const [wsMessageCount, setWsMessageCount] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);

  // WebSocket 相关状态 - 消息代理流
  const [brokerWsConnected, setBrokerWsConnected] = useState(false);
  const [brokerWsMessages, setBrokerWsMessages] = useState<any[]>([]);
  const [brokerMessageCount, setBrokerMessageCount] = useState(0);
  const [currentCameras, setCurrentCameras] = useState<any[]>([]);
  const brokerWsRef = useRef<WebSocket | null>(null);

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

  // 消息代理 WebSocket 连接测试
  const connectBrokerWebSocket = () => {
    const wsUrl = backendUrl.replace('http://', 'ws://').replace('https://', 'wss://');
    const fullWsUrl = `${wsUrl}/api/broker/stream`;
    
    try {
      const ws = new WebSocket(fullWsUrl);
      brokerWsRef.current = ws;
      
      ws.onopen = () => {
        setBrokerWsConnected(true);
        setBrokerWsMessages([]);
        setBrokerMessageCount(0);
        setCurrentCameras([]);
        console.log('消息代理 WebSocket 已连接:', fullWsUrl);
      };
      
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setBrokerMessageCount(prev => prev + 1);
          
          // 更新当前摄像头列表
          if (message.cameras) {
            setCurrentCameras(message.cameras);
          }
          
          // 只保留最近的20条消息
          setBrokerWsMessages(prev => {
            const newMessages = [message, ...prev];
            return newMessages.slice(0, 20);
          });
        } catch (error) {
          console.error('解析消息代理 WebSocket 消息失败:', error);
        }
      };
      
      ws.onerror = (error) => {
        console.error('消息代理 WebSocket 错误:', error);
        setBrokerWsConnected(false);
      };
      
      ws.onclose = () => {
        console.log('消息代理 WebSocket 已断开');
        setBrokerWsConnected(false);
      };
    } catch (error) {
      console.error('创建消息代理 WebSocket 连接失败:', error);
      setBrokerWsConnected(false);
    }
  };

  const disconnectBrokerWebSocket = () => {
    if (brokerWsRef.current) {
      brokerWsRef.current.close();
      brokerWsRef.current = null;
      setBrokerWsConnected(false);
      setBrokerWsMessages([]);
      setBrokerMessageCount(0);
      setCurrentCameras([]);
    }
  };

  const clearBrokerWsMessages = () => {
    setBrokerWsMessages([]);
    setBrokerMessageCount(0);
  };

  const requestBrokerRefresh = () => {
    if (brokerWsRef.current && brokerWsConnected) {
      brokerWsRef.current.send('refresh');
    }
  };

  // 测试发布消息
  const testPublishMessage = async (messageType: string, data: any) => {
    try {
      const response = await fetch(`${backendUrl}/api/broker/test/publish?message_type=${messageType}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      
      const result = await response.json();
      
      setResults(prev => [{
        endpoint: `/api/broker/test/publish (${messageType})`,
        status: response.ok ? 'success' : 'error',
        data: result,
        timestamp: new Date().toLocaleTimeString()
      }, ...prev]);
      
      return result;
    } catch (error) {
      console.error('发布消息失败:', error);
      setResults(prev => [{
        endpoint: `/api/broker/test/publish (${messageType})`,
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toLocaleTimeString()
      }, ...prev]);
    }
  };

  // 快速测试按钮
  const testDirectionMessage = () => {
    testPublishMessage('direction_result', {
      command: 'forward',
      intensity: 0.85,
      angular_intensity: 0.0,
      timestamp: new Date().toISOString()
    });
  };

  const testAngleMessage = () => {
    testPublishMessage('angle_value', {
      angle: 45.5,
      timestamp: new Date().toISOString()
    });
  };

  const testAIAlertMessage = () => {
    testPublishMessage('ai_alert', {
      alert_type: 'motion_detected',
      severity: 'high',
      timestamp: new Date().toISOString(),
      metadata: {
        confidence: 0.92,
        location: 'zone_1'
      }
    });
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

      {/* WebSocket 传感器流测试区域 */}
      <div className="websocket-test">
        <h3>📡 WebSocket 传感器流测试</h3>
        
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

      {/* 消息代理 WebSocket 测试区域 */}
      <div className="websocket-test broker-test">
        <h3>🔄 消息代理 WebSocket 测试</h3>
        
        <div className="ws-controls">
          <div className="ws-status">
            <span className={`status-indicator ${brokerWsConnected ? 'connected' : 'disconnected'}`}>
              {brokerWsConnected ? '● 已连接' : '○ 未连接'}
            </span>
            {brokerWsConnected && (
              <>
                <span className="message-count">
                  已接收: {brokerMessageCount} 条消息
                </span>
                <span className="camera-count">
                  当前摄像头: {currentCameras.length} 个
                </span>
              </>
            )}
          </div>
          
          <div className="ws-buttons">
            {!brokerWsConnected ? (
              <button 
                onClick={connectBrokerWebSocket}
                className="primary"
              >
                连接消息代理
              </button>
            ) : (
              <>
                <button 
                  onClick={disconnectBrokerWebSocket}
                  className="danger"
                >
                  断开连接
                </button>
                <button 
                  onClick={requestBrokerRefresh}
                  className="secondary"
                >
                  刷新状态
                </button>
                <button 
                  onClick={clearBrokerWsMessages}
                  className="secondary"
                >
                  清空消息
                </button>
              </>
            )}
          </div>
        </div>

        <div className="ws-endpoint-info">
          <strong>端点:</strong> {backendUrl.replace('http://', 'ws://').replace('https://', 'wss://')}/api/broker/stream
        </div>

        {/* 测试消息发布按钮 */}
        <div className="test-publish-section">
          <h4>📤 测试消息发布</h4>
          <div className="publish-buttons">
            <button 
              onClick={testDirectionMessage}
              className="test-btn direction-btn"
              title="发布方向消息: forward"
            >
              🧭 发送方向消息
            </button>
            <button 
              onClick={testAngleMessage}
              className="test-btn angle-btn"
              title="发布角度消息: 45.5°"
            >
              📐 发送角度消息
            </button>
            <button 
              onClick={testAIAlertMessage}
              className="test-btn alert-btn"
              title="发布AI报警消息"
            >
              🚨 发送AI报警
            </button>
          </div>
          <p className="test-hint">
            💡 提示: 先连接消息代理 WebSocket，然后点击按钮发送测试消息，观察实时消息流中的处理结果
          </p>
        </div>

        {/* 当前摄像头列表 */}
        {brokerWsConnected && currentCameras.length > 0 && (
          <div className="current-cameras">
            <h4>📹 当前激活的摄像头</h4>
            <div className="camera-grid">
              {currentCameras.map((camera: any, index: number) => (
                <div key={index} className="camera-card">
                  <div className="camera-name">{camera.name || camera.id || `摄像头 ${index + 1}`}</div>
                  {camera.url && (
                    <div className="camera-url">{camera.url}</div>
                  )}
                  {camera.status && (
                    <div className={`camera-status ${camera.status}`}>
                      {camera.status === 'online' ? '🟢 在线' : '🔴 离线'}
                    </div>
                  )}
                  {camera.directions && camera.directions.length > 0 && (
                    <div className="camera-directions">
                      方向: {camera.directions.join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="ws-messages">
          <h4>实时消息流 (最近20条)</h4>
          {brokerWsMessages.length === 0 ? (
            <p className="no-results">
              {brokerWsConnected ? '等待消息...' : '未连接到消息代理 WebSocket'}
            </p>
          ) : (
            <div className="message-list broker-messages">
              {brokerWsMessages.map((msg, index) => (
                <div key={index} className={`ws-message broker-message ${msg.type}`}>
                  <div className="message-header">
                    <span className="message-type">
                      {msg.type === 'current_state' && '📊 当前状态'}
                      {msg.type === 'direction_result' && '🧭 方向消息'}
                      {msg.type === 'angle_value' && '📐 角度消息'}
                      {msg.type === 'ai_alert' && '🚨 AI报警'}
                      {msg.type === 'error' && '❌ 错误'}
                    </span>
                    <span className="message-time">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </span>
                    {msg.message_id && (
                      <span className="message-id">ID: {msg.message_id.substring(0, 8)}</span>
                    )}
                  </div>
                  <div className="message-body">
                    {msg.type === 'current_state' && msg.data && (
                      <div className="current-state-data">
                        <div className="state-section">
                          <strong>方向映射:</strong>
                          {msg.data.directions && Object.keys(msg.data.directions).length > 0 ? (
                            <ul>
                              {Object.entries(msg.data.directions).map(([dir, cameras]: [string, any]) => (
                                <li key={dir}>
                                  {dir}: {Array.isArray(cameras) ? cameras.length : 0} 个摄像头
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <div className="no-data">无方向映射</div>
                          )}
                        </div>
                        <div className="state-section">
                          <strong>角度范围:</strong>
                          {msg.data.angle_ranges && msg.data.angle_ranges.length > 0 ? (
                            <div>{msg.data.angle_ranges.length} 个角度范围</div>
                          ) : (
                            <div className="no-data">无角度范围</div>
                          )}
                        </div>
                      </div>
                    )}
                    {msg.type === 'direction_result' && msg.data && (
                      <div className="direction-data">
                        <div><strong>指令:</strong> {msg.data.command}</div>
                        {msg.data.intensity !== undefined && (
                          <div><strong>强度:</strong> {msg.data.intensity}</div>
                        )}
                        {msg.cameras && (
                          <div><strong>匹配摄像头:</strong> {msg.cameras.length} 个</div>
                        )}
                      </div>
                    )}
                    {msg.type === 'angle_value' && msg.data && (
                      <div className="angle-data">
                        <div><strong>角度:</strong> {msg.data.angle}°</div>
                        {msg.cameras && (
                          <div><strong>匹配摄像头:</strong> {msg.cameras.length} 个</div>
                        )}
                      </div>
                    )}
                    {msg.type === 'ai_alert' && msg.data && (
                      <div className="ai-alert-data">
                        <div><strong>报警类型:</strong> {msg.data.alert_type}</div>
                        {msg.data.severity && (
                          <div><strong>严重程度:</strong> {msg.data.severity}</div>
                        )}
                        {msg.cameras && (
                          <div><strong>相关摄像头:</strong> {msg.cameras.length} 个</div>
                        )}
                      </div>
                    )}
                    {msg.type === 'error' && msg.data && (
                      <div className="error-data">
                        <strong>错误:</strong> {msg.data.error}
                      </div>
                    )}
                    {msg.cameras && msg.cameras.length > 0 && msg.type !== 'current_state' && (
                      <div className="message-cameras">
                        <strong>摄像头列表:</strong>
                        <div className="mini-camera-list">
                          {msg.cameras.slice(0, 5).map((cam: any, idx: number) => (
                            <span key={idx} className="mini-camera-tag">
                              {cam.name || cam.id || `摄像头${idx + 1}`}
                            </span>
                          ))}
                          {msg.cameras.length > 5 && (
                            <span className="more-cameras">+{msg.cameras.length - 5} 更多</span>
                          )}
                        </div>
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
