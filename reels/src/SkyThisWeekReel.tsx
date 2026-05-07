import React from 'react';
import { AbsoluteFill, Audio, Sequence, staticFile } from 'remotion';
import { Starfield } from './Starfield';
import { Background, HookScene, SignScene, CtaScene, COLORS } from './scenes';

// 10s @ 30fps = 300 frames
export const SkyThisWeekReel: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.cosmos }}>
      <Audio src={staticFile('audio/ambient.wav')} />
      <Background />
      <Starfield seed={53} width={1080} height={1920} />

      <Sequence from={0} durationInFrames={60}>
        <HookScene
          headline={'your week,\nbut only\n4 signs.'}
          subline={'May 11–17. Pluto is the backdrop. Here is who is hit.'}
        />
      </Sequence>

      <Sequence from={60} durationInFrames={45}>
        <SignScene
          glyph={'♓︎'}
          sign="pisces"
          message="Mon: don't make the hard decision."
          color={COLORS.violet}
        />
      </Sequence>

      <Sequence from={105} durationInFrames={45}>
        <SignScene
          glyph={'♉︎'}
          sign="taurus"
          message="Wed: the week's gift falls on you."
          color={COLORS.gold}
        />
      </Sequence>

      <Sequence from={150} durationInFrames={45}>
        <SignScene
          glyph={'♋︎'}
          sign="cancer"
          message="Wed: someone offers you the ease. Say yes faster."
          color={COLORS.pink}
        />
      </Sequence>

      <Sequence from={195} durationInFrames={45}>
        <SignScene
          glyph={'♊︎'}
          sign="gemini"
          message="Fri: your ruler is back. Mind speeds up."
          color={COLORS.gold}
        />
      </Sequence>

      <Sequence from={240} durationInFrames={60}>
        <CtaScene
          label="TAG SOMEONE WHO NEEDS THEIR WEEK"
          headline={'save this\nfor your\nwhole week.'}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
