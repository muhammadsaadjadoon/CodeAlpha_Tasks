import { useEffect, useRef, useState } from 'react';
import {
  Brush,
  Eraser,
  PenLine,
  RotateCcw,
  Sparkles,
} from 'lucide-react';

export function DrawingPad({
  onBlob,
}: {
  onBlob: (blob: Blob | null) => void;
}) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const [drawing, setDrawing] = useState(false);
  const [tool, setTool] = useState<'pen' | 'eraser'>('pen');
  const [brushSize, setBrushSize] = useState(16);

  function prepareCanvas() {
    const element = canvas.current;
    if (!element) return;

    const rect = element.getBoundingClientRect();
    const ratio = Math.max(1, window.devicePixelRatio || 1);
    element.width = Math.max(1, Math.round(rect.width * ratio));
    element.height = Math.max(1, Math.round(rect.height * ratio));

    const context = element.getContext('2d');
    if (!context) return;

    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, rect.width, rect.height);
    context.lineCap = 'round';
    context.lineJoin = 'round';
  }

  useEffect(() => {
    prepareCanvas();
  }, []);

  function pointerPosition(event: React.PointerEvent<HTMLCanvasElement>) {
    const rect = canvas.current!.getBoundingClientRect();
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
  }

  function start(event: React.PointerEvent<HTMLCanvasElement>) {
    const element = canvas.current;
    if (!element) return;

    const context = element.getContext('2d');
    if (!context) return;

    const point = pointerPosition(event);
    setDrawing(true);
    element.setPointerCapture(event.pointerId);
    context.beginPath();
    context.moveTo(point.x, point.y);
  }

  function move(event: React.PointerEvent<HTMLCanvasElement>) {
    if (!drawing) return;

    const element = canvas.current;
    const context = element?.getContext('2d');
    if (!element || !context) return;

    const point = pointerPosition(event);
    context.strokeStyle = tool === 'eraser' ? '#ffffff' : '#10213f';
    context.lineWidth = tool === 'eraser' ? brushSize * 2.2 : brushSize;
    context.lineTo(point.x, point.y);
    context.stroke();
  }

  function finish() {
    if (!drawing) return;
    setDrawing(false);
    canvas.current?.toBlob((blob) => onBlob(blob), 'image/png');
  }

  function clear() {
    prepareCanvas();
    onBlob(null);
  }

  return (
    <div className="draw-studio">
      <div className="draw-toolbar">
        <div className="draw-tool-group">
          <button
            type="button"
            className={tool === 'pen' ? 'active' : ''}
            onClick={() => setTool('pen')}
          >
            <PenLine />
            <span>Pen</span>
          </button>
          <button
            type="button"
            className={tool === 'eraser' ? 'active' : ''}
            onClick={() => setTool('eraser')}
          >
            <Eraser />
            <span>Eraser</span>
          </button>
        </div>

        <div className="brush-control">
          <Brush />
          <span>Stroke</span>
          {[12, 16, 22].map((size) => (
            <button
              type="button"
              key={size}
              className={brushSize === size ? 'active' : ''}
              onClick={() => setBrushSize(size)}
              aria-label={`Use ${size}px stroke`}
            >
              <i style={{ width: size / 2, height: size / 2 }} />
            </button>
          ))}
        </div>

        <button type="button" className="clear-canvas" onClick={clear}>
          <RotateCcw />
          <span>Clear</span>
        </button>
      </div>

      <div className="canvas-frame">
        <div className="canvas-corner corner-tl" />
        <div className="canvas-corner corner-tr" />
        <div className="canvas-corner corner-bl" />
        <div className="canvas-corner corner-br" />
        <canvas
          ref={canvas}
          className="drawing-canvas"
          onPointerDown={start}
          onPointerMove={move}
          onPointerUp={finish}
          onPointerCancel={finish}
        />
        <span className="canvas-hint"><Sparkles /> Write one character near the center</span>
      </div>
    </div>
  );
}
