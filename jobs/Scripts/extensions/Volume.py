def resetAttributes():
    cmds.setAttr('RPRVolumeMaterial1.scatterColor', 1, 1, 1, type='double3')
    cmds.setAttr('RPRVolumeMaterial1.transmissionColor',
                 1, 1, 1, type='double3')
    cmds.setAttr('RPRVolumeMaterial1.emissionColor', 1, 0, 1, type='double3')
    cmds.setAttr('RPRVolumeMaterial1.density', 0.5)
    cmds.setAttr('RPRVolumeMaterial1.scatteringDirection', 0.096)
    cmds.setAttr('RPRVolumeMaterial1.multiscatter', 1)


def setAttribute(volume_attr, file_attr, value):
    file = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
    texture = cmds.shadingNode("place2dTexture", asUtility=True)
    cmds.connectAttr(texture + ".coverage", file + ".coverage", f=True)
    cmds.connectAttr(texture + ".translateFrame",
                     file + ".translateFrame", f=True)
    cmds.connectAttr(texture + ".rotateFrame", file + ".rotateFrame", f=True)
    cmds.connectAttr(texture + ".mirrorU", file + ".mirrorU", f=True)
    cmds.connectAttr(texture + ".mirrorV", file + ".mirrorV", f=True)
    cmds.connectAttr(texture + ".stagger", file + ".stagger", f=True)
    cmds.connectAttr(texture + ".wrapU", file + ".wrapU", f=True)
    cmds.connectAttr(texture + ".wrapV", file + ".wrapV", f=True)
    cmds.connectAttr(texture + ".repeatUV", file + ".repeatUV", f=True)
    cmds.connectAttr(texture + ".offset", file + ".offset", f=True)
    cmds.connectAttr(texture + ".rotateUV", file + ".rotateUV", f=True)
    cmds.connectAttr(texture + ".noiseUV", file + ".noiseUV", f=True)
    cmds.connectAttr(texture + ".vertexUvTwo", file + ".vertexUvTwo", f=True)
    cmds.connectAttr(texture + ".vertexUvThree",
                     file + ".vertexUvThree", f=True)
    cmds.connectAttr(texture + ".vertexCameraOne",
                     file + ".vertexCameraOne", f=True)
    cmds.connectAttr(texture + ".outUV", file + ".uv", f=True)
    cmds.connectAttr(texture + ".outUvFilterSize", file + ".uvFilterSize")
    cmds.connectAttr(texture + ".vertexUvOne", file + ".vertexUvOne")

    cmds.connectAttr(file + "." + file_attr,
                     "RPRVolumeMaterial1." + volume_attr, force=True)
    cmds.setAttr(file + ".fileTextureName", value, type="string")

    return file
