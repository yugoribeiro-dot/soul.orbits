import React from 'react';
import { AbsoluteFill, Audio, Sequence, staticFile } from 'remotion';
import { Starfield } from './Starfield';
import { Background, HookScene, PovScene, SignScene, CtaScene, COLORS } from './scenes';

// 10s @ 30fps = 300 frames — sample of the new POV format with upgraded visuals.
export const PovEclipseSampleReel: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.cosmos }}>
      <Audio src={staticFile('audio/ambient.wav')} />
      <Background animate />
      <Starfield seed={61} width={1080} height={1920} />

      {/* 0-72: POV intro */}
      <Sequence from={0} durationInFrames={72}>
        <PovScene
          pov="POV"
          body={'you woke up\nand everything\nfeels off.'}
          closer="Mercury just stationed retrograde."
        />
      </Sequence>

      {/* 72-132: Sign callout 1 — Gemini (Mercury home) */}
      <Sequence from={72} durationInFrames={60}>
        <SignScene
          glyph={'♊︎'}
          sign="gemini"
          message="Your phone is going to betray you this week."
          color={COLORS.gold}
        />
      </Sequence>

      {/* 132-192: Sign callout 2 — Virgo (also Mercury-ruled) */}
      <Sequence from={132} durationInFrames={60}>
        <SignScene
          glyph={'♍︎'}
          sign="virgo"
          message="The plan you spent 3 weeks on. Re-read it."
          color={COLORS.violet}
        />
      </Sequence>

      {/* 192-252: HookScene with zoom-punch on a keyword */}
      <Sequence from={192} durationInFrames={60}>
        <HookScene
          headline={"don't sign\nanything\nuntil June."}
          subline="Mercury Rx ends June 3."
          punch="anything"
        />
      </Sequence>

      {/* 252-300: CTA with zoom-punch on "save" */}
      <Sequence from={252} durationInFrames={48}>
        <CtaScene
          label="TAG A GEMINI OR VIRGO"
          headline={'save this\nbefore you\nsend it.'}
          punch="save"
        />
      </Sequence>
    </AbsoluteFill>
  );
};
