#!/usr/bin/python3
# Copyright © 2015 Bart Massey

# Peak detector for Guitar Hero style charting.

# Basic algorithm: Use RMS power for finding volume
# level. Use a wide Gaussian window for background power.
# Use a narrow Gaussian window for peak power.

import wave
import audioop
from sys import stdin, argv

# Read the file and remember info about it.
waveRead = wave.open(argv[1], 'rb')
nFrames = waveRead.getnframes()
nChannels = waveRead.getnchannels()
bytesPerSample = waveRead.getsampwidth()
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

# Find and display min and max samples.
minSample = monoFrames[0]
maxSample = monoFrames[0]
for sample in monoFrames:
    minSample = min(sample, minSample)
    maxSample = max(sample, maxSample)
print(minSample, maxSample)
