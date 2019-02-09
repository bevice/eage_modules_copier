from xml.etree.ElementTree import Element, parse
from copy import deepcopy
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


class Signal:
    def __init__(self, element):
        self.element = element

    def copy(self):
        return Signal(deepcopy(self.element))

    # пересчитываем относительные
    def ref_coords(self, origin_x, origin_y):
        for e in self.element.iter():
            if e.tag == "wire":
                self._ref_coords_wire(e, origin_x, origin_y)
            if e.tag in ["via", "drill"]:
                self._ref_coords_xy(e, origin_x, origin_y)
            if e.tag == "polygon":
                for v in e.iter('vertex'):
                    self._ref_coords_xy(v, origin_x, origin_y)

    def _ref_coords_wire(self, e, origin_x, origin_y):
        e.attrib["x1"] = str(Decimal(e.attrib["x1"]) - origin_x)
        e.attrib["y1"] = str(Decimal(e.attrib["y1"]) - origin_y)
        e.attrib["x2"] = str(Decimal(e.attrib["x2"]) - origin_x)
        e.attrib["y2"] = str(Decimal(e.attrib["y2"]) - origin_y)

    def _ref_coords_xy(self, e, origin_x, origin_y):
        e.attrib["x"] = str(Decimal(e.attrib["x"]) - origin_x)
        e.attrib["y"] = str(Decimal(e.attrib["y"]) - origin_y)

    def move(self, new_origin_x, new_origin_y):
        self.ref_coords(-new_origin_x, -new_origin_y)


tree = parse(filename)
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

ref_signals = {}
for signal in root.iter("signal"):
    if get_module_name(signal.attrib["name"]) == REF_DESIGN:
        le = Signal(deepcopy(signal))
        ref_signals[get_element_name(signal.attrib["name"])] = le
        le.ref_coords(ref_position["x"], ref_position["y"])
        le.element.attrib["name"] = get_element_name(le.element.attrib["name"])

for signal in root.iter("signal"):
    if get_module_name(signal.attrib["name"]) not in MODIFY_DESIGN:
        continue
    signal_name = get_element_name(signal.attrib["name"])
    module_name = get_module_name(signal.attrib["name"])
    remove_elements = []
    for e in signal.iter('wire'):
        if Decimal(e.attrib["layer"]) == 19:
            remove_elements.append(e)
    for e in remove_elements:
        signal.remove(e)

    if signal_name in ref_signals:
        le = ref_signals[signal_name].copy()
        le.move(modify_zeroes[module_name]["x"], modify_zeroes[module_name]["y"])

        for element in le.element.iter("wire"): signal.append(element)
        for element in le.element.iter("polygon"): signal.append(element)
        for element in le.element.iter("via"): signal.append(element)

tree.write(open(f2, "wb"))

print("Done")
