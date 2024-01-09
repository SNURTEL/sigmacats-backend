import gpxo
import numpy as np
import pandas as pd
from scipy.signal import argrelmin

LOOP_DISTANCE_THRESHOLD = 0.00015
FINISH_DISTANCE_THRESHOLD = 0.00015

NO_LAPS = 3

track = gpxo.Track('track.gpx')

start_point = track.data.head(1)[['latitude (°)', 'longitude (°)']].values.T.squeeze()
end_point = track.data.tail(1)[['latitude (°)', 'longitude (°)']].values.T.squeeze()

# assert track is a loop
assert np.linalg.norm(start_point - end_point) <= LOOP_DISTANCE_THRESHOLD

recording = gpxo.Track('test_recording.gpx')
recording.elevation = np.zeros(recording.latitude.shape)
recording.smooth(n=15)

df = recording.data

# calculate distance to track end point
dist = df.apply(lambda r: np.linalg.norm(np.array([r['latitude (°)'], r['longitude (°)']]) - end_point), axis='columns')
# find points locally closest to track end
indices = argrelmin(dist.values, order=5)[0]

assert len(indices) >= 2

merged = df.merge(dist.rename('dist'), left_index=True, right_index=True, validate='1:1')
peaks = merged.iloc[indices]

# filter out local minima not located near track's end
filtered = peaks.loc[peaks.dist < FINISH_DISTANCE_THRESHOLD]
# get trackpoint closest to end in final lap; use `min` in case recording in app starts with a delay
closest = filtered.iloc[[min(NO_LAPS, len(filtered)-1)]]

assert not closest.empty

merged_with_timestamp = merged.assign(timestamp=merged.index)
# sample neighbouring points to closes, discard one with greatest dist
samples = pd.concat([closest.assign(timestamp=closest.index), merged_with_timestamp.shift(1).loc[closest.index], merged_with_timestamp.shift(-1).loc[closest.index]])
p1, p2 = samples.nsmallest(2, columns='dist')[['latitude (°)', 'longitude (°)']].values
t1, t2 = samples.nsmallest(2, columns='dist')['timestamp']

# analytically find point between p1 and p2 closest to track end
a1 = (p1[1] - p2[1]) / (p1[0] - p2[0] + 1e-12) + 1e-12
b1 = (p1[1] - a1 * p1[0])
a2 = -1 / a1
b2 = end_point[1] - a2 * end_point[0]

xp = (b2 - b1) / (a1 - a2)
yp = a2 * xp + b2
p_interpolated = np.array([xp, yp])

p_first, p_second, t_first, t_second = (p1, p2, t1, t2) if t1 <= t2 else (p2, p1, t2, t1)

print(t1, t2)
print(f"first to p3: {np.linalg.norm(p_first-p_interpolated)}\nsecond to p3: {np.linalg.norm(p_second-p_interpolated)}")

# estimate timestamp for interpolated point
delta_p = np.linalg.norm(p1 - p2)
delta_t = t_second - t_first
t_interpolated = t_first + delta_t * (np.linalg.norm(p_first- p_interpolated) / delta_p)
print(t_interpolated)

pass