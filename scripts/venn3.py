import json
import math

def intersection_area(r1, r2, d):
    """
    Calculate the intersection area of two circles.
    https://mathworld.wolfram.com/Circle-CircleIntersection.html
    """
    if d <= 0:
        return math.pi * min(r1, r2)**2
    if d >= r1 + r2:
        return 0
    if d <= abs(r1 - r2):
        return math.pi * min(r1, r2)**2

    d2 = d**2
    r1_2 = r1**2
    r2_2 = r2**2
    
    term1 = r1_2 * math.acos((d2 + r1_2 - r2_2) / (2 * d * r1))
    term2 = r2_2 * math.acos((d2 + r2_2 - r1_2) / (2 * d * r2))
    term3 = 0.5 * math.sqrt((-d + r1 + r2) * (d + r1 - r2) * (d - r1 + r2) * (d + r1 + r2))
    
    return term1 + term2 - term3

def find_distance(r1, r2, target_area):
    """
    Find the distance between circle centers for a target intersection area
    using the bisection method.
    """
    if target_area <= 1e-9:
        return r1 + r2
    
    min_possible_intersection_area = math.pi * min(r1, r2)**2
    if target_area >= min_possible_intersection_area:
        # This happens when one circle is almost completely inside another
        # The distance should be small
        return abs(r1-r2)

    low = abs(r1 - r2)
    high = r1 + r2
    
    for _ in range(100): # 100 iterations for precision
        d = (low + high) / 2
        area = intersection_area(r1, r2, d)
        if abs(area - target_area) < 1e-9:
            break
        if area > target_area:
            low = d
        else:
            high = d
    return d

# Define the sets
set1 = {'a', 'b', 'c'}
set2 = {'c', 'd', 'e', 'f'}
set3 = {'c', 'f', 'g', 'h', 'i', 'j', 'k'}

# Calculate the sizes of the sets and intersections
size1 = len(set1)
size2 = len(set2)
size3 = len(set3)
size12 = len(set1.intersection(set2))
size13 = len(set1.intersection(set3))
size23 = len(set2.intersection(set3))
size123 = len(set1.intersection(set2).intersection(set3))

s1_only = size1 - size12 - size13 + size123
s2_only = size2 - size12 - size23 + size123
s3_only = size3 - size13 - size23 + size123
s12_only = size12 - size123
s13_only = size13 - size123
s23_only = size23 - size123

# Calculate radii and target intersection areas
# Area of circle will be proportional to set size
scaling_factor = 20
r1 = scaling_factor * math.sqrt(size1)
r2 = scaling_factor * math.sqrt(size2)
r3 = scaling_factor * math.sqrt(size3)

# The area of a circle is pi * r^2. The scaling constant k for area is pi * scaling_factor^2
k_area = math.pi * scaling_factor**2
target_area12 = k_area * size12
target_area13 = k_area * size13
target_area23 = k_area * size23

# Find distances between circle centers
d12 = find_distance(r1, r2, target_area12)
d13 = find_distance(r1, r3, target_area13)
d23 = find_distance(r2, r3, target_area23)

# It's not always possible to satisfy all intersection areas perfectly with circles.
# We must check if the distances can form a triangle.
# If not, we have to adjust them. This is a hard problem.
# For now, we'll proceed assuming they form a valid triangle.
if not (d12 + d13 >= d23 and d12 + d23 >= d13 and d13 + d23 >= d12):
    print("Warning: The calculated distances do not form a valid triangle. The Venn diagram will be distorted.")
    # A simple adjustment to make it a triangle, though this breaks the area mapping for one intersection.
    if d12 + d13 < d23:
        d23 = d12 + d13 - 1e-6
    elif d12 + d23 < d13:
        d13 = d12 + d23 - 1e-6
    elif d13 + d23 < d12:
        d12 = d13 + d23 - 1e-6

# Calculate circle center coordinates
c1 = (0, 0)
c2 = (d12, 0)
# Using law of cosines to find the position of the third circle
x3 = (d12**2 + d13**2 - d23**2) / (2 * d12) if d12 > 1e-9 else 0
y3_sq = d13**2 - x3**2
y3 = math.sqrt(y3_sq) if y3_sq > 0 else 0
c3 = (x3, y3)

