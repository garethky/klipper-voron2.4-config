import numpy as np
import math
import json

# Load probe data from JSON file
sample_probes = None
with open('sample_probes.json', 'r') as f:
    sample_probes = json.loads(f.read())


# point on a time/force graph
class ForcePoint(object):
    def __init__(self, time, force):
        self.time = time
        self.force = force

    def to_dict(self):
        return {'time': self.time, 'force': self.force}

# slope/intercept based line where x is time and y is force
class ForceLine(object):
    def __init__(self, slope, intercept):
        self.slope = float(slope)
        self.intercept = float(intercept)

    # measure angles between lines at the 1g == 1ms scale
    # returns +/- 0-180. Positive values represent clockwise rotation
    def angle(self, line, time_scale=0.001):
        radians = (math.atan2(self.slope * time_scale, 1) -
                   math.atan2(line.slope * time_scale, 1))
        return math.degrees(radians)

    def find_force(self, time):
        return self.slope * time + self.intercept

    def find_time(self, force):
        return (force - self.intercept) / self.slope

    def intersection(self, line):
        numerator = -self.intercept + line.intercept
        denominator = self.slope - line.slope
        # lines are parallel, will not intersect
        if denominator == 0.:
            # to get debuggable data we want to return a clearly bad value here
            return ForcePoint(0., 0.)
        intersection_time = numerator / denominator
        intersection_force = self.find_force(intersection_time)
        return ForcePoint(intersection_time, intersection_force)

    def to_dict(self):
        return {'slope': self.slope, 'intercept': self.intercept}

