"""
Original author: @martisak
https://github.com/martisak/dict2uml

Author: Sirvan Almasi @ Imperial College London
This code has been modified from 20 Apr 2021 due to lack of maintenance by
original author.
"""
import json
import fileinput
from IPython.display import SVG
import subprocess
import uuid
import os

def plantuml_exec(*file_names):
    """Run PlantUML"""
    cmd = ["/usr/local/bin/plantuml",
           "-tsvg"] + list(file_names)
    subprocess.check_call(cmd, shell=False, stderr=subprocess.STDOUT)
    return [os.path.splitext(f)[0] + ".svg" for f in file_names]

def dict2svg(d):
    base_name = str(uuid.uuid4())
    uml_path = base_name + ".uml"
    with open(uml_path, 'w') as fp:
        fp.write(dict2plantuml(d))
    try:
        output = plantuml_exec(uml_path)
        svg_name = output[0]
        return SVG(filename=svg_name)
    finally:
        if os.path.exists(uml_path):
            os.unlink(uml_path)

        svg_path = base_name + ".svg"
        if os.path.exists(svg_path):
            os.unlink(svg_path)


def traverse(obj, parent):
    """Traverse the dictionary"""
    vertices = []
    edges = []

    for key, value in obj.items():
        properties = []
        children = {}
        children_str = []

        # The value is a list of things. Iterate over them and add
        # an object for each element. Add a child as well.
        if isinstance(value, list):
            for idx, a in enumerate(value):
                (children_str
                    .append("{}: {}".format(idx, "[object Object]")))
                if isinstance(a, dict):
                    children[idx] = a
                else:
                    children[idx] = {"value [{}]".format(type(a).__name__): a}
            vertices.append({
                "clsName": key,
                "clsNameFullReference": key,
                "clsProperties": properties,
                "clsObjects": children_str
            })
        # The value is a dictionary.
        elif isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, dict):
                    (children_str
                        .append("{}: {}".format(k, "[object Object]")))
                    children[k] = v
                elif isinstance(v, list):
                    (children_str
                        .append("{}: {}".format(k, "[object Object]")))
                    children[k] = v
                else:
                    properties.append("{}: {}".format(k, v))
            vertices.append({
                "clsName": key,
                "clsNameFullReference": key,
                "clsProperties": properties,
                "clsObjects": children_str
            })

        if children:
            p = "{}.{}".format(parent, key) if parent is not None else key
            tmpobj, tmprel = traverse(children, p)
            for r in tmprel:
                edges.append(r)
            for o in tmpobj:
                o["clsNameFullReference"] = \
                    "{}.{}".format(key, o["clsNameFullReference"])
                vertices.append(o)
            for child in children:
                if parent is not None:
                    (edges.append("\"{}.{}\" \"1\" --> \"1\" \"{}.{}.{}\""
                                  .format(parent, key, parent, key, child)))
                else:
                    (edges.append("\"{}\" \"1\" --> \"1\" \"{}.{}\""
                                  .format(key, key, child)))
    return vertices, edges


def printClass(cls):
    """Returns the string reopresention of a class"""
    s = ""
    s += ("class \"{}\" as {} {{"
          .format(cls["clsName"], cls["clsNameFullReference"])) + "\n"
    s += "\t" + ".. Properties .." + "\n"
    if cls["clsProperties"]:
        for p in cls["clsProperties"]:
            s += "\t" + p + "\n"
    if cls["clsObjects"]:
        s += "\t" + ".. Objects .." + "\n"
        for o in cls["clsObjects"]:
            s += "\t" + o + "\n"
    s += "}" + "\n"
    return s


def dict2plantuml(d):
    """Covert a dictionary to PlantUML text"""
    s = "@startuml\n"
    if isinstance(d, dict):
        d = {"root": d}
        c, r = traverse(d, None)
        for cls in c:
            s += printClass(cls) + "\n"
        for rel in r:
            s += rel + "\n"
    else:
        raise TypeError("The input should be a dictionary.")
    return s + "@enduml"


if __name__ == "__main__":
    message = ""
    for line in fileinput.input():
        message += line

    d = json.loads(message)

    print(dict2plantuml(d))
