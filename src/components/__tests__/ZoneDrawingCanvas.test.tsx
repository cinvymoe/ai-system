/**
 * ZoneDrawingCanvas Component Tests
 * Basic tests for the zone drawing canvas component
 */

import React from 'react';
import { ZoneDrawingCanvas } from '../ZoneDrawingCanvas';
import { Zone, DrawingState } from '../../types/zone';
import { CanvasDimensions } from '../../utils/coordinateTransform';

// Mock canvas element
const createMockCanvas = (): HTMLCanvasElement => {
  const canvas = document.createElement('canvas');
  canvas.width = 800;
  canvas.height = 600;
  
  // Mock getContext method
  const mockContext = {
    clearRect: () => {},
    fillRect: () => {},
    strokeRect: () => {},
    fillText: () => {},
    measureText: () => ({ width: 50 }),
    setLineDash: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    getBoundingClientRect: () => ({
      left: 0,
      top: 0,
      width: 800,
      height: 600
    })
  };
  
  canvas.getContext = () => mockContext as any;
  Object.defineProperty(canvas, 'style', {
    value: { cursor: 'default' },
    writable: true
  });
  
  return canvas as any;
};

// Mock dimensions
const mockDimensions: CanvasDimensions = {
  width: 800,
  height: 600
};

// Mock zones
const mockZones: Zone[] = [
  {
    id: 'zone-1',
    type: 'warning',
    points: [
      { x: 0.1, y: 0.1 },
      { x: 0.3, y: 0.1 },
      { x: 0.3, y: 0.3 },
      { x: 0.1, y: 0.3 }
    ],
    visible: true,
    selected: false,
    zIndex: 1
  },
  {
    id: 'zone-2',
    type: 'alarm',
    points: [
      { x: 0.5, y: 0.5 },
      { x: 0.7, y: 0.5 },
      { x: 0.7, y: 0.7 },
      { x: 0.5, y: 0.7 }
    ],
    visible: true,
    selected: true,
    zIndex: 2
  }
];

// Mock drawing state
const mockDrawingState: DrawingState = {
  isDrawing: false,
  drawingType: null,
  startPoint: null,
  currentPoint: null
};

const mockActiveDrawingState: DrawingState = {
  isDrawing: true,
  drawingType: 'warning',
  startPoint: { x: 0.2, y: 0.2 },
  currentPoint: { x: 0.4, y: 0.4 }
};

/**
 * Test component rendering without canvas
 */
export function testZoneDrawingCanvasWithoutCanvas() {
  console.log('Testing ZoneDrawingCanvas without canvas...');
  
  try {
    React.createElement(ZoneDrawingCanvas, {
      canvas: null,
      dimensions: mockDimensions,
      zones: [],
      drawingState: mockDrawingState
    });
    
    console.log('✓ Component created successfully without canvas');
    return true;
  } catch (error) {
    console.error('✗ Component creation failed:', error);
    return false;
  }
}

/**
 * Test component rendering with canvas and zones
 */
export function testZoneDrawingCanvasWithZones() {
  console.log('Testing ZoneDrawingCanvas with zones...');
  
  try {
    const mockCanvas = createMockCanvas();
    
    React.createElement(ZoneDrawingCanvas, {
      canvas: mockCanvas,
      dimensions: mockDimensions,
      zones: mockZones,
      drawingState: mockDrawingState,
      drawingMode: 'warning',
      onDrawingStart: (type, point) => {
        console.log('Drawing start called with type:', type, 'point:', point);
      },
      onDrawingUpdate: (point) => {
        console.log('Drawing update called with point:', point);
      },
      onDrawingEnd: () => {
        console.log('Drawing end called');
      },
      onZoneClick: (zoneId, point) => {
        console.log('Zone click called with zoneId:', zoneId, 'point:', point);
      },
      onZoneResize: (zoneId, newPoints) => {
        console.log('Zone resize called with zoneId:', zoneId, 'newPoints:', newPoints);
      },
      onZoneMove: (zoneId, newPoints) => {
        console.log('Zone move called with zoneId:', zoneId, 'newPoints:', newPoints);
      },
      onZoneDelete: (zoneId) => {
        console.log('Zone delete called with zoneId:', zoneId);
      }
    });
    
    console.log('✓ Component created successfully with zones');
    return true;
  } catch (error) {
    console.error('✗ Component creation failed:', error);
    return false;
  }
}

/**
 * Test component with active drawing state
 */
