from typing import List

allowed_allen_transitions = [
    'la','lb','rb','ra', 
    'la,lb', 'la,rb','ra,lb','ra,rb'
]

allen_mapping = {
    "lb_rb_la_ra": "is preceded",
    "la_ra_lb_rb": "preceeds",
    "lb_la,rb_ra": "meets inverse",
    "la_ra,lb_rb": "meets",
    "lb_la_rb_ra": "overlaps inverse",
    "la_lb_ra_rb": "overlaps",
    "la,lb_rb_ra": "starts inverse",
    "la,lb_ra_rb": "starts",
    "lb_la_ra_rb": "during",
    "la_lb_rb_ra": "during inverse",
    "lb_la_ra,rb": "finishes",
    "la_lb_ra,rb": "finishes inverse",
    "la,lb_ra,rb": "equals"
}

def depad(path: List[str]):
    ans = []

    for x in path:
        x = x.replace(",t", "")
        x = x.replace("t", "")

        if len(x) > 0 and x in allowed_allen_transitions:
            ans.append(x)

    return ans

def compute_allen_count(paths: List[List[str]]):
    counts = {}

    for path in paths:
        dpd = depad(path)
        key = "_".join(dpd)

        if key in allen_mapping:
            key = allen_mapping[key]

            if key in counts:
                counts[key]+=1
            else:
                counts[key] = 1

    return counts