# Center the diagram
centroid_x = (c1[0] + c2[0] + c3[0]) / 3
centroid_y = (c1[1] + c2[1] + c3[1]) / 3
view_center_x = 250
view_center_y = 170

c1 = (c1[0] - centroid_x + view_center_x, c1[1] - centroid_y + view_center_y)
c2 = (c2[0] - centroid_x + view_center_x, c2[1] - centroid_y + view_center_y)
c3 = (c3[0] - centroid_x + view_center_x, c3[1] - centroid_y + view_center_y)

# Load the Vega template
template_path = '/Users/alexamies/silk_road_corpus/drawings/venn3_template.vg.json'
with open(template_path, 'r') as f:
    vega_spec = json.load(f)

# Update circles
vega_spec['data'][0]['values'][0].update({'radius': r1, 'x': c1[0], 'y': c1[1], 'set': f"Set 1 ({size1})"})
vega_spec['data'][0]['values'][1].update({'radius': r2, 'x': c2[0], 'y': c2[1], 'set': f"Set 2 ({size2})"})
vega_spec['data'][0]['values'][2].update({'radius': r3, 'x': c3[0], 'y': c3[1], 'set': f"Set 3 ({size3})"})

# --- Approximate Label Positions ---
# This is a heuristic and may not be perfect for all configurations.
# s1_only
l_s1_x = c1[0] - r1/2 if c1[0] < min(c2[0], c3[0]) else c1[0] + r1/2
l_s1_y = c1[1]
# s2_only
l_s2_x = c2[0] + r2/2 if c2[0] > max(c1[0], c3[0]) else c2[0] - r2/2
l_s2_y = c2[1]
# s3_only
l_s3_x = c3[0]
l_s3_y = c3[1] + r3/2 if c3[1] > max(c1[1], c2[1]) else c3[1] - r3/2

# Midpoints for intersections
m12 = ((c1[0]+c2[0])/2, (c1[1]+c2[1])/2)
m13 = ((c1[0]+c3[0])/2, (c1[1]+c3[1])/2)
m23 = ((c2[0]+c3[0])/2, (c2[1]+c3[1])/2)
m123 = ((c1[0]+c2[0]+c3[0])/3, (c1[1]+c2[1]+c3[1])/3)

# s12_only: from m12 move away from c3
l_s12_x = m12[0] + (m12[0] - c3[0]) * 0.2
l_s12_y = m12[1] + (m12[1] - c3[1]) * 0.2
# s13_only: from m13 move away from c2
l_s13_x = m13[0] + (m13[0] - c2[0]) * 0.2
l_s13_y = m13[1] + (m13[1] - c2[1]) * 0.2
# s23_only: from m23 move away from c1
l_s23_x = m23[0] + (m23[0] - c1[0]) * 0.2
l_s23_y = m23[1] + (m23[1] - c1[1]) * 0.2

# s123
l_s123_x = m123[0]
l_s123_y = m123[1]

labels = [
    {"label": str(s1_only), "x": l_s1_x, "y": l_s1_y},
    {"label": str(s2_only), "x": l_s2_x, "y": l_s2_y},
    {"label": str(s3_only), "x": l_s3_x, "y": l_s3_y},
    {"label": str(s12_only), "x": l_s12_x, "y": l_s12_y},
    {"label": str(s13_only), "x": l_s13_x, "y": l_s13_y},
    {"label": str(s23_only), "x": l_s23_x, "y": l_s23_y},
    {"label": str(size123), "x": l_s123_x, "y": l_s123_y}
]
vega_spec['data'][1]['values'] = labels

# Write the generated Vega spec to a new file
output_path = '/Users/alexamies/silk_road_corpus/drawings/venn3_generated.vg.json'
with open(output_path, 'w') as f:
    json.dump(vega_spec, f, indent=2)

print(f"Generated Venn diagram specification at: {output_path}")
