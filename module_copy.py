from xml.etree import ElementTree
from decimal import Decimal

filename = "c:/Users/bevice/eagle/projects/bulychev/pwr/pwr_profile_test1.brd"
f2 = "c:/Users/bevice/eagle/projects/bulychev/pwr/pwr_profile_test2.brd"

REF_DESIGN = "CHARGER1"
MODIFY_DESIGN = ["CHARGER2", "CHARGER3", "CHARGER4", "CHARGER5"]
REF_ELEMENT = "IC2"


def get_module_name(element_name):
    if not ":" in element_name:
        return None
    return element_name.split(":")[0]


def get_element_name(element_name):
    if not ":" in element_name:
        return element_name
    return element_name.split(":")[1]


tree = ElementTree.parse(filename)
root = tree.getroot()

positions = {}
# Находим все прозиции  элементов для заданного модуля
ref_position = None
modify_zeroes = {}

for e in root.iter("element"):
    name = get_element_name(e.attrib["name"])
    if get_module_name(e.attrib["name"]) == REF_DESIGN:
        attribs = {}
        positions[name] = {"x": Decimal(e.attrib["x"]), "y": Decimal(e.attrib["y"]),
                           "attribs": attribs}
        if "rot" in e.attrib.keys():
            positions[name]["rot"] = e.attrib["rot"]
        # Находим позиции аттрибутов
        for a in e.iter("attribute"):
            if len({"name", "x", "y"} & set(a.attrib.keys())) == 3:
                attribs[a.attrib["name"]] = {"x": Decimal(a.attrib["x"]), "y": Decimal(a.attrib["y"])}
        if name == REF_ELEMENT:
            ref_position = {"x": Decimal(e.attrib["x"]), "y": Decimal(e.attrib["y"])}
    if get_module_name(e.attrib["name"]) in MODIFY_DESIGN:
        if name == REF_ELEMENT:
            modify_zeroes[get_module_name(e.attrib["name"])] = {"x": Decimal(e.attrib["x"]),
                                                                "y": Decimal(e.attrib["y"])}

# Приводим координаты к REF_ELEMENT
if ref_position is not None:
    for name in positions.keys():
        positions[name]["x"] -= ref_position["x"]
        positions[name]["y"] -= ref_position["y"]
        for a in positions[name]["attribs"].keys():
            positions[name]["attribs"][a]["x"] -= ref_position["x"]
            positions[name]["attribs"][a]["y"] -= ref_position["y"]

# Изменяем координаты
for e in root.iter("element"):
    if get_module_name(e.attrib["name"]) in MODIFY_DESIGN:
        name = get_element_name(e.attrib["name"])
        module = get_module_name(e.attrib["name"])
        e.attrib["x"] = str(modify_zeroes[module]["x"] + positions[name]["x"])
        e.attrib["y"] = str(modify_zeroes[module]["y"] + positions[name]["y"])
        if "rot" in positions[name]:
            e.attrib["rot"] = positions[name]["rot"]
        for a in e.iter("attribute"):
            if len({"name", "x", "y"} & set(a.attrib.keys())) == 3 \
                    and a.attrib["name"] in positions[name]["attribs"].keys():
                a.attrib["x"] = str(modify_zeroes[module]["x"] + positions[name]["attribs"][a.attrib["name"]]["x"])
                a.attrib["y"] = str(modify_zeroes[module]["y"] + positions[name]["attribs"][a.attrib["name"]]["y"])

tree.write(open(f2, "wb"))

print("Done")