import React from 'react';
import { AbsoluteFill, Sequence, useCurrentFrame, interpolate } from 'remotion';
import { Starfield } from './Starfield';
import { Background, HookScene, SignScene, CtaScene, COLORS, FONT_DISPLAY, FONT_SERIF, FONT_SERIF_ITALIC, FONT_SANS } from './scenes';

const QuestionScene: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 14], [0, 1], { extrapolateRight: 'clamp' });
  const lift = interpolate(frame, [0, 18], [40, 0], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        padding: 80,
        textAlign: 'center',
        opacity,
        transform: `translateY(${lift}px)`,
      }}
    >
      <div
        style={{
          fontFamily: FONT_SANS,
          fontSize: 24,
          fontWeight: 900,
          letterSpacing: 5,
          color: COLORS.pink,
          textTransform: 'uppercase',
          marginBottom: 32,
        }}
      >
        SATURN ASKS ONE QUESTION
      </div>
      <div
        style={{
          fontFamily: FONT_DISPLAY,
          fontSize: 124,
          lineHeight: 0.98,
          color: COLORS.moon,
          letterSpacing: -2,
          maxWidth: 920,
        }}
      >
        are you
        <br />
        actually
        <br />
        the leader?
      </div>
      <div
        style={{
          marginTop: 40,
          fontFamily: FONT_SERIF_ITALIC,
          fontSize: 56,
          color: COLORS.gold,
          maxWidth: 880,
        }}
      >
        or just the loudest voice in the room?
      </div>
    </AbsoluteFill>
  );
};

// 10s @ 30fps = 300 frames — Aries Sun rebuild Reel
export const AriesSunReel: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.cosmos }}>
      <Background />
      <Starfield seed={23} width={1080} height={1920} />

      <Sequence from={0} durationInFrames={75}>
        <HookScene
          headline={"if you're\nan aries,\nread this."}
          subline={'The next 2 years rebuild you.'}
        />
      </Sequence>

      <Sequence from={75} durationInFrames={60}>
        <SignScene
          glyph={'☉'}
          sign="aries sun"
          message="Saturn-on-Sun. Most identity-defining transit in your chart."
          color={COLORS.gold}
        />
      </Sequence>

      <Sequence from={135} durationInFrames={60}>
        <SignScene
          glyph={'☉'}
          sign="every 29-30 yrs"
          message="It only crosses your Sun twice in a lifetime. This is one of them."
          color={COLORS.pink}
        />
      </Sequence>

      <Sequence from={195} durationInFrames={60}>
        <QuestionScene />
      </Sequence>

      <Sequence from={255} durationInFrames={45}>
        <CtaScene
          label="TAG EVERY ARIES YOU KNOW"
          headline={'save this.\nre-read on\nthe other side.'}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
