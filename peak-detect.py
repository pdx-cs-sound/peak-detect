#!/usr/bin/python3
# Copyright (c) 2015 Bart and Ben Massey
# [This program is licensed under the GPL version 3 or later.]
# Please see the file COPYING in the source
# distribution of this software for license terms.

# Peak detector for Guitar Hero style charting.

# Basic algorithm: Use RMS power for finding volume
# level. Use a wide Gaussian window for background power.
# Use a narrow Gaussian window for peak power.

import wave
import audioop
from sys import stdin, argv
from math import sqrt
import numpy as np

# Read the file and remember info about it.
waveRead = wave.open(argv[1], 'rb')
nFrames = waveRead.getnframes()
nChannels = waveRead.getnchannels()
bytesPerSample = waveRead.getsampwidth()
frameRate = waveRead.getframerate()
waveData = waveRead.readframes(nFrames)
waveRead.close()

# Form the audio data into frames.
scale = (1 << (8 * bytesPerSample - 1)) - 1
frames = []
for f in range(nFrames):
    frame = []
    for c in range(nChannels):
        pos = nChannels * f + c
        sample = audioop.getsample(waveData, bytesPerSample, pos)
        frame.append(sample / scale)
    frames.append(frame)

# Average all the channels to get a mono sound.
monoFrames = []
for f in frames:
    t = 0
    for c in f:
        t += c
    monoFrames.append(t / nChannels)

# Calculate parameters for window.
bigWindowWidth = int(frameRate * 0.5)
smallWindowWidth = int(frameRate * 0.05)
assert smallWindowWidth <= bigWindowWidth
halfWindowWidth = bigWindowWidth // 2
stepWidth = int(frameRate * 0.05)
powerRatio = 5

# Pad audio out for easier averaging.
monoFrames = [0]*halfWindowWidth + monoFrames + [0]*halfWindowWidth
monoFrames = np.array(monoFrames)

# Apply windows everywhere looking for RMS peaks.
for fi in range(halfWindowWidth, nFrames - halfWindowWidth, stepWidth):
    def calcPower(windowWidth):
        ww = windowWidth // 2
        t = sum(monoFrames[fi - ww:fi + ww]**2)
        return sqrt(t) / windowWidth

    widePower = calcPower(bigWindowWidth)
    narrowPower = calcPower(smallWindowWidth)
    if widePower > 0 and narrowPower >= powerRatio * widePower:
        secs = (fi - halfWindowWidth) / frameRate
        ratio = narrowPower / widePower
        print("%.3g %.4g" % (secs, ratio))
