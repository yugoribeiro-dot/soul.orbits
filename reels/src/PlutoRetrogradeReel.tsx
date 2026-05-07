import React from 'react';
import { AbsoluteFill, Audio, Sequence, staticFile } from 'remotion';
import { Starfield } from './Starfield';
import { Background, HookScene, SignScene, CtaScene, COLORS } from './scenes';

// 10s @ 30fps = 300 frames
export const PlutoRetrogradeReel: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.cosmos }}>
      <Audio src={staticFile('audio/ambient.wav')} />
      <Background />
      <Starfield seed={31} width={1080} height={1920} />

      <Sequence from={0} durationInFrames={60}>
        <HookScene
          headline={'Pluto just\nwent\nbackwards.'}
          subline={'5 months of secrets coming up.'}
        />
      </Sequence>

      <Sequence from={60} durationInFrames={45}>
        <SignScene
          glyph={'♏︎'}
          sign="scorpio"
          message="Your ruler points the spotlight at you."
          color={COLORS.violet}
        />
      </Sequence>

      <Sequence from={105} durationInFrames={45}>
        <SignScene
          glyph={'♈︎'}
          sign="aries"
          message="The fight you keep picking is with yourself."
          color={COLORS.pink}
        />
      </Sequence>

      <Sequence from={150} durationInFrames={45}>
        <SignScene
          glyph={'♋︎'}
          sign="cancer"
          message="A family truth is about to surface."
          color={COLORS.gold}
        />
      </Sequence>

      <Sequence from={195} durationInFrames={45}>
        <SignScene
          glyph={'♑︎'}
          sign="capricorn"
          message="Power dynamics you ignored get loud."
          color={COLORS.violet}
        />
      </Sequence>

      <Sequence from={240} durationInFrames={60}>
        <CtaScene
          label="TAG SOMEONE WHO NEEDS THIS"
          headline={'save this.\nre-read in\noctober.'}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
