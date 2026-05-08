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

// ─────────────────────────────────────────────────────────────────────────────
// Animation utilities
// ─────────────────────────────────────────────────────────────────────────────

/** Reveal text character-by-character. Returns the substring visible at frame. */
export function useTypeOn(text: string, startFrame: number, charsPerSecond = 24) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const elapsed = Math.max(0, frame - startFrame);
  const cps = charsPerSecond / fps;
  const visible = Math.min(text.length, Math.floor(elapsed * cps));
  return text.slice(0, visible);
}

/** Camera shake — small XY offset that decays from peak frame. */
export function useShake(peakFrame: number, intensity = 14, decay = 12) {
  const frame = useCurrentFrame();
  const t = frame - peakFrame;
  if (t < 0 || t > decay) return { x: 0, y: 0 };
  const fall = 1 - t / decay;
  const x = Math.sin(t * 1.7) * intensity * fall;
  const y = Math.cos(t * 2.1) * intensity * fall;
  return { x, y };
}

/** Zoom punch on a single keyword — scale spikes and falls. */
export function useZoomPunch(peakFrame: number, peakScale = 1.18, decay = 14) {
  const frame = useCurrentFrame();
  const t = frame - peakFrame;
  if (t < 0) return 0.92;
  if (t > decay) return 1;
  // ease-out-back-ish
  const k = t / decay;
  return 1 + (peakScale - 1) * (1 - k) ** 2;
}

/** Pulsing glow scalar — oscillates 0..1, useful for dynamic shadow. */
export function usePulse(speed = 0.18) {
  const frame = useCurrentFrame();
  return 0.5 + 0.5 * Math.sin(frame * speed);
}

// ─────────────────────────────────────────────────────────────────────────────
// Background — animated gradient mesh
// ─────────────────────────────────────────────────────────────────────────────

export const Background: React.FC<{ animate?: boolean }> = ({ animate = true }) => {
  const frame = useCurrentFrame();
  const drift = animate ? Math.sin(frame * 0.012) * 8 : 0; // slow gradient sway
  const drift2 = animate ? Math.cos(frame * 0.009) * 6 : 0;
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at ${20 + drift}% ${12 + drift2}%, rgba(138,77,255,0.5) 0%, transparent 45%),
                     radial-gradient(circle at ${85 - drift}% ${28 + drift2}%, rgba(255,77,141,0.5) 0%, transparent 50%),
                     radial-gradient(circle at ${60 + drift2}% ${95 - drift}%, rgba(255,200,87,0.30) 0%, transparent 45%),
                     linear-gradient(160deg, #1a0f3a 0%, #14122B 55%, #2a0f3a 100%)`,
      }}
    />
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// HookScene — bouncy entrance, settle shake, optional zoom-punch on a keyword
// ─────────────────────────────────────────────────────────────────────────────

