/**
 * CameraFeedViewer Component
 * Displays camera feed with canvas overlay for zone drawing interactions
 * Requirements: 1.1
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Camera } from '../services/cameraService';
import { CanvasDimensions } from '../utils/coordinateTransform';

interface CameraFeedViewerProps {
  camera: Camera | null;
  onCanvasReady?: (canvas: HTMLCanvasElement, dimensions: CanvasDimensions) => void;
  onCanvasClick?: (event: React.MouseEvent<HTMLCanvasElement>) => void;
  onCanvasMouseDown?: (event: React.MouseEvent<HTMLCanvasElement>) => void;
  onCanvasMouseMove?: (event: React.MouseEvent<HTMLCanvasElement>) => void;
  onCanvasMouseUp?: (event: React.MouseEvent<HTMLCanvasElement>) => void;
  className?: string;
}

export function CameraFeedViewer({
  camera,
  onCanvasReady,
  onCanvasClick,
  onCanvasMouseDown,
  onCanvasMouseMove,
  onCanvasMouseUp,
  className = ''
}: CameraFeedViewerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const [videoLoaded, setVideoLoaded] = useState(false);
  const [videoError, setVideoError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [dimensions, setDimensions] = useState<CanvasDimensions>({ width: 0, height: 0 });

  const MAX_RETRY_COUNT = 3;

  // Update canvas dimensions to match video
  const updateCanvasDimensions = useCallback(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const container = containerRef.current;

    if (!video || !canvas || !container) return;

    // Get container dimensions
    const containerRect = container.getBoundingClientRect();
    const containerWidth = containerRect.width;
    const containerHeight = containerRect.height;

    // Calculate video aspect ratio
    const videoAspectRatio = video.videoWidth / video.videoHeight;
    const containerAspectRatio = containerWidth / containerHeight;

    let displayWidth: number;
    let displayHeight: number;

    // Fit video to container while maintaining aspect ratio
    if (videoAspectRatio > containerAspectRatio) {
      // Video is wider than container
      displayWidth = containerWidth;
      displayHeight = containerWidth / videoAspectRatio;
    } else {
      // Video is taller than container
      displayHeight = containerHeight;
      displayWidth = containerHeight * videoAspectRatio;
    }

    // Update canvas dimensions
    canvas.width = displayWidth;
    canvas.height = displayHeight;
    canvas.style.width = `${displayWidth}px`;
    canvas.style.height = `${displayHeight}px`;

    // Update video dimensions
    video.style.width = `${displayWidth}px`;
    video.style.height = `${displayHeight}px`;

    const newDimensions = { width: displayWidth, height: displayHeight };
    setDimensions(newDimensions);

    // Notify parent component
    if (onCanvasReady) {
      onCanvasReady(canvas, newDimensions);
    }
  }, [onCanvasReady]);

  // Handle video load
  const handleVideoLoad = useCallback(() => {
    setVideoLoaded(true);
    setVideoError(null);
    setRetryCount(0); // Reset retry count on successful load
    updateCanvasDimensions();
  }, [updateCanvasDimensions]);

  // Retry loading camera stream
  const retryLoadCamera = useCallback(() => {
    const video = videoRef.current;
    if (!video || !camera || retryCount >= MAX_RETRY_COUNT) return;
    
    console.log(`[CameraFeedViewer] Retrying camera load (${retryCount + 1}/${MAX_RETRY_COUNT})`);
    setRetryCount(prev => prev + 1);
    setVideoError(null);
    
    // Wait a bit before retrying
    setTimeout(() => {
      video.load();
    }, 2000);
  }, [camera, retryCount, MAX_RETRY_COUNT]);
    const video = event.currentTarget;
    const error = video.error;
    
    let errorMessage = 'Failed to load camera feed';
    if (error) {
      switch (error.code) {
        case MediaError.MEDIA_ERR_ABORTED:
          errorMessage = '视频加载被中止';
          break;
        case MediaError.MEDIA_ERR_NETWORK:
          errorMessage = '网络连接错误，请检查摄像头网络';
          break;
        case MediaError.MEDIA_ERR_DECODE:
          errorMessage = '视频解码错误，请检查摄像头设置';
          break;
        case MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED:
          errorMessage = '不支持的视频格式或RTSP流无法访问';
          break;
        default:
          errorMessage = `摄像头连接失败 (错误代码: ${error.code})`;
      }
    }
    
    console.error('[CameraFeedViewer] Video error:', {
      camera: camera?.name,
      url: camera?.url,
      errorCode: error?.code,
      errorMessage: error?.message
    });
    
    setVideoError(errorMessage);
    setVideoLoaded(false);
  }, [camera]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (videoLoaded) {
        updateCanvasDimensions();
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [videoLoaded, updateCanvasDimensions]);

  // Load camera stream when camera changes
  useEffect(() => {
    const video = videoRef.current;
    if (!video || !camera) {
      setVideoLoaded(false);
      setVideoError(null);
      return;
    }

    // Reset state
    setVideoLoaded(false);
    setVideoError(null);

    // Set video source
    video.src = camera.url;
    video.load();
  }, [camera]);

  // Handle canvas mouse events
  const handleCanvasMouseDown = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    if (onCanvasMouseDown) {
      onCanvasMouseDown(event);
    }
  }, [onCanvasMouseDown]);

  const handleCanvasMouseMove = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    if (onCanvasMouseMove) {
      onCanvasMouseMove(event);
    }
  }, [onCanvasMouseMove]);

  const handleCanvasMouseUp = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    if (onCanvasMouseUp) {
      onCanvasMouseUp(event);
    }
  }, [onCanvasMouseUp]);

  const handleCanvasClick = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    if (onCanvasClick) {
      onCanvasClick(event);
    }
  }, [onCanvasClick]);

  return (
    <div 
      ref={containerRef}
      className={`relative bg-slate-900 border border-slate-700 rounded-lg overflow-hidden ${className}`}
      style={{ minHeight: '300px' }}
    >
      {/* Camera selection prompt */}
      {!camera && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-slate-400 text-center">
            <div className="text-lg mb-2">No camera selected</div>
            <div className="text-sm">Select a camera to view the feed</div>
          </div>
        </div>
      )}

      {/* Video element */}
      {camera && (
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          onLoadedData={handleVideoLoad}
          onError={handleVideoError}
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 max-w-full max-h-full"
          style={{ 
            display: videoLoaded ? 'block' : 'none',
            objectFit: 'contain'
          }}
        />
      )}

      {/* Canvas overlay for drawing */}
      {camera && videoLoaded && (
        <canvas
          ref={canvasRef}
          onClick={handleCanvasClick}
          onMouseDown={handleCanvasMouseDown}
          onMouseMove={handleCanvasMouseMove}
          onMouseUp={handleCanvasMouseUp}
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 cursor-crosshair"
          style={{ 
            pointerEvents: 'auto',
            zIndex: 10
          }}
        />
      )}

      {/* Loading state */}
      {camera && !videoLoaded && !videoError && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-slate-400 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500 mx-auto mb-2"></div>
            <div className="text-sm">Loading camera feed...</div>
          </div>
        </div>
      )}

      {/* Error state */}
      {camera && videoError && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-red-400 text-center max-w-md px-4">
            <div className="text-lg mb-2">摄像头连接错误</div>
            <div className="text-sm mb-3">{videoError}</div>
            <div className="text-xs text-slate-500 space-y-1">
              <div>摄像头: {camera.name}</div>
              <div>地址: {camera.address}</div>
              <div className="mt-2 pt-2 border-t border-slate-600">
                <div>故障排除:</div>
                <div>• 检查摄像头电源和网络连接</div>
                <div>• 确认用户名密码是否正确</div>
                <div>• 检查RTSP端口554是否开放</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Camera info overlay */}
      {camera && videoLoaded && (
        <div className="absolute top-2 left-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
          {camera.name} • {camera.resolution} • {camera.fps}fps
        </div>
      )}

      {/* Dimensions info for debugging (only in development) */}
      {process.env.NODE_ENV === 'development' && videoLoaded && (
        <div className="absolute bottom-2 right-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
          {dimensions.width}×{dimensions.height}
        </div>
      )}
    </div>
  );
}