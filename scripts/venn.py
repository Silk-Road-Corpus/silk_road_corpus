"""This script generates a Venn diagram for two sets.
"""

import json
import math

# T 607
s1 = """三藏,僧伽羅剎,安世高,佛,三界,精進,度,佛法,諦法,行者,道地,生老病死,憂慼,苦本,得道,無為,念欲,念瞋恚,念侵,惡知識,持戒,受慧,
攝意,色想,常樂,淨,貪,恚,癡,睡眠,忘意,疑過,畏怖,攝根,世間法,縛束,出,明知識,少食事,苦,不淨,守意,方便,攝根門,空澤,觀,護,厭食,戒淨,
墮信,斂受法事,定,功德聚,習,止觀,四德,一切苦,穿,苦行,慧者,無為種,通經者,觀經教,五陰,甘露,貪為種,愛,佛說,箜篌,色種,痛痒種,思想種,
行種,識種,十入,法,受入,百八痛,百八思想,百八行為行種,百八識,五種,成聚五種,五陰慧,性河,六足,蓮花,慧日,奉事佛,清淨,世絕福祐人,敷演,
五種各應相,五陰種相,五盛陰,五陰薪,惡火,三毒,智慧意,佛所說,地獄,罪,畜生,餓鬼,天上,人中,殃福,夙行,風熱寒,愛識,生死種,身根,心根,節,
筋脈,骨髓,三好,上天,精識滅,中陰,受生種,天眼,三食,樂,念,癡生,刀葉樹,惡意,不與取,讒失誡,妄論議,善還不行法語,福行,精,胞門,邪鬼,
魑魅魍魎,蠱魅魖行,六根,世間輪,空,幻,生死,流水,生滅,慧清入心,度世樂,一心,世間明,止,因緣,念惡露,安般守意,惡露行,安隱,死屍,無有異,
非常,非身,無所有,自在,行增滿,五十五因緣,沫,五樂,怨家,化城,骨關肉血塗,貪恚癡聚,善意,破瓶常漏,畫瓶,清溷,九門,血,疥,腐穀舍,大窟,蟲,
骨嚾,罪如滿狐猴不失,不熟器,一囊兩口,葬地,露霧,瘡,盲,不淨聚,地孔,虺,空把,塚間,瞋恚忽然,顛疾盛,八十八結行,畏死,銅塗金,空聚,六衰,
腐髑髏,迦陀樹皮,胎小,腐囊,深冥,六十二疑,喜妬,結垢,不意,無所依,愛不愛,破碎,病,無有自歸
"""

# T 606, fascicle 1
s2 = """沙門,法藏,十二部經,三達之智,大慈悲,眾生,甘露,菩薩,五陰,生死,三昧,禪數,解空歸無,無為,三藏,天人龍鬼神,世尊,三界,佛,正法,
眾僧,三德,道眼,平等法,修行,世俗,經典,精進,生老死,苦,濟度,毀戒,邪計常,貪樂有身,放逸,懈怠,怒癡,根門,邪說,非法,道義,瞋恚,貪欲,不淨想,
奉戒清淨,無常,苦空非身,塵勞,寂定,平等解脫,諦,泥洹,無我想,諸根,凡夫,學向道,無所學,寂觀,沙門四德之果,有餘泥洹,無為之界,教禁,定,憍慢,
智慧,靜漠,垢冥,度世,羅漢,能仁,稽首,欲,色,痛,想,行,識,十入,佛教,愚癡,比丘,無所著,無想,墮落,善,不善,佛法教,弟子,閻王,迦葉,天帝,
執金剛,業,眾緣,四大,意根,善道,惡道,身,口,意,中止,三食,三塗,人間,天上,泥犁,地獄,聖法教,正道,邪徑,畜生處,癡,冥道,薜荔,餓鬼,忉利天,
福業,人道,邪念,罪福,緣,宿行,不淨,偈,六情,空,生死之輪,幻化,顛倒
"""

