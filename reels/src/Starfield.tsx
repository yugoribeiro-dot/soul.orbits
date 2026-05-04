import React, { useMemo } from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';

type Star = {
  x: number;
  y: number;
  r: number;
  o: number;
  color: string;
  halo: boolean;
};

function seededRandom(seed: number) {
  let s = seed;
  return () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

export const Starfield: React.FC<{ seed?: number; width?: number; height?: number }> = ({
  seed = 7,
  width = 1080,
  height = 1920,
}) => {
  const frame = useCurrentFrame();
  const stars = useMemo<Star[]>(() => {
    const rnd = seededRandom(seed);
    const tiers: Array<[number, [number, number], [number, number], string, boolean]> = [
      [180, [0.4, 0.9], [0.18, 0.45], '255,255,255', false],
      [70, [0.9, 1.6], [0.45, 0.75], '255,255,255', false],
      [25, [1.4, 2.2], [0.55, 0.85], '255,200,140', false],
      [10, [1.8, 2.8], [0.65, 0.95], '255,200,220', false],
      [6, [2.4, 3.6], [0.85, 1.0], '255,220,170', true],
    ];
    const out: Star[] = [];
    for (const [count, [rmin, rmax], [omin, omax], color, halo] of tiers) {
      for (let i = 0; i < count; i++) {
        out.push({
          x: rnd() * width,
          y: rnd() * height,
          r: rmin + rnd() * (rmax - rmin),
          o: omin + rnd() * (omax - omin),
          color,
          halo,
        });
      }
    }
    return out;
  }, [seed, width, height]);

  // gentle parallax: stars drift down slowly
  const drift = (frame * 0.15) % height;

  return (
    <AbsoluteFill style={{ pointerEvents: 'none' }}>
      <svg
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        style={{ position: 'absolute', inset: 0 }}
      >
        <defs>
          <radialGradient id="g1" cx="20%" cy="15%" r="55%">
            <stop offset="0%" stopColor="rgba(138,77,255,0.30)" />
            <stop offset="100%" stopColor="rgba(138,77,255,0)" />
          </radialGradient>
          <radialGradient id="g2" cx="85%" cy="35%" r="55%">
            <stop offset="0%" stopColor="rgba(255,77,141,0.28)" />
            <stop offset="100%" stopColor="rgba(255,77,141,0)" />
          </radialGradient>
          <radialGradient id="g3" cx="55%" cy="92%" r="55%">
            <stop offset="0%" stopColor="rgba(255,200,87,0.18)" />
            <stop offset="100%" stopColor="rgba(255,200,87,0)" />
          </radialGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" />
          </filter>
        </defs>
        <rect width={width} height={height} fill="url(#g1)" />
        <rect width={width} height={height} fill="url(#g2)" />
        <rect width={width} height={height} fill="url(#g3)" />
        {stars.map((s, i) => {
          const y = (s.y + drift) % height;
          const twinkle = 0.7 + 0.3 * Math.sin((frame + i * 7) * 0.08);
          return (
            <circle
              key={i}
              cx={s.x}
              cy={y}
              r={s.r}
              fill={`rgba(${s.color},${(s.o * twinkle).toFixed(2)})`}
              filter={s.halo ? 'url(#glow)' : undefined}
            />
          );
        })}
      </svg>
    </AbsoluteFill>
  );
};
