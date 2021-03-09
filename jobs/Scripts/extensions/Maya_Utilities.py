def assignMaterial(material):
    cmds.select('shaderball')
    cmds.hyperShade(assign=material)
    cmds.setAttr("%s.reflections" % material, 1)
    cmds.setAttr("%s.reflectRoughness" % material, 0)

def resetMaterial():
    cmds.select('shaderball')
    cmds.hyperShade(assign='lambert1')