# slope/intercept based line where x is time and y is force
class ForceGraph:
    def __init__(self, time, force):
        import numpy as np
        self.time = time
        self.force = force
        # prepare arrays for numpy to save re-allocation costs
        self.time_float32 = np.asarray(time, dtype=np.float32)
        ones = np.ones(len(time), dtype=np.float32)
        self.time_nd = np.vstack([self.time_float32, ones]).T
        self.force_nd = np.asarray(force, dtype=np.float32)

    # Least Squares on x[] y[] points, returns ForceLine
    def _lstsq_line(self, x_stacked, y):
        import numpy as np
        mx, b = np.linalg.lstsq(x_stacked, y, rcond=None)[0]
        return mx, b

    # returns the residual sum for a best fit line
    def _lstsq_error(self, x_stacked, y):
        import numpy as np
        residuals = np.linalg.lstsq(x_stacked, y, rcond=None)[1]
        return residuals[0] if residuals.size > 0 else 0

    # split a chunk of the graph in to 2 lines at i and return the residual sum
    def _two_lines_error(self, time, force, i):
        r1 = self._lstsq_error(time[0:i], force[0:i])
        r2 = self._lstsq_error(time[i:], force[i:])
        return r1 + r2

    # search exhaustively for the 2 lines that best fit the data
    # return the elbow index
    def _two_lines_best_fit(self, time, force):
        best_error = float('inf')
        best_fit_index = -1
        for i in range(1, len(force) - 2):
            #error = self._two_lines_error(time, force, i)
            r1 = np.linalg.lstsq(time[0:i], force[0:i], rcond=None)[1]
            r2 = np.linalg.lstsq(time[i:], force[i:], rcond=None)[1]
            error = (r1[0] if r1.size > 0 else 0) + (r2[0] if r2.size > 0 else 0)
            if error < best_error:
                best_error = error
                best_fit_index = i
        return best_fit_index
    
    def _two_lines_best_fit_gpt(self, time, force):
        n = len(force)
        time = np.asarray(time)
        force = np.asarray(force)

        # Precompute cumulative sums
        Sx = np.cumsum(time)
        Sy = np.cumsum(force)
        Sxx = np.cumsum(time ** 2)
        Sxy = np.cumsum(time * force)
        Syy = np.cumsum(force ** 2)  # New: precompute sum of squares of force

        def linear_fit_error(start, end):
            """Compute sum of squared errors (SSE) for least-squares line between start and end."""
            n = end - start
            if n < 2:
                return float('inf')  # Invalid segment
            
            # Compute segment sums
            sx = Sx[end - 1] - (Sx[start - 1] if start > 0 else 0)
            sy = Sy[end - 1] - (Sy[start - 1] if start > 0 else 0)
            sxx = Sxx[end - 1] - (Sxx[start - 1] if start > 0 else 0)
            sxy = Sxy[end - 1] - (Sxy[start - 1] if start > 0 else 0)
            syy = Syy[end - 1] - (Syy[start - 1] if start > 0 else 0)

            # Compute slope and intercept
            denom = (n * sxx - sx ** 2)
            if abs(denom) < 1e-10:
                return float('inf')  # Avoid division by zero
            
            slope = (n * sxy - sx * sy) / denom
            intercept = (sy - slope * sx) / n

            # Compute SSE directly
            return syy - 2 * slope * sxy + slope ** 2 * sxx

        # Search for the best breakpoint
        best_error = float('inf')
        best_fit_index = -1
        for i in range(2, n - 2):  # Ensure valid split
            error = linear_fit_error(0, i) + linear_fit_error(i, n)
            if error < best_error:
                best_error = error
                best_fit_index = i

        return best_fit_index

    # slice the internal nd arrays with optional discards
    def _slice_nd(self, start_idx, end_idx, discard_left=0, discard_right=0):
        t = self.time_nd[start_idx + discard_left:end_idx - discard_right]
        f = self.force_nd[start_idx + discard_left:end_idx - discard_right]
        return t, f

    def find_elbow(self, start_idx, end_idx):
        #t, f = self._slice_nd(start_idx, end_idx)
        #elbow_index = self._two_lines_best_fit(t, f)
        elbow_index = self._two_lines_best_fit_gpt(self.time_float32[start_idx:end_idx], self.force_nd[start_idx:end_idx])
        return start_idx + elbow_index

    def index_near(self, instant):
        import numpy as np
        return int(np.searchsorted(self.time_float32, instant) - 1)

    # construct a line from 2 points
    def _points_to_line(self, a, b):
        import numpy as np
        t = np.asarray([[a.time, 1], [b.time, 1]], dtype=np.float32)
        f = np.asarray([a.force, b.force], dtype=np.float32)
        mx, b = self._lstsq_line(t, f)
        return ForceLine(mx, b)

    # construct a line using a subset of the graph
    def line(self, start_idx, end_idx, discard_left=0, discard_right=0):
        t, f = self._slice_nd(start_idx, end_idx, discard_left, discard_right)
        mx, b = self._lstsq_line(t, f)
        return ForceLine(mx, b)

    # given a line and a range, calculate the standard deviation of the noise
    def noise_std(self, start_idx, end_idx, line):
        import numpy as np
        f = self.force_nd[start_idx:end_idx]
        t = self.time_float32[start_idx:end_idx]
        noise = []
        for i in range(len(f)):
            noise.append(f[i] - line.find_force(t[i]))
        return np.std(noise, dtype=np.float32)

    # true if the reference force won't be confused for noise in the graph chunk
    # reference force must be more than 3 standard deviations away from the line
    # at the reference index
    def is_clear_signal(self, start_idx, end_idx, line, reference_idx, force_idx):
        import numpy as np
        noise = self.noise_std(start_idx, end_idx, line)
        noise_3_std = noise * 2
        base_force = line.find_force(self.time[reference_idx])
        return abs(base_force - self.force[force_idx]) > noise_3_std

    # return the first index that exceeds the median force between start and end:
    def _split_by_force(self, start_idx, end_idx):
        import numpy as np
        start_f = self.force_nd[start_idx]
        end_f = self.force_nd[end_idx]
        median_f = np.median([start_f, end_f])
        scan = range(start_idx, end_idx)
        # if force is ascending, swap the scan direction
        if start_f > end_f:
            scan = reversed(scan)
        for i in scan:
            if self.force[i] > median_f:
                return i
        return end_idx

    # break a tap event down into 6 points and 5 lines:
    #    *-----*|       /*-----*
    #           |      /
    #           *----*/
    def tap_decompose(self, homing_end_time, pullback_start_time,
                      pullback_cruise_time, pullback_cruise_duration,
                      discard=0):
        homing_end_idx = self.index_near(homing_end_time)
        # use the pullback duration to trim the amount of approach data used
        homing_start_time = homing_end_time - (2 * pullback_cruise_duration)
        homing_start_idx = self.index_near(homing_start_time)
        # locate the point where the probe made contact with the bed
        contact_elbow_idx = self.find_elbow(homing_start_idx, homing_end_idx)

        pullback_start_idx = self.index_near(pullback_start_time)
        pullback_cruise_idx = self.index_near(pullback_cruise_time)
        # limit use of additional data after the pullback move ends
        pullback_end_idx = self.index_near(pullback_cruise_time
                                           + (2 * pullback_cruise_duration))

        # l1 is the approach line
        l1 = self.line(0, contact_elbow_idx, discard, discard)
        # sometime after contact_elbow_idx is the peak force and the start of
        # the dwell line
        dwell_end = self.time[contact_elbow_idx] + (2 * pullback_cruise_duration)
        dwell_end_idx = min(pullback_start_idx, self.index_near(dwell_end))
        dwell_start_idx = self.find_elbow(contact_elbow_idx, dwell_end_idx)
        # l2 is the compression line, it may have very few points so no discard
        l2 = self.line(contact_elbow_idx, dwell_start_idx)
        # l3 is the dwell line
        l3 = self.line(dwell_start_idx, pullback_start_idx, discard, discard)

        # find the elbow where the probe breaks contact on the way back up.
        # This starts from the pullback_cruise_idx to avoid the curve caused
        # by axis acceleration
        break_contact_idx = self.find_elbow(pullback_cruise_idx,
                                            pullback_end_idx)
        l4 = self.line(pullback_cruise_idx, break_contact_idx, discard, discard)
        l5 = self.line(break_contact_idx, -1, discard, discard)

        # Line intersections:
        p0 = ForcePoint(self.time[0],
                        l1.find_force(self.time[0]))
        p1 = l1.intersection(l2)
        p2 = l2.intersection(l3)
        p3 = l3.intersection(l4)
        p4 = l4.intersection(l5)
        p5 = ForcePoint(self.time[-1],
                        l5.find_force(self.time[-1]))
        return [p0, p1, p2, p3, p4, p5], [l1, l2, l3, l4, l5]

    # break a tap event down into 6 points and 5 lines:
    #    *-----*|       /*-----*
    #           |      /
    #           *----*/
    def tap_decompose_better(self, homing_end_time, pullback_start_time,
                             pullback_cruise_time, pullback_cruise_duration,
                             discard=0):
        homing_end_idx = self.index_near(homing_end_time)
        extra_time = pullback_cruise_duration
        # use the pullback duration to trim the amount of approach data used
        homing_start_time = homing_end_time - extra_time
        homing_start_idx =  max(0, self.index_near(homing_start_time))
        # locate the point where the probe made contact with the bed
        contact_elbow_idx = self.find_elbow(homing_start_idx, homing_end_idx)

        pullback_start_idx = self.index_near(pullback_start_time)
        pullback_cruise_idx = self.index_near(pullback_cruise_time)
        # limit use of additional data after the pullback move ends
        pullback_end_time = (pullback_cruise_time + pullback_cruise_duration + (0.25 * pullback_cruise_duration))
        pullback_end_idx = self.index_near(pullback_end_time)

        # l1 is the approach line
        l1 = self.line(homing_start_idx, contact_elbow_idx, discard, discard)
        # sometime after contact_elbow_idx is the peak force and the start of
        # the dwell line
        dwell_end = self.time[contact_elbow_idx] + extra_time
        dwell_end_idx = min(pullback_start_idx, self.index_near(dwell_end))
        dwell_start_idx = self.find_elbow(contact_elbow_idx, dwell_end_idx)
        # l2 is the compression line, it may have very few points so no discard
        # also +1 the last index in case its sequential [1, 2]
        l2 = self.line(contact_elbow_idx, dwell_start_idx + 1)
        # l3 is the dwell line
        l3 = self.line(dwell_start_idx, pullback_start_idx, discard, discard)

        # find the approximate elbow location
        break_contact_idx = self.find_elbow(pullback_cruise_idx,
                                            pullback_end_idx)
        # l5 is the line after decompression ends
        l5 = self.line(break_contact_idx, pullback_end_idx,
                       discard, discard)
        # split the points between the elbow and the start of movement by force
        midpoint_idx = self._split_by_force(pullback_cruise_idx,
                                            break_contact_idx)
        # elbow finding success depends on their being good signal-to-noise:
        clear_dwell = self.is_clear_signal(dwell_start_idx, dwell_end_idx,
                                            l3, dwell_end_idx, midpoint_idx - 1)
        clear_decomp = self.is_clear_signal(break_contact_idx, pullback_end_idx,
                                            l5, break_contact_idx,midpoint_idx)
        l4_start = None
        l4_end = None
        if clear_dwell & clear_decomp:
            # perform iterative refinement
            l4_start = self.line(pullback_cruise_idx, midpoint_idx, discard, 0)
            # real break contact index
            break_contact_idx = self.find_elbow(midpoint_idx, pullback_end_idx)
            l4_end = self.line(midpoint_idx, break_contact_idx)
            l5 = self.line(break_contact_idx, pullback_end_idx,
                           discard, discard)
            # l4 is built from 2 points:
            l4 = self._points_to_line(l4_start.intersection(l3),
                                      l4_end.intersection(l5))
        else:
            # noise is too high, don't use the split
            print("WARNING!")
            l4 = self.line(pullback_cruise_idx, break_contact_idx)

        # Line intersections:
        p0 = ForcePoint(self.time[homing_start_idx],
                        l1.find_force(self.time[homing_start_idx]))
        p1 = l1.intersection(l2)
        p2 = l2.intersection(l3)
        p3 = l3.intersection(l4)
        p4 = l4.intersection(l5)
        p5 = ForcePoint(self.time[pullback_end_idx],
                        l5.find_force(self.time[pullback_end_idx]))
        return [p0, p1, p2, p3, p4, p5], [l1, l2, l3, l4_start, l4_end, l5]

for i in range(1, 100):
    for probe in sample_probes:
        fg = ForceGraph(probe["time"], probe["force"])
        better_points, better_lines = fg.tap_decompose_better(probe["home_end_time"],
                                        probe["pullback_start_time"],
                                        probe["moves"][4]["print_time"],
                                        probe["pullback_end_time"] - probe["pullback_start_time"],
                                        3)