/**
 * Range Slider Component
 * 双滑块范围选择器 - 用于选择角度范围
 */

import { useEffect, useRef, useState } from 'react';

interface RangeSliderProps {
  min: number;
  max: number;
  minValue: number;
  maxValue: number;
  onChange: (min: number, max: number) => void;
  step?: number;
  unit?: string;
}

export function RangeSlider({ 
  min, 
  max, 
  minValue, 
  maxValue, 
  onChange, 
  step = 1,
  unit = '°'
}: RangeSliderProps) {
  const [localMinValue, setLocalMinValue] = useState(minValue);
  const [localMaxValue, setLocalMaxValue] = useState(maxValue);
  const minThumbRef = useRef<HTMLInputElement>(null);
  const maxThumbRef = useRef<HTMLInputElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setLocalMinValue(minValue);
    setLocalMaxValue(maxValue);
  }, [minValue, maxValue]);

  const handleMinChange = (value: number) => {
    const newMin = Math.min(value, localMaxValue - step);
    setLocalMinValue(newMin);
    onChange(newMin, localMaxValue);
  };

  const handleMaxChange = (value: number) => {
    const newMax = Math.max(value, localMinValue + step);
    setLocalMaxValue(newMax);
    onChange(localMinValue, newMax);
  };

  // 计算高亮条的位置和宽度（只显示选中范围）
  const minPercent = ((localMinValue - min) / (max - min)) * 100;
  const maxPercent = ((localMaxValue - min) / (max - min)) * 100;
  
  return (
    <div className="space-y-3">
      {/* 数值显示 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-400">范围:</span>
          <span className="text-cyan-400 font-mono text-lg font-semibold">
            {localMinValue}{unit}
          </span>
          <span className="text-slate-500">-</span>
          <span className="text-cyan-400 font-mono text-lg font-semibold">
            {localMaxValue}{unit}
          </span>
        </div>
        <span className="text-sm text-slate-500">
          跨度: {localMaxValue - localMinValue}{unit}
        </span>
      </div>

      {/* 滑动条容器 */}
      <div ref={trackRef} className="relative h-8 flex items-center px-2">
        {/* 背景轨道 */}
        <div className="absolute left-2 right-2 h-2 bg-slate-700 rounded-lg"></div>
        
        {/* 选中范围高亮 - 从第一个圆点中心到第二个圆点中心 */}
        <div 
          className="absolute h-2 rounded-lg top-1/2 -translate-y-1/2"
          style={{
            left: `calc(8px + 10px + (100% - 16px - 20px) * ${minPercent / 100})`,
            width: `calc((100% - 16px - 20px) * ${(maxPercent - minPercent) / 100})`,
            background: 'linear-gradient(to right, #06b6d4, #22d3ee)'
          }}
        ></div>

        {/* 最小值滑块 */}
        <input
          ref={minThumbRef}
          type="range"
          min={min}
          max={max}
          step={step}
          value={localMinValue}
          onChange={(e) => handleMinChange(parseInt(e.target.value))}
          className="absolute w-full appearance-none bg-transparent pointer-events-none z-10 range-slider-min"
          style={{ padding: '0 8px' }}
        />

        {/* 最大值滑块 */}
        <input
          ref={maxThumbRef}
          type="range"
          min={min}
          max={max}
          step={step}
          value={localMaxValue}
          onChange={(e) => handleMaxChange(parseInt(e.target.value))}
          className="absolute w-full appearance-none bg-transparent pointer-events-none z-20 range-slider-max"
          style={{ padding: '0 8px' }}
        />
      </div>

      {/* 刻度标记 */}
      <div className="flex justify-between text-xs text-slate-500 px-1">
        <span>0°</span>
        <span>90°</span>
        <span>180°</span>
        <span>270°</span>
        <span>360°</span>
      </div>

      <style>{`
        .range-slider-min,
        .range-slider-max {
          height: 8px;
          -webkit-appearance: none;
          appearance: none;
          background: transparent !important;
        }

        .range-slider-min::-webkit-slider-runnable-track,
        .range-slider-max::-webkit-slider-runnable-track {
          height: 0px;
          background: transparent !important;
          -webkit-appearance: none;
          appearance: none;
        }

        .range-slider-min::-webkit-slider-thumb,
        .range-slider-max::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #06b6d4;
          cursor: pointer;
          pointer-events: all;
          border: 3px solid #0e1726;
          box-shadow: 0 2px 6px rgba(6, 182, 212, 0.4);
          transition: all 0.2s;
          margin-top: 0px;
        }

        .range-slider-min::-webkit-slider-thumb:hover,
        .range-slider-max::-webkit-slider-thumb:hover {
          background: #0891b2;
          transform: scale(1.1);
          box-shadow: 0 3px 8px rgba(6, 182, 212, 0.6);
        }

        .range-slider-min::-webkit-slider-thumb:active,
        .range-slider-max::-webkit-slider-thumb:active {
          transform: scale(1.2);
          box-shadow: 0 4px 12px rgba(6, 182, 212, 0.8);
        }

        .range-slider-min::-moz-range-track,
        .range-slider-max::-moz-range-track {
          height: 0px;
          background: transparent !important;
        }

        .range-slider-min::-moz-range-progress,
        .range-slider-max::-moz-range-progress {
          background: transparent !important;
        }

        .range-slider-min::-moz-range-thumb,
        .range-slider-max::-moz-range-thumb {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #06b6d4;
          cursor: pointer;
          pointer-events: all;
          border: 3px solid #0e1726;
          box-shadow: 0 2px 6px rgba(6, 182, 212, 0.4);
          transition: all 0.2s;
        }
      `}</style>
    </div>
  );
}
