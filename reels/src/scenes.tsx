import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';
import { loadFont as loadArchivoBlack } from '@remotion/google-fonts/ArchivoBlack';
import { loadFont as loadCormorant } from '@remotion/google-fonts/CormorantGaramond';
import { loadFont as loadInter } from '@remotion/google-fonts/Inter';

const { fontFamily: archivoBlack } = loadArchivoBlack();
const { fontFamily: cormorant } = loadCormorant('normal', { weights: ['500'], subsets: ['latin'] });
const { fontFamily: cormorantItalic } = loadCormorant('italic', { weights: ['500'], subsets: ['latin'] });
const { fontFamily: inter } = loadInter('normal', { weights: ['600', '900'], subsets: ['latin'] });

export const FONT_DISPLAY = `${archivoBlack}, system-ui, sans-serif`;
export const FONT_SERIF = `${cormorant}, Georgia, serif`;
export const FONT_SERIF_ITALIC = `${cormorantItalic}, Georgia, serif`;
export const FONT_SANS = `${inter}, system-ui, sans-serif`;

export const COLORS = {
  cosmos: '#14122B',
  gold: '#FFC857',
  pink: '#FF4D8D',
  violet: '#8A4DFF',
  moon: '#F5EFE0',
};

export const Background: React.FC = () => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(circle at 20% 12%, rgba(138,77,255,0.5) 0%, transparent 45%),
                   radial-gradient(circle at 85% 28%, rgba(255,77,141,0.5) 0%, transparent 50%),
                   radial-gradient(circle at 60% 95%, rgba(255,200,87,0.30) 0%, transparent 45%),
                   linear-gradient(160deg, #1a0f3a 0%, #14122B 55%, #2a0f3a 100%)`,
    }}
  />
);

export const HookScene: React.FC<{ headline: string; subline: string }> = ({ headline, subline }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: 'clamp' });
  const y = interpolate(frame, [0, 20], [40, 0], { extrapolateRight: 'clamp' });
  const scale = spring({ frame, fps, config: { damping: 14, stiffness: 80 } });

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', padding: 80, textAlign: 'center' }}>
      <div
        style={{
          opacity,
          transform: `translateY(${y}px) scale(${0.9 + 0.1 * scale})`,
          fontFamily: FONT_DISPLAY,
          fontSize: 140,
          lineHeight: 0.95,
          color: COLORS.moon,
          letterSpacing: -2,
          textShadow: '0 8px 40px rgba(0,0,0,0.5)',
          maxWidth: 920,
          whiteSpace: 'pre-line',
        }}
      >
        {headline}
      </div>
      <div
        style={{
          opacity: interpolate(frame, [25, 45], [0, 1], { extrapolateRight: 'clamp' }),
          marginTop: 50,
          fontFamily: FONT_SERIF_ITALIC,
          fontSize: 56,
          color: COLORS.gold,
          maxWidth: 880,
        }}
      >
        {subline}
      </div>
    </AbsoluteFill>
  );
};

export const SignScene: React.FC<{
  glyph: string;
  sign: string;
  message: string;
  color: string;
}> = ({ glyph, sign, message, color }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: 'clamp' });
  const slide = interpolate(frame, [0, 10], [60, 0], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        padding: 80,
        textAlign: 'center',
        opacity,
        transform: `translateY(${slide}px)`,
      }}
    >
      <div
        style={{
          fontFamily: FONT_SERIF,
          fontSize: 220,
          color,
          textShadow: `0 0 40px ${color}88`,
          marginBottom: 20,
          lineHeight: 1,
        }}
      >
        {glyph}
      </div>
      <div
        style={{
          fontFamily: FONT_DISPLAY,
          fontSize: 96,
          color: COLORS.moon,
          textTransform: 'lowercase',
          letterSpacing: -2,
          marginBottom: 36,
        }}
      >
        {sign}
      </div>
      <div
        style={{
          fontFamily: FONT_SERIF_ITALIC,
          fontWeight: 500,
          fontSize: 64,
          lineHeight: 1.15,
          color: COLORS.moon,
          maxWidth: 920,
        }}
      >
        {message}
      </div>
    </AbsoluteFill>
  );
};

export const CtaScene: React.FC<{ label?: string; headline: string }> = ({
  label = 'TAG SOMEONE WHO NEEDS THIS',
  headline,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacity = interpolate(frame, [0, 14], [0, 1], { extrapolateRight: 'clamp' });
  const scale = spring({ frame, fps, config: { damping: 12, stiffness: 90 } });
  const pulse = 1 + 0.04 * Math.sin(frame * 0.25);

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', padding: 80, textAlign: 'center', opacity }}>
      <div
        style={{
          fontFamily: FONT_SANS,
          fontSize: 24,
          fontWeight: 900,
          letterSpacing: 6,
          color: COLORS.gold,
          textTransform: 'uppercase',
          marginBottom: 30,
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontFamily: FONT_DISPLAY,
          fontSize: 130,
          lineHeight: 0.95,
          color: COLORS.moon,
          letterSpacing: -2,
          transform: `scale(${0.9 + 0.1 * scale})`,
          marginBottom: 60,
          whiteSpace: 'pre-line',
        }}
      >
        {headline}
      </div>
      <div
        style={{
          fontFamily: FONT_DISPLAY,
          fontSize: 44,
          letterSpacing: 4,
          color: COLORS.moon,
          textTransform: 'lowercase',
          transform: `scale(${pulse})`,
        }}
      >
        <span style={{ color: COLORS.pink }}>@</span>soul
        <span style={{ color: COLORS.pink }}>.</span>orbits
      </div>
    </AbsoluteFill>
  );
};