export const HookScene: React.FC<{
  headline: string;
  subline: string;
  /** Optional: a substring of headline that gets a zoom-punch when settled. */
  punch?: string;
}> = ({ headline, subline, punch }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // headline drops in with spring bounce
  const dropIn = spring({ frame, fps, config: { damping: 11, stiffness: 110 }, durationInFrames: 22 });
  const opacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: 'clamp' });
  const y = interpolate(dropIn, [0, 1], [-60, 0]);
  const scale = interpolate(dropIn, [0, 1], [0.85, 1]);

  // shake on landing (frame ~22 when settle finishes)
  const shake = useShake(22, 10, 14);

  // subline fades in after headline lands
  const subOpacity = interpolate(frame, [28, 48], [0, 1], { extrapolateRight: 'clamp' });
  const subY = interpolate(frame, [28, 48], [20, 0], { extrapolateRight: 'clamp' });

  // optional zoom-punch on keyword at frame 38
  const punchScale = useZoomPunch(38, 1.18, 14);

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', padding: 80, textAlign: 'center' }}>
      <div
        style={{
          opacity,
          transform: `translate(${shake.x}px, ${y + shake.y}px) scale(${scale})`,
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
        {punch ? renderWithPunch(headline, punch, punchScale) : headline}
      </div>
      <div
        style={{
          opacity: subOpacity,
          transform: `translateY(${subY}px)`,
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

function renderWithPunch(text: string, target: string, scale: number) {
  const idx = text.toLowerCase().indexOf(target.toLowerCase());
  if (idx < 0) return text;
  const before = text.slice(0, idx);
  const match = text.slice(idx, idx + target.length);
  const after = text.slice(idx + target.length);
  return (
    <>
      {before}
      <span
        style={{
          display: 'inline-block',
          transform: `scale(${scale})`,
          transformOrigin: 'center',
          color: COLORS.gold,
        }}
      >
        {match}
      </span>
      {after}
    </>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// SignScene — glyph with rotating glow ring, type-on message, subtle shake on entry
// ─────────────────────────────────────────────────────────────────────────────

export const SignScene: React.FC<{
  glyph: string;
  sign: string;
  message: string;
  color: string;
}> = ({ glyph, sign, message, color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({ frame, fps, config: { damping: 13, stiffness: 100 }, durationInFrames: 18 });
  const opacity = interpolate(frame, [0, 7], [0, 1], { extrapolateRight: 'clamp' });
  const slide = interpolate(enter, [0, 1], [40, 0]);
  const glyphScale = interpolate(enter, [0, 1], [0.6, 1]);
  const glyphRot = (frame % 360) * 0.15; // very slow rotation
  const pulse = usePulse(0.16);

  // type-on the message (24 cps)
  const typed = useTypeOn(message, 12, 28);

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
      {/* glow ring behind glyph */}
      <div style={{ position: 'relative', marginBottom: 24 }}>
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            width: 360,
            height: 360,
            transform: `translate(-50%, -50%) rotate(${glyphRot}deg)`,
            background: `conic-gradient(from 0deg, ${color}00, ${color}66, ${color}00, ${color}33, ${color}00)`,
            borderRadius: '50%',
            filter: `blur(${20 + 14 * pulse}px)`,
            opacity: 0.55 + 0.35 * pulse,
          }}
        />
        <div
          style={{
            position: 'relative',
            fontFamily: FONT_SERIF,
            fontSize: 220,
            color,
            textShadow: `0 0 ${40 + 30 * pulse}px ${color}aa, 0 0 80px ${color}55`,
            lineHeight: 1,
            transform: `scale(${glyphScale})`,
          }}
        >
          {glyph}
        </div>
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
          minHeight: 160, // reserve space so layout doesn't reflow as we type
        }}
      >
        {typed}
        {typed.length < message.length && (
          <span style={{ opacity: 0.5 + 0.5 * pulse }}>|</span>
        )}
      </div>
    </AbsoluteFill>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// POVScene — direct second-person hook (e.g. "POV: you're an Aries and...")
// ─────────────────────────────────────────────────────────────────────────────

export const PovScene: React.FC<{
  pov: string; // top-line "POV:" badge text
  body: string; // main statement
  closer?: string; // small italic closer
}> = ({ pov, body, closer }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 12, stiffness: 95 }, durationInFrames: 18 });
  const badgeScale = interpolate(enter, [0, 1], [0.5, 1]);
  const badgeRot = interpolate(enter, [0, 1], [-8, 0]);
  const bodyOpacity = interpolate(frame, [10, 28], [0, 1], { extrapolateRight: 'clamp' });
  const bodyY = interpolate(frame, [10, 28], [30, 0], { extrapolateRight: 'clamp' });
  const closerOpacity = interpolate(frame, [40, 60], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', padding: 80, textAlign: 'center' }}>
      <div
        style={{
          fontFamily: FONT_DISPLAY,
          fontSize: 38,
          letterSpacing: 6,
          background: COLORS.gold,
          color: COLORS.cosmos,
          textTransform: 'uppercase',
          padding: '14px 30px 10px',
          borderRadius: 999,
          marginBottom: 50,
          transform: `scale(${badgeScale}) rotate(${badgeRot}deg)`,
          boxShadow: `0 10px 40px ${COLORS.gold}55`,
        }}
      >
        {pov}
      </div>
      <div
        style={{
          opacity: bodyOpacity,
          transform: `translateY(${bodyY}px)`,
          fontFamily: FONT_DISPLAY,
          fontSize: 130,
          lineHeight: 0.95,
          color: COLORS.moon,
          letterSpacing: -2,
          textShadow: '0 6px 30px rgba(0,0,0,0.5)',
          maxWidth: 940,
          whiteSpace: 'pre-line',
        }}
      >
        {body}
      </div>
      {closer && (
        <div
          style={{
            opacity: closerOpacity,
            marginTop: 40,
            fontFamily: FONT_SERIF_ITALIC,
            fontSize: 52,
            color: COLORS.gold,
            maxWidth: 880,
          }}
        >
          {closer}
        </div>
      )}
    </AbsoluteFill>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// ProgressBar — for "read your sign" tap-through format
// ─────────────────────────────────────────────────────────────────────────────

export const ProgressBar: React.FC<{ steps: number; current: number }> = ({ steps, current }) => {
  return (
    <div style={{ display: 'flex', gap: 12, justifyContent: 'center', width: '100%' }}>
      {Array.from({ length: steps }).map((_, i) => (
        <div
          key={i}
          style={{
            flex: 1,
            height: 6,
            borderRadius: 3,
            background: i < current ? COLORS.gold : 'rgba(245,239,224,0.18)',
            boxShadow: i < current ? `0 0 12px ${COLORS.gold}88` : undefined,
            transition: 'background 0.3s',
          }}
        />
      ))}
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// CtaScene — punchy CTA with pulse + zoom-punch on "save" or whatever keyword
// ─────────────────────────────────────────────────────────────────────────────

export const CtaScene: React.FC<{ label?: string; headline: string; punch?: string }> = ({
  label = 'TAG SOMEONE WHO NEEDS THIS',
  headline,
  punch = 'save',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacity = interpolate(frame, [0, 14], [0, 1], { extrapolateRight: 'clamp' });
  const enter = spring({ frame, fps, config: { damping: 12, stiffness: 90 }, durationInFrames: 18 });
  const scale = interpolate(enter, [0, 1], [0.85, 1]);
  const pulse = 1 + 0.04 * Math.sin(frame * 0.25);
  const punchScale = useZoomPunch(20, 1.22, 14);

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
          transform: `scale(${scale})`,
          marginBottom: 60,
          whiteSpace: 'pre-line',
        }}
      >
        {punch ? renderWithPunch(headline, punch, punchScale) : headline}
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
