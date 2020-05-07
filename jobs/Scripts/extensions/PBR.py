def resetAttributes():
    cmds.setAttr('R_PBRMat.color', 0.0719, 0.31, 0.0719, type='double3')
    cmds.setAttr('R_PBRMat.metalness', 0)
    cmds.setAttr('R_PBRMat.specular', 1)
    cmds.setAttr('R_PBRMat.roughness', 0.1)
    try:
        cmds.connectAttr('RPRNormal4.out', 'R_PBRMat.normalMap', f=True)
    except:
        pass
    cmds.setAttr('R_PBRMat.glass', 1)
    cmds.setAttr('R_PBRMat.glassIOR', 1.2)
    cmds.setAttr('R_PBRMat.emissiveColor', 0.5, 0.5, 0.5, type='double3')
    cmds.setAttr('R_PBRMat.emissiveWeight', 0)
    cmds.setAttr('R_PBRMat.subsurfaceWeight', 0)
    cmds.setAttr('R_PBRMat.subsurfaceColor', 0.436,
                 0.227, 0.131, type='double3')
    cmds.setAttr('R_PBRMat.subsurfaceRadius0', 3.67)
    cmds.setAttr('R_PBRMat.subsurfaceRadius1', 1.37)
    cmds.setAttr('R_PBRMat.subsurfaceRadius2', 0.68)
    cmds.setAttr('file14.fileTextureName',
                 'sourceimages/normal.tif', type='string')


def setAttribute(pbr_attr, file_attr, value):
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
                     "R_PBRMat." + pbr_attr, force=True)
    cmds.setAttr(file + ".fileTextureName", value, type="string")

    return file
