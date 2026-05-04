import React from 'react';
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from 'remotion';
import { loadFont as loadArchivoBlack } from '@remotion/google-fonts/ArchivoBlack';
import { loadFont as loadCormorant } from '@remotion/google-fonts/CormorantGaramond';
import { loadFont as loadInter } from '@remotion/google-fonts/Inter';
import { Starfield } from './Starfield';

const { fontFamily: archivoBlack } = loadArchivoBlack();
const { fontFamily: cormorant } = loadCormorant('normal', { weights: ['500'], subsets: ['latin'] });
const cormorantItalic = loadCormorant('italic', { weights: ['500'], subsets: ['latin'] }).fontFamily;
const { fontFamily: inter } = loadInter('normal', { weights: ['600', '900'], subsets: ['latin'] });

const COLORS = {
  cosmos: '#14122B',
  gold: '#FFC857',
  pink: '#FF4D8D',
  violet: '#8A4DFF',
  moon: '#F5EFE0',
};

const FONT_DISPLAY = `${archivoBlack}, system-ui, sans-serif`;
const FONT_SERIF = `${cormorant}, Georgia, serif`;
const FONT_SERIF_ITALIC = `${cormorantItalic}, Georgia, serif`;
const FONT_SANS = `${inter}, system-ui, sans-serif`;

const Background: React.FC = () => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(circle at 20% 12%, rgba(138,77,255,0.5) 0%, transparent 45%),
                   radial-gradient(circle at 85% 28%, rgba(255,77,141,0.5) 0%, transparent 50%),
                   radial-gradient(circle at 60% 95%, rgba(255,200,87,0.30) 0%, transparent 45%),
                   linear-gradient(160deg, #1a0f3a 0%, #14122B 55%, #2a0f3a 100%)`,
    }}
  />
);

// SCENE 1 — HOOK (0-60 frames, 0-2s)
const HookScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: 'clamp' });
  const y = interpolate(frame, [0, 20], [40, 0], { extrapolateRight: 'clamp' });
  const scale = spring({ frame, fps, config: { damping: 14, stiffness: 80 } });

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        padding: 80,
        textAlign: 'center',
      }}
    >
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
        }}
      >
        you wanna
        <br />
        fight your
        <br />
        boss today.
      </div>
      <div
        style={{
          opacity: interpolate(frame, [25, 45], [0, 1], { extrapolateRight: 'clamp' }),
          marginTop: 50,
          fontFamily: FONT_SERIF,
          fontStyle: 'italic',
          fontSize: 56,
          color: COLORS.gold,
          maxWidth: 880,
        }}
      >
        It's Mars □ Jupiter.
      </div>
    </AbsoluteFill>
  );
};

// SIGN SCENE — reused for all 4 signs
const SignScene: React.FC<{
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
          fontFamily: FONT_SERIF,
          fontStyle: 'italic',
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

// CTA SCENE
const CtaScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacity = interpolate(frame, [0, 14], [0, 1], { extrapolateRight: 'clamp' });
  const scale = spring({ frame, fps, config: { damping: 12, stiffness: 90 } });
  const pulse = 1 + 0.04 * Math.sin(frame * 0.25);

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        padding: 80,
        textAlign: 'center',
        opacity,
      }}
    >
      <div
        style={{
          fontFamily: FONT_DISPLAY,
          fontSize: 24,
          letterSpacing: 6,
          color: COLORS.gold,
          textTransform: 'uppercase',
          marginBottom: 30,
        }}
      >
        TAG SOMEONE WHO NEEDS THIS
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
        }}
      >
        save this
        <br />
        before you
        <br />
        text them.
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

// FULL REEL — 10s @ 30fps = 300 frames
export const MarsJupiterReel: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.cosmos }}>
      <Background />
      <Starfield seed={7} width={1080} height={1920} />

      {/* 0-60: Hook (2s) */}
      <Sequence from={0} durationInFrames={60}>
        <HookScene />
      </Sequence>

      {/* 60-105: Aries (1.5s) */}
      <Sequence from={60} durationInFrames={45}>
        <SignScene
          glyph={'♈︎'}
          sign="aries"
          message="Stop drafting the angry email."
          color={COLORS.pink}
        />
      </Sequence>

      {/* 105-150: Cancer (1.5s) */}
      <Sequence from={105} durationInFrames={45}>
        <SignScene
          glyph={'♋︎'}
          sign="cancer"
          message='That "small" argument is not small.'
          color={COLORS.violet}
        />
      </Sequence>

      {/* 150-195: Libra (1.5s) */}
      <Sequence from={150} durationInFrames={45}>
        <SignScene
          glyph={'♎︎'}
          sign="libra"
          message="Don't fold to keep the peace."
          color={COLORS.gold}
        />
      </Sequence>

      {/* 195-240: Capricorn (1.5s) */}
      <Sequence from={195} durationInFrames={45}>
        <SignScene
          glyph={'♑︎'}
          sign="capricorn"
          message="Stay out of the work drama. Reply tomorrow."
          color={COLORS.pink}
        />
      </Sequence>

      {/* 240-300: CTA (2s) */}
      <Sequence from={240} durationInFrames={60}>
        <CtaScene />
      </Sequence>
    </AbsoluteFill>
  );
};
