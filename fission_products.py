import requests
import csv


def str2float(input):
    """takes a string and converts to a float.
        empty strings return 0"""
    try:
        return float(input)
    except ValueError:
        return 0


def total_fission_dict(parent):
    """returns a dictionary w/ thermal, fast, and 14MeV fission yeilds for
    the parent isotope"""

    url = f"https://nds.iaea.org/relnsd/v1/data?fields=cumulative_fy&parents={parent}"

    with requests.Session() as s:
        download = s.get(url)
        decoded_content = download.content.decode("utf-8")
        cr = csv.reader(decoded_content.splitlines(), delimiter=",")

        csv_list = list(cr)
        indices = csv_list[0]

        fission_dict = {}

        for row in csv_list[1:]:
            if len(row) == 0:
                continue

            a_daughter = row[indices.index("a_daughter")]
            element_daughter = row[indices.index("element_daughter")]
            cumulative_thermal_fy = row[indices.index("cumulative_thermal_fy")]
            cumulative_fast_fy = row[indices.index("cumulative_fast_fy")]
            cumulative_14mev_fy = row[indices.index("cumulative_14mev_fy")]

            daughter = f"{element_daughter}{a_daughter}"

            fission_dict[daughter] = {
                "thermal": str2float(cumulative_thermal_fy),
                "fast": str2float(cumulative_fast_fy),
                "14mev": str2float(cumulative_14mev_fy),
            }

        return fission_dict


def specific_fission(parent, energy="thermal"):
    """returns the isotope with the corresponding thermal fission"""
    fission_dict = total_fission_dict(parent)
    specific_dict = {}

    for isotope in fission_dict:
        fission_yield = fission_dict[isotope][energy]

        if fission_yield == 0:
            continue

        if fission_yield <= 1e-6:
            continue

        specific_dict[isotope] = fission_yield

    return specific_dict


u235_tf = specific_fission("235u")
u233_tf = specific_fission("233u")

total = 0
for isotope in u233_tf:
    #print(isotope, u233_tf[isotope])
    total += u233_tf[isotope]
print(total)

#fps = 7e11
#sm = u233_tf["Sm149"]
#smps = sm * fps

#print(smps / 3600 / 24 / 365)
