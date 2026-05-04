import React from 'react';
import { Composition } from 'remotion';
import { MarsJupiterReel } from './MarsJupiterReel';
import { SaturnAriesReel } from './SaturnAriesReel';
import { AriesSunReel } from './AriesSunReel';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MarsJupiter"
        component={MarsJupiterReel}
        durationInFrames={300}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="SaturnAries"
        component={SaturnAriesReel}
        durationInFrames={300}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="AriesSun"
        component={AriesSunReel}
        durationInFrames={300}
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};
