import { useEffect, useRef } from 'react';

export function Waveform({ analyser, active }: { analyser: AnalyserNode | null; active: boolean }) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const context = canvas.getContext('2d');
    if (!context) return;

    let frame = 0;
    const data = new Uint8Array(analyser?.fftSize || 256);

    const draw = () => {
      const dpr = window.devicePixelRatio || 1;
      const width = Math.max(1, Math.floor(canvas.clientWidth * dpr));
      const height = Math.max(1, Math.floor(canvas.clientHeight * dpr));

      if (canvas.width !== width || canvas.height !== height) {
        canvas.width = width;
        canvas.height = height;
      }

      const styles = getComputedStyle(canvas);
      const primary = styles.getPropertyValue('--wave-primary').trim() || '#6d72ff';
      const secondary = styles.getPropertyValue('--wave-secondary').trim() || '#2cc6c9';
      const quiet = styles.getPropertyValue('--wave-quiet').trim() || 'rgba(109,114,255,.18)';

      context.clearRect(0, 0, width, height);

      if (active && analyser) {
        analyser.getByteTimeDomainData(data);
      } else {
        data.fill(128);
      }

      const gradient = context.createLinearGradient(0, 0, width, 0);
      gradient.addColorStop(0, secondary);
      gradient.addColorStop(0.5, primary);
      gradient.addColorStop(1, secondary);

      context.beginPath();
      context.lineWidth = 2.5 * dpr;
      context.strokeStyle = active ? gradient : quiet;
      context.lineCap = 'round';
      context.lineJoin = 'round';

      data.forEach((value, index) => {
        const x = (index / (data.length - 1)) * width;
        const normalized = active ? (value - 128) / 128 : Math.sin(index / 9) * 0.02;
        const y = height / 2 + normalized * height * 0.36;
        if (index === 0) context.moveTo(x, y);
        else context.lineTo(x, y);
      });

      context.stroke();
      frame = requestAnimationFrame(draw);
    };

    draw();
    return () => cancelAnimationFrame(frame);
  }, [analyser, active]);

  return <canvas className="waveform" ref={ref} aria-label={active ? 'Live microphone waveform' : 'Voice waveform preview'}/>;
}