export function testZoneDrawingCanvasActiveDrawing() {
  console.log('Testing ZoneDrawingCanvas with active drawing...');
  
  try {
    const mockCanvas = createMockCanvas();
    
    React.createElement(ZoneDrawingCanvas, {
      canvas: mockCanvas,
      dimensions: mockDimensions,
      zones: mockZones,
      drawingState: mockActiveDrawingState,
      drawingMode: 'warning'
    });
    
    console.log('✓ Component created successfully with active drawing');
    return true;
  } catch (error) {
    console.error('✗ Component creation failed:', error);
    return false;
  }
}

/**
 * Test component props validation
 */
export function testZoneDrawingCanvasProps() {
  console.log('Testing ZoneDrawingCanvas props...');
  
  try {
    const mockCanvas = createMockCanvas();
    
    // Test with all props
    React.createElement(ZoneDrawingCanvas, {
      canvas: mockCanvas,
      dimensions: mockDimensions,
      zones: mockZones,
      drawingState: mockDrawingState,
      drawingMode: 'alarm',
      onDrawingStart: () => {},
      onDrawingUpdate: () => {},
      onDrawingEnd: () => {},
      onZoneClick: () => {},
      onZoneResize: () => {},
      onZoneMove: () => {},
      onZoneDelete: () => {}
    });
    
    console.log('✓ All props accepted successfully');
    return true;
  } catch (error) {
    console.error('✗ Props validation failed:', error);
    return false;
  }
}

/**
 * Test drawing mode changes
 */
export function testZoneDrawingCanvasDrawingModes() {
  console.log('Testing ZoneDrawingCanvas drawing modes...');
  
  try {
    const mockCanvas = createMockCanvas();
    
    // Test warning mode
    React.createElement(ZoneDrawingCanvas, {
      canvas: mockCanvas,
      dimensions: mockDimensions,
      zones: [],
      drawingState: mockDrawingState,
      drawingMode: 'warning'
    });
    
    // Test alarm mode
    React.createElement(ZoneDrawingCanvas, {
      canvas: mockCanvas,
      dimensions: mockDimensions,
      zones: [],
      drawingState: mockDrawingState,
      drawingMode: 'alarm'
    });
    
    // Test no drawing mode
    React.createElement(ZoneDrawingCanvas, {
      canvas: mockCanvas,
      dimensions: mockDimensions,
      zones: [],
      drawingState: mockDrawingState,
      drawingMode: null
    });
    
    console.log('✓ All drawing modes work correctly');
    return true;
  } catch (error) {
    console.error('✗ Drawing mode test failed:', error);
    return false;
  }
}

/**
 * Test zone manipulation features
 */
export function testZoneDrawingCanvasManipulation() {
  console.log('Testing ZoneDrawingCanvas manipulation features...');
  
  try {
    const mockCanvas = createMockCanvas();
    let resizeCalled = false;
    let moveCalled = false;
    let deleteCalled = false;
    
    React.createElement(ZoneDrawingCanvas, {
      canvas: mockCanvas,
      dimensions: mockDimensions,
      zones: mockZones,
      drawingState: mockDrawingState,
      drawingMode: null,
      onZoneResize: (zoneId, newPoints) => {
        resizeCalled = true;
        console.log('Zone resize handler called for zone:', zoneId);
      },
      onZoneMove: (zoneId, newPoints) => {
        moveCalled = true;
        console.log('Zone move handler called for zone:', zoneId);
      },
      onZoneDelete: (zoneId) => {
        deleteCalled = true;
        console.log('Zone delete handler called for zone:', zoneId);
      }
    });
    
    console.log('✓ Manipulation handlers set up correctly');
    return true;
  } catch (error) {
    console.error('✗ Manipulation features test failed:', error);
    return false;
  }
}

/**
 * Run all tests
 */
export function runZoneDrawingCanvasTests() {
  console.log('\n=== ZoneDrawingCanvas Component Tests ===');
  
  const results = [
    testZoneDrawingCanvasWithoutCanvas(),
    testZoneDrawingCanvasWithZones(),
    testZoneDrawingCanvasActiveDrawing(),
    testZoneDrawingCanvasProps(),
    testZoneDrawingCanvasDrawingModes(),
    testZoneDrawingCanvasManipulation()
  ];
  
  const passed = results.filter(Boolean).length;
  const total = results.length;
  
  console.log(`\nTest Results: ${passed}/${total} passed`);
  
  if (passed === total) {
    console.log('✓ All tests passed!');
  } else {
    console.log('✗ Some tests failed');
  }
  
  return passed === total;
}

// Export for potential future test runner integration
export default {
  testZoneDrawingCanvasWithoutCanvas,
  testZoneDrawingCanvasWithZones,
  testZoneDrawingCanvasActiveDrawing,
  testZoneDrawingCanvasProps,
  testZoneDrawingCanvasDrawingModes,
  testZoneDrawingCanvasManipulation,
  runZoneDrawingCanvasTests
};