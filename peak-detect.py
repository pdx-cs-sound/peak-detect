#!/usr/bin/python3
# Copyright © 2015 Bart Massey

# Peak detector for Guitar Hero style charting.

# Basic algorithm: Use RMS power for finding volume
# level. Use a wide Gaussian window for background power.
# Use a narrow Gaussian window for peak power.

import wave
import audioop
from sys import stdin, argv
from math import sqrt

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
bigWindowWidth = int(frameRate * 0.2)
smallWindowWidth = int(frameRate * 0.02)
assert smallWindowWidth <= bigWindowWidth
halfWindowWidth = bigWindowWidth // 2

# Pad audio out for easier averaging.
monoFrames = [0]*halfWindowWidth + monoFrames + [0]*halfWindowWidth

# Apply windows everywhere looking for RMS peaks.
for fi in range(halfWindowWidth, nFrames - halfWindowWidth):
    def calcPower(windowWidth):
        t = 0
        ww = windowWidth // 2
        for wi in range(fi - ww, fi + ww):
            t += monoFrames[wi]**2
        return sqrt(t) / windowWidth

    widePower = calcPower(bigWindowWidth)
    narrowPower = calcPower(smallWindowWidth)
    if widePower > 0 and narrowPower >= 5 * widePower:
        print(fi / frameRate, narrowPower / widePower)
