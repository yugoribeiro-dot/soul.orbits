import React from 'react';
import { Composition } from 'remotion';
import { MarsJupiterReel } from './MarsJupiterReel';

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
    </>
  );
};
