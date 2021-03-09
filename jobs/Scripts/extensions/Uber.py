def setAttribute(pbr_attr, file_attr, value):
    file = setTexture(pbr_attr, value)
    cmds.connectAttr(file + '.' + file_attr,
                     'R_UberMat.' + pbr_attr, force=True)
    cmds.setAttr(file + '.fileTextureName', value, type='string')

    return file


def resetAttributes():
    cmds.setAttr('R_UberMat.diffuse', 1)
    cmds.setAttr('R_UberMat.diffuseColor', 0.05285,
                 0.298014, 0.303, type='double3')
    cmds.setAttr('R_UberMat.diffuseWeight', 1)
    cmds.setAttr('R_UberMat.diffuseRoughness', 1)
    cmds.setAttr('R_UberMat.useShaderNormal', 1)
    cmds.setAttr('R_UberMat.diffuseNormal', 1, 1, 1, type='double3')
    cmds.setAttr('R_UberMat.backscatteringWeight', 0)
    cmds.setAttr('R_UberMat.separateBackscatterColor', 0)
    cmds.setAttr('R_UberMat.backscatteringColor',
                 0.5, 0.5, 0.5, type='double3')

    cmds.setAttr('R_UberMat.reflections', 1)
    cmds.setAttr('R_UberMat.reflectColor', 1, 1, 1, type='double3')
    cmds.setAttr('R_UberMat.reflectWeight', 1)
    cmds.setAttr('R_UberMat.reflectRoughness', 0.119)
    cmds.setAttr('R_UberMat.reflectAnisotropy', 0)
    cmds.setAttr('R_UberMat.reflectAnisotropyRotation', 0)
    cmds.setAttr('R_UberMat.reflectUseShaderNormal', 1)
    cmds.setAttr('R_UberMat.reflectNormal', 1, 1, 1, type='double3')

    cmds.setAttr('R_UberMat.reflectMetalMaterial', 0)
    cmds.setAttr('R_UberMat.reflectIOR', 1.5)
    cmds.setAttr('R_UberMat.reflectMetalness', 0)

    cmds.setAttr('R_UberMat.refraction', 1)
    cmds.setAttr('R_UberMat.refractColor', 0.22, 0.957, 0.794, type='double3')
    cmds.setAttr('R_UberMat.refractWeight', 1)
    cmds.setAttr('R_UberMat.refractRoughness', 0)
    cmds.setAttr('R_UberMat.refractLinkToReflect', 0)
    cmds.setAttr('R_UberMat.refractIor', 1.5)
    cmds.setAttr('R_UberMat.refractThinSurface', 0)
    cmds.setAttr('R_UberMat.refractAbsorptionDistance', 0)
    cmds.setAttr('R_UberMat.refractAbsorbColor', 0, 0, 0, type='double3')
    cmds.setAttr('R_UberMat.refractAllowCaustics', 1)

    cmds.setAttr('R_UberMat.clearCoat', 0)
    cmds.setAttr('R_UberMat.coatColor', 1, 1, 1, type='double3')
    cmds.setAttr('R_UberMat.coatWeight', 1)
    cmds.setAttr('R_UberMat.coatRoughness', 0.5)
    cmds.setAttr('R_UberMat.coatIor', 1.5)
    cmds.setAttr('R_UberMat.coatUseShaderNormal', 0)
    cmds.setAttr('R_UberMat.coatNormal', 1, 1, 1, type='double3')
    cmds.setAttr('R_UberMat.coatThickness', 1)
    cmds.setAttr('R_UberMat.coatTransmissionColor', 1, 1, 1, type='double3')

    cmds.setAttr('R_UberMat.emissive', 0)
    cmds.setAttr('R_UberMat.emissiveWeight', 1)
    cmds.setAttr('R_UberMat.emissiveColor', 1, 1, 1, type='double3')
    cmds.setAttr('R_UberMat.emissiveIntensity', 1)
    cmds.setAttr('R_UberMat.emissiveDoubleSided', 0)

    cmds.setAttr('R_UberMat.sssEnable', 0)
    cmds.setAttr('R_UberMat.sssWeight')
    cmds.setAttr('R_UberMat.sssUseDiffuseColor', 0)
    cmds.setAttr('R_UberMat.volumeScatter', 0.436,
                 0.227, 0.131, type='double3')
    cmds.setAttr('R_UberMat.subsurfaceRadius0', 3.67)
    cmds.setAttr('R_UberMat.subsurfaceRadius1', 1.37)
    cmds.setAttr('R_UberMat.subsurfaceRadius2', 0.68)
    cmds.setAttr('R_UberMat.scatteringDirection', 0)
    cmds.setAttr('R_UberMat.multipleScattering', 1)

    cmds.setAttr('R_UberMat.transparencyEnable', 0)
    cmds.setAttr('R_UberMat.transparencyLevel', 1)
    cmds.setAttr('R_UberMat.normalMapEnable', 1)

    try:
        cmds.connectAttr('RPRNormal3.out', 'R_UberMat.normalMap', force=True)
    except:
        pass
    cmds.setAttr('R_UberMat.displacementEnable', 0)
    cmds.setAttr('R_UberMat.displacementMap', 0, 0, 0, type='double3')
    cmds.setAttr('R_UberMat.displacementMin', 13.986)
    cmds.setAttr('R_UberMat.displacementMax', 23.776)
    cmds.setAttr('R_UberMat.displacementSubdiv', 4)
    cmds.setAttr('R_UberMat.displacementCreaseWeight', 0)
    cmds.setAttr('R_UberMat.displacementBoundary', 1)


def setTexture(attr, value):
    file = cmds.shadingNode('file', asTexture=True, isColorManaged=True)
    texture = cmds.shadingNode('place2dTexture', asUtility=True)
    cmds.connectAttr(texture + '.coverage', file + '.coverage', f=True)
    cmds.connectAttr(texture + '.translateFrame',
                     file + '.translateFrame', f=True)
    cmds.connectAttr(texture + '.rotateFrame', file + '.rotateFrame', f=True)
    cmds.connectAttr(texture + '.mirrorU', file + '.mirrorU', f=True)
    cmds.connectAttr(texture + '.mirrorV', file + '.mirrorV', f=True)
    cmds.connectAttr(texture + '.stagger', file + '.stagger', f=True)
    cmds.connectAttr(texture + '.wrapU', file + '.wrapU', f=True)
    cmds.connectAttr(texture + '.wrapV', file + '.wrapV', f=True)
    cmds.connectAttr(texture + '.repeatUV', file + '.repeatUV', f=True)
    cmds.connectAttr(texture + '.offset', file + '.offset', f=True)
    cmds.connectAttr(texture + '.rotateUV', file + '.rotateUV', f=True)
    cmds.connectAttr(texture + '.noiseUV', file + '.noiseUV', f=True)
    cmds.connectAttr(texture + '.vertexUvTwo', file + '.vertexUvTwo', f=True)
    cmds.connectAttr(texture + '.vertexUvThree',
                     file + '.vertexUvThree', f=True)
    cmds.connectAttr(texture + '.vertexCameraOne',
                     file + '.vertexCameraOne', f=True)
    cmds.connectAttr(texture + '.outUV', file + '.uv', f=True)
    cmds.connectAttr(texture + '.outUvFilterSize', file + '.uvFilterSize')
    cmds.connectAttr(texture + '.vertexUvOne', file + '.vertexUvOne')

    return file
