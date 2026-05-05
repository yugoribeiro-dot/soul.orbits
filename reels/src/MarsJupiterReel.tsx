import React from 'react';
import { AbsoluteFill, Audio, Sequence, staticFile } from 'remotion';
import { Starfield } from './Starfield';
import { Background, HookScene, SignScene, CtaScene, COLORS } from './scenes';

// 10s @ 30fps = 300 frames
export const MarsJupiterReel: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.cosmos }}>
      <Audio src={staticFile('audio/ambient.wav')} />
      <Background />
      <Starfield seed={7} width={1080} height={1920} />

      <Sequence from={0} durationInFrames={60}>
        <HookScene
          headline={'you wanna\nfight your\nboss today.'}
          subline={"It's Mars □ Jupiter."}
        />
      </Sequence>

      <Sequence from={60} durationInFrames={45}>
        <SignScene
          glyph={'♈︎'}
          sign="aries"
          message="Stop drafting the angry email."
          color={COLORS.pink}
        />
      </Sequence>

      <Sequence from={105} durationInFrames={45}>
        <SignScene
          glyph={'♋︎'}
          sign="cancer"
          message='That "small" argument is not small.'
          color={COLORS.violet}
        />
      </Sequence>

      <Sequence from={150} durationInFrames={45}>
        <SignScene
          glyph={'♎︎'}
          sign="libra"
          message="Don't fold to keep the peace."
          color={COLORS.gold}
        />
      </Sequence>

      <Sequence from={195} durationInFrames={45}>
        <SignScene
          glyph={'♑︎'}
          sign="capricorn"
          message="Stay out of the work drama. Reply tomorrow."
          color={COLORS.pink}
        />
      </Sequence>

      <Sequence from={240} durationInFrames={60}>
        <CtaScene
          label="TAG SOMEONE WHO NEEDS THIS"
          headline={'save this\nbefore you\ntext them.'}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
