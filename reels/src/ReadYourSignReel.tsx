import React from 'react';
import { AbsoluteFill, Audio, Sequence, useCurrentFrame, interpolate, spring, useVideoConfig, staticFile } from 'remotion';
import { Starfield } from './Starfield';
import {
  Background, COLORS, FONT_DISPLAY, FONT_SERIF, FONT_SERIF_ITALIC, FONT_SANS,
  ProgressBar, useTypeOn, usePulse,
} from './scenes';

// ─────────────────────────────────────────────────────────────────────────────
// "Read your sign" tap-through format
//
// 10s = 300 frames. 1 hook (60f, 2s) + 8 quick sign cards (24f each, 0.8s) +
// 1 CTA (48f, 1.6s).
//
// Each sign card has a progress bar at top and the sign's one-line message
// type-on. Faster pacing → user "reads through" their sign as it scrolls.
// ─────────────────────────────────────────────────────────────────────────────

type SignBeat = {
  glyph: string;
  sign: string;
  message: string;
  color: string;
};

const HOOK_FRAMES = 60;
const PER_SIGN = 24;
const CTA_FRAMES = 48;

const SIGNS: SignBeat[] = [
  { glyph: '♈︎', sign: 'aries', message: 'Stop drafting that text.', color: COLORS.pink },
  { glyph: '♉︎', sign: 'taurus', message: "Don't move money this week.", color: COLORS.gold },
  { glyph: '♊︎', sign: 'gemini', message: 'Your phone will betray you.', color: COLORS.violet },
  { glyph: '♋︎', sign: 'cancer', message: 'A family truth surfaces.', color: COLORS.pink },
  { glyph: '♌︎', sign: 'leo', message: "Your name is in the room.", color: COLORS.gold },
  { glyph: '♍︎', sign: 'virgo', message: 'Re-read what you spent 3 weeks on.', color: COLORS.violet },
  { glyph: '♎︎', sign: 'libra', message: "Don't fold to keep the peace.", color: COLORS.gold },
  { glyph: '♏︎', sign: 'scorpio', message: 'The pattern ends here.', color: COLORS.pink },
];

const HookCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 12, stiffness: 100 }, durationInFrames: 18 });
  const y = interpolate(enter, [0, 1], [-40, 0]);
  const scale = interpolate(enter, [0, 1], [0.85, 1]);
  const subOpacity = interpolate(frame, [22, 42], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', padding: 80, textAlign: 'center' }}>
      <div
        style={{
          fontFamily: FONT_SANS,
          fontSize: 26,
          fontWeight: 900,
          letterSpacing: 6,
          color: COLORS.gold,
          textTransform: 'uppercase',
          marginBottom: 36,
        }}
      >
        READ YOUR SIGN ↓
      </div>
      <div
        style={{
          fontFamily: FONT_DISPLAY,
          fontSize: 150,
          lineHeight: 0.95,
          color: COLORS.moon,
          letterSpacing: -3,
          transform: `translateY(${y}px) scale(${scale})`,
          textShadow: '0 8px 40px rgba(0,0,0,0.5)',
          maxWidth: 940,
        }}
      >
        Mercury{'\n'}Rx hits{'\n'}every sign.
      </div>
      <div
        style={{
          opacity: subOpacity,
          marginTop: 40,
          fontFamily: FONT_SERIF_ITALIC,
          fontSize: 52,
          color: COLORS.gold,
          maxWidth: 880,
        }}
      >
        find yours.
      </div>
    </AbsoluteFill>
  );
};

const SignCard: React.FC<{ beat: SignBeat; index: number; total: number }> = ({ beat, index, total }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 14, stiffness: 130 }, durationInFrames: 8 });
  const x = interpolate(enter, [0, 1], [120, 0]);
  const opacity = interpolate(frame, [0, 4], [0, 1], { extrapolateRight: 'clamp' });
  const typed = useTypeOn(beat.message, 4, 60); // fast type-on
  const pulse = usePulse(0.2);

  return (
    <AbsoluteFill style={{ padding: '120px 80px', display: 'flex', flexDirection: 'column' }}>
      {/* Progress at top */}
      <div style={{ marginBottom: 80, opacity: 0.95 }}>
        <ProgressBar steps={total} current={index + 1} />
      </div>

      <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 50, opacity, transform: `translateX(${x}px)` }}>
        {/* Glyph block — larger left */}
        <div style={{ position: 'relative', width: 360, height: 360, flexShrink: 0 }}>
          <div
            style={{
              position: 'absolute', inset: 0,
              background: `radial-gradient(circle at 50% 50%, ${beat.color}55, transparent 60%)`,
              filter: `blur(${20 + 10 * pulse}px)`,
            }}
          />
          <div
            style={{
              position: 'relative', width: '100%', height: '100%',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: FONT_SERIF,
              fontSize: 280,
              color: beat.color,
              textShadow: `0 0 ${50 + 30 * pulse}px ${beat.color}cc`,
              lineHeight: 1,
            }}
          >
            {beat.glyph}
          </div>
        </div>

        {/* Right column: sign name + message */}
        <div style={{ flex: 1, textAlign: 'left' }}>
          <div
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 70,
              color: COLORS.moon,
              textTransform: 'lowercase',
              letterSpacing: -1,
              marginBottom: 24,
            }}
          >
            {beat.sign}
          </div>
          <div
            style={{
              fontFamily: FONT_SERIF_ITALIC,
              fontSize: 56,
              lineHeight: 1.1,
              color: COLORS.moon,
              minHeight: 140,
            }}
          >
            {typed}
            {typed.length < beat.message.length && <span style={{ opacity: 0.4 + 0.6 * pulse }}>|</span>}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const CtaCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 12, stiffness: 95 }, durationInFrames: 14 });
  const scale = interpolate(enter, [0, 1], [0.85, 1]);
  const pulse = 1 + 0.04 * Math.sin(frame * 0.25);

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', padding: 80, textAlign: 'center' }}>
      <div
        style={{
          fontFamily: FONT_SANS, fontSize: 24, fontWeight: 900, letterSpacing: 6,
          color: COLORS.gold, textTransform: 'uppercase', marginBottom: 28,
        }}
      >
        COMMENT YOUR SIGN ↓
      </div>
      <div
        style={{
          fontFamily: FONT_DISPLAY,
          fontSize: 130,
          lineHeight: 0.95,
          color: COLORS.moon,
          letterSpacing: -2,
          transform: `scale(${scale})`,
          marginBottom: 50,
          whiteSpace: 'pre-line',
        }}
      >
        which one{'\n'}was you?
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

export const ReadYourSignReel: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.cosmos }}>
      <Audio src={staticFile('audio/ambient.wav')} />
      <Background animate />
      <Starfield seed={73} width={1080} height={1920} />

      <Sequence from={0} durationInFrames={HOOK_FRAMES}>
        <HookCard />
      </Sequence>

      {SIGNS.map((beat, i) => (
        <Sequence
          key={beat.sign}
          from={HOOK_FRAMES + i * PER_SIGN}
          durationInFrames={PER_SIGN}
        >
          <SignCard beat={beat} index={i} total={SIGNS.length} />
        </Sequence>
      ))}

      <Sequence from={HOOK_FRAMES + SIGNS.length * PER_SIGN} durationInFrames={CTA_FRAMES}>
        <CtaCard />
      </Sequence>
    </AbsoluteFill>
  );
};