def csv_to_set(csv_string: str) -> set[str]:
    """
    Transforms a comma-separated string into a set of unique strings.
    """
    if not csv_string:
        return set()
    items: list[str] = csv_string.split(',')
    # Strip whitespace and 3. Filter out empty strings
    cleaned_items: list[str] = [item.strip() for item in items if item.strip()]
    return set(cleaned_items)

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

    term1 = r1**2 * math.acos((d**2 + r1**2 - r2**2) / (2 * d * r1))
    term2 = r2**2 * math.acos((d**2 + r2**2 - r1**2) / (2 * d * r2))
    term3 = 0.5 * math.sqrt((-d + r1 + r2) * (d + r1 - r2) * (d - r1 + r2) * (d + r1 + r2))
    return term1 + term2 - term3

def find_distance(r1, r2, target_intersection_area):
    """
    Find the distance between circle centers for a target intersection area
    using the bisection method.
    """
    if target_intersection_area <= 1e-9:
        return r1 + r2
    
    min_possible_intersection_area = math.pi * min(r1, r2)**2
    if target_intersection_area >= min_possible_intersection_area:
        return 0

    low = abs(r1 - r2)
    high = r1 + r2
    
    area = 0.0
    for _ in range(100): # 100 iterations for precision
        d = (low + high) / 2
        area = intersection_area(r1, r2, d)
        if abs(area - target_intersection_area) < 1e-9:
            break
        if area > target_intersection_area:
            low = d
        else:
            high = d
    area1 = math.pi * r1**2
    area2 = math.pi * r2**2
    print(f"Area 1: {area1:.1f}, Area 2: {area2:.1f}, intersection area: {area:.1f}")
    print(f"Intersection percent of 1: {area /area1:.3f}, Intersection percent of 2: {area /area2:.3f}")
    return d

# Define the sets
set1 = csv_to_set(s1)
set2 = csv_to_set(s2)
# set1 = {'a', 'b', 'c', 'd', 'e'}
# set2 = {'e', 'f', 'g', 'h', 'i'}

# Calculate sizes
set1_size = len(set1)
set2_size = len(set2)
intersection_size = len(set1.intersection(set2))
set1_only_size = len(set1.difference(set2))
set2_only_size = len(set2.difference(set1))

print(f"set1_size: {set1_size}, set2_size: {set2_size}, intersection_size: {intersection_size}")
print(f"Intersection 1 ratio: {intersection_size/set1_size:.2f}, Intersection 2 ratio: {intersection_size/set2_size:.2f}")
print(f"Intersection: {set1.intersection(set2)}")

# Calculate radii so that circle area is proportional to set size
scaling_factor = 10
radius1 = scaling_factor * math.sqrt(set1_size)
radius2 = scaling_factor * math.sqrt(set2_size)

# Calculate the target intersection area
if set1_size > 0:
    k = (math.pi * radius1**2) / set1_size
    target_intersection_area = k * intersection_size
else:
    target_intersection_area = 0

# Find the distance between the centers
distance = find_distance(radius1, radius2, target_intersection_area)

print(f"radius1: {radius1:.1f}, radius2: {radius2:.1f}")
print(f"Target intersection area: {target_intersection_area:.1f}")
print(f"Distance between centers: {distance:.1f}")

# File paths
template_path = 'drawings/venn2_template.vg.json'
output_path = 'drawings/venn2_generated.vg.json'

# Read the template file
with open(template_path, 'r') as f:
    vega_template = json.load(f)

# Update radii
vega_template['data'][0]['values'][0]['radius'] = radius1
vega_template['data'][0]['values'][1]['radius'] = radius2

# Update positions
center_x = (vega_template['data'][0]['values'][0]['x'] + vega_template['data'][0]['values'][1]['x']) / 2
x1 = center_x - distance / 2
x2 = center_x + distance / 2
vega_template['data'][0]['values'][0]['x'] = x1
vega_template['data'][0]['values'][1]['x'] = x2

# Update the sizes in the template
vega_template['data'][1]['values'][0]['label'] = str(set1_only_size)
vega_template['data'][1]['values'][1]['label'] = str(intersection_size)
vega_template['data'][1]['values'][2]['label'] = str(set2_only_size)

# Update positions of the size labels
vega_template['data'][1]['values'][0]['x'] = x1 - radius1 / 2.5
vega_template['data'][1]['values'][1]['x'] = (x1 + x2) / 2
vega_template['data'][1]['values'][2]['x'] = x2 + radius2 / 2.5

# Save the new vega file
with open(output_path, 'w') as f:
    json.dump(vega_template, f, indent=2)

print(f"Generated Venn diagram with updated radii and positions saved to {output_path}")