import React from 'react';
import { Composition } from 'remotion';
import { MarsJupiterReel } from './MarsJupiterReel';
import { SaturnAriesReel } from './SaturnAriesReel';
import { AriesSunReel } from './AriesSunReel';
import { PlutoRetrogradeReel } from './PlutoRetrogradeReel';
import { SaturnQuoteReel } from './SaturnQuoteReel';
import { SkyThisWeekReel } from './SkyThisWeekReel';
import { PovEclipseSampleReel } from './PovEclipseSampleReel';
import { ReadYourSignReel } from './ReadYourSignReel';

const sharedProps = {
  durationInFrames: 300,
  fps: 30,
  width: 1080,
  height: 1920,
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="MarsJupiter" component={MarsJupiterReel} {...sharedProps} />
      <Composition id="SaturnAries" component={SaturnAriesReel} {...sharedProps} />
      <Composition id="AriesSun" component={AriesSunReel} {...sharedProps} />
      <Composition id="PlutoRetrograde" component={PlutoRetrogradeReel} {...sharedProps} />
      <Composition id="SaturnQuote" component={SaturnQuoteReel} {...sharedProps} />
      <Composition id="SkyThisWeek" component={SkyThisWeekReel} {...sharedProps} />
      <Composition id="PovEclipseSample" component={PovEclipseSampleReel} {...sharedProps} />
      <Composition id="ReadYourSign" component={ReadYourSignReel} {...sharedProps} />
    </>
  );
};
