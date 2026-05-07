import React from 'react';
import { AbsoluteFill, Audio, Sequence, useCurrentFrame, interpolate, staticFile } from 'remotion';
import { Starfield } from './Starfield';
import { Background, COLORS, FONT_DISPLAY, FONT_SERIF, FONT_SERIF_ITALIC } from './scenes';

// Quote-style Reel: less per-sign, more punchy single statement.
// 10s @ 30fps = 300 frames

const Phase: React.FC<{ children: React.ReactNode; align?: 'top' | 'center' }> = ({
  children,
  align = 'center',
}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 8, 35, 45], [0, 1, 1, 1], { extrapolateRight: 'clamp' });
  const slide = interpolate(frame, [0, 12], [40, 0], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill
      style={{
        justifyContent: align === 'top' ? 'flex-start' : 'center',
        alignItems: 'center',
        padding: 80,
        textAlign: 'center',
        opacity,
        transform: `translateY(${slide}px)`,
        paddingTop: align === 'top' ? 220 : 80,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};

export const SaturnQuoteReel: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.cosmos }}>
      <Audio src={staticFile('audio/ambient.wav')} />
      <Background />
      <Starfield seed={42} width={1080} height={1920} />

      {/* 0-60 (2s): Hook */}
      <Sequence from={0} durationInFrames={60}>
        <Phase>
          <div
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 150,
              lineHeight: 0.95,
              letterSpacing: -3,
              color: COLORS.moon,
              textShadow: '0 6px 30px rgba(0,0,0,0.4)',
            }}
          >
            Saturn{'\n'}doesn't{'\n'}punish.
          </div>
          <div
            style={{
              fontFamily: FONT_SERIF_ITALIC,
              fontSize: 56,
              color: COLORS.gold,
              marginTop: 36,
              fontStyle: 'italic',
              fontWeight: 500,
            }}
          >
            It edits.
          </div>
        </Phase>
      </Sequence>

      {/* 60-130 (2.3s): What it removes */}
      <Sequence from={60} durationInFrames={70}>
        <Phase>
          <div
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 24,
              letterSpacing: 5,
              color: COLORS.pink,
              textTransform: 'uppercase',
              marginBottom: 28,
            }}
          >
            WHAT IT REMOVES
          </div>
          <div
            style={{
              fontFamily: FONT_SERIF,
              fontSize: 72,
              lineHeight: 1.1,
              color: COLORS.moon,
              maxWidth: 920,
            }}
          >
            What isn't load-bearing.
          </div>
          <div
            style={{
              fontFamily: FONT_SERIF_ITALIC,
              fontSize: 38,
              color: COLORS.gold,
              marginTop: 28,
              fontStyle: 'italic',
              maxWidth: 880,
            }}
          >
            The job that drained you. The friendship that flattered you.
          </div>
        </Phase>
      </Sequence>

      {/* 130-200 (2.3s): Why it feels like punishment */}
      <Sequence from={130} durationInFrames={70}>
        <Phase>
          <div
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 24,
              letterSpacing: 5,
              color: COLORS.pink,
              textTransform: 'uppercase',
              marginBottom: 28,
            }}
          >
            WHY IT FEELS HARD
          </div>
          <div
            style={{
              fontFamily: FONT_SERIF,
              fontSize: 72,
              lineHeight: 1.1,
              color: COLORS.moon,
              maxWidth: 920,
            }}
          >
            You liked the thing it took.
          </div>
          <div
            style={{
              fontFamily: FONT_SERIF_ITALIC,
              fontSize: 38,
              color: COLORS.gold,
              marginTop: 28,
              fontStyle: 'italic',
              maxWidth: 880,
            }}
          >
            The grief is real. The edit is correct.
          </div>
        </Phase>
      </Sequence>

      {/* 200-270 (2.3s): What's left */}
      <Sequence from={200} durationInFrames={70}>
        <Phase>
          <div
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 24,
              letterSpacing: 5,
              color: COLORS.gold,
              textTransform: 'uppercase',
              marginBottom: 28,
            }}
          >
            WHAT'S LEFT
          </div>
          <div
            style={{
              fontFamily: FONT_SERIF,
              fontSize: 80,
              lineHeight: 1.1,
              color: COLORS.moon,
              maxWidth: 920,
            }}
          >
            The version of you that can stand alone.
          </div>
        </Phase>
      </Sequence>

      {/* 270-300 (1s): CTA flash */}
      <Sequence from={270} durationInFrames={30}>
        <Phase>
          <div
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 110,
              lineHeight: 1.0,
              letterSpacing: -2,
              color: COLORS.moon,
            }}
          >
            send to
            <br />
            someone in their
            <br />
            saturn return.
          </div>
          <div
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 40,
              letterSpacing: 4,
              color: COLORS.moon,
              textTransform: 'lowercase',
              marginTop: 36,
            }}
          >
            <span style={{ color: COLORS.pink }}>@</span>soul
            <span style={{ color: COLORS.pink }}>.</span>orbits
          </div>
        </Phase>
      </Sequence>
    </AbsoluteFill>
  );
};
