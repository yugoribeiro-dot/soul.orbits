import React from 'react';
import { AbsoluteFill, Sequence } from 'remotion';
import { Starfield } from './Starfield';
import { Background, HookScene, SignScene, CtaScene, COLORS } from './scenes';

// 10s @ 30fps = 300 frames
export const SaturnAriesReel: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.cosmos }}>
      <Background />
      <Starfield seed={11} width={1080} height={1920} />

      <Sequence from={0} durationInFrames={60}>
        <HookScene
          headline={'Saturn just\nentered\nAries.'}
          subline={'4 signs are about to be rebuilt.'}
        />
      </Sequence>

      <Sequence from={60} durationInFrames={45}>
        <SignScene
          glyph={'♈︎'}
          sign="aries"
          message="Saturn is editing your identity."
          color={COLORS.pink}
        />
      </Sequence>

      <Sequence from={105} durationInFrames={45}>
        <SignScene
          glyph={'♋︎'}
          sign="cancer"
          message="Saturn is rewriting your career."
          color={COLORS.violet}
        />
      </Sequence>

      <Sequence from={150} durationInFrames={45}>
        <SignScene
          glyph={'♎︎'}
          sign="libra"
          message="Saturn is editing your relationships."
          color={COLORS.gold}
        />
      </Sequence>

      <Sequence from={195} durationInFrames={45}>
        <SignScene
          glyph={'♑︎'}
          sign="capricorn"
          message="Saturn is burning your comfort zone."
          color={COLORS.pink}
        />
      </Sequence>

      <Sequence from={240} durationInFrames={60}>
        <CtaScene
          label="TAG AN ARIES, CANCER, LIBRA, CAPRICORN"
          headline={'save this.\nre-read in\n2028.'}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
