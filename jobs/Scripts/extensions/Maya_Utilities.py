def assignMaterial(material):
    cmds.select('shaderball')
    cmds.hyperShade(assign=material)


def resetMaterial():
    cmds.select('shaderball')
    cmds.hyperShade(assign='lambert1')
