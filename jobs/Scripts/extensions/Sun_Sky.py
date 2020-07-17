def removeEnvironment():
    objects = cmds.ls(g=True)
    for obj in objects:
        if cmds.objectType(obj) in ('RPRIBL', 'RPRSky'):
            transform = cmds.listRelatives(obj, p=True)[0]
            cmds.delete(transform)


def setAttribute(ss_shape, attr, value):
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

    cmds.connectAttr(file + ".outColor", ss_shape + "." + attr, force=True)
    cmds.setAttr(file + ".fileTextureName", value, type="string")

    return file
