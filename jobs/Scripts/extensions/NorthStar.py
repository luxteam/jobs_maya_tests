def removeEnvironment():
    objects = cmds.ls(g=True)
    for obj in objects:
        if cmds.objectType(obj) in ('RPRIBL', 'RPRSky'):
            transform = cmds.listRelatives(obj, p=True)[0]
            cmds.delete(transform)


def resetAttributesPBR():
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


def setAttributePBR(pbr_attr, file_attr, value):
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


def resetAttributesPL():
    cmds.setAttr('RPRPhysicalLight1Shape.luminousEfficacy', 17)
    cmds.setAttr('RPRPhysicalLight1Shape.intensity', 1)
    cmds.setAttr('RPRPhysicalLight1Shape.colorMode', 0)
    cmds.setAttr('RPRPhysicalLight1Shape.temperature', 6500)
    cmds.setAttr('RPRPhysicalLight1Shape.intensityUnits', 2)
    cmds.setAttr('RPRPhysicalLight1Shape.shadowsSoftness', 0.02)
    cmds.setAttr('RPRPhysicalLight1Shape.areaWidth', 1)
    cmds.setAttr('RPRPhysicalLight1Shape.areaLength', 1)
    cmds.setAttr('RPRPhysicalLight1Shape.areaLightVisible', 0)
    cmds.setAttr('RPRPhysicalLight1Shape.areaLightShape', 3)
    cmds.setAttr('RPRPhysicalLight1Shape.shadowsEnabled', 1)
    cmds.setAttr('RPRPhysicalLight1Shape.spotLightInnerConeAngle', 43)
    cmds.setAttr('RPRPhysicalLight1Shape.spotLightOuterConeFalloff', 45)


def resetAttributesQuality():
    cmds.setAttr('RadeonProRenderGlobals.maxRayDepth', 8)
    cmds.setAttr('RadeonProRenderGlobals.maxDepthDiffuse', 3)
    cmds.setAttr('RadeonProRenderGlobals.maxDepthGlossy', 5)
    cmds.setAttr('RadeonProRenderGlobals.maxDepthRefraction', 5)
    cmds.setAttr('RadeonProRenderGlobals.maxDepthRefractionGlossy', 5)
    cmds.setAttr('RadeonProRenderGlobals.maxDepthShadow', 5)
    cmds.setAttr('RadeonProRenderGlobals.raycastEpsilon', 0.02)
    cmds.setAttr('RadeonProRenderGlobals.enableOOC', 0)
    cmds.setAttr('RadeonProRenderGlobals.textureCacheSize', 512)


def resetAttributesNodes():
    cmds.setAttr('BlendUbernPBRMaterials.visibility', 0)
    cmds.setAttr('CheckerDotTexture.visibility', 0)
    cmds.setAttr('SubsurfaceMaterial.visibility', 0)
    cmds.setAttr('Arythmetic_Blend_Gradient.visibility', 0)
    cmds.setAttr('LookUpNoisePassthrough.visibility', 0)
    cmds.setAttr('BumpNormal.visibility', 0)
    cmds.setAttr('Fresnel.visibility', 0)


def applyMaterial(material):
    libraryPath = fireRender.rpr_material_browser.getLibPath()
    material_path = path.join(libraryPath, material)
    xml = [f for f in os.listdir(material_path) if f.endswith('.xml')]
    print('Material to import: ' + material)
    cmds.RPRXMLImport(file=path.join(
        material_path, xml[0]), ii=False, mn='materialTestNode')
    cmds.hyperShade(objects='lambert1')
    rpr_sg = cmds.listConnections('materialTestNode', type='shadingEngine')[0]
    print('Material connected: ' + material)
    cmds.sets(e=True, forceElement=rpr_sg)


def detachMaterial():
    cmds.delete('materialTestNode')
    rpr_sg = cmds.listConnections('lambert1', type='shadingEngine')[0]
    cmds.sets(e=True, forceElement=rpr_sg)


def setAttributeSS(ss_shape, attr, value):
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


def resetAttributesTM():
    cmds.setAttr('RadeonProRenderGlobals.toneMappingType', 0)
    cmds.setAttr('RadeonProRenderGlobals.applyGammaToMayaViews', 0)
    cmds.setAttr('RadeonProRenderGlobals.toneMappingLinearScale', 1)
    cmds.setAttr('RadeonProRenderGlobals.toneMappingPhotolinearSensitivity', 1)
    cmds.setAttr('RadeonProRenderGlobals.toneMappingPhotolinearExposure', 1)
    cmds.setAttr('RadeonProRenderGlobals.toneMappingPhotolinearFstop', 3.8)
    cmds.setAttr('RadeonProRenderGlobals.toneMappingReinhard02Prescale', 0.1)
    cmds.setAttr('RadeonProRenderGlobals.toneMappingReinhard02Postscale', 1)
    cmds.setAttr('RadeonProRenderGlobals.toneMappingReinhard02Burn', 30)
    cmds.setAttr('RadeonProRenderGlobals.toneMappingWhiteBalanceValue', 3200)
    cmds.setAttr('RadeonProRenderGlobals.toneMappingWhiteBalanceEnabled', 0)
    cmds.setAttr('RadeonProRenderGlobals.displayGamma', 2.2)


def setAttributeUber(pbr_attr, file_attr, value):
    file = setTextureUber(pbr_attr, value)
    cmds.connectAttr(file + '.' + file_attr,
                     'R_UberMat.' + pbr_attr, force=True)
    cmds.setAttr(file + '.fileTextureName', value, type='string')
    return file


def resetAttributesUber():
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


def setTextureUber(attr, value):
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


def setPass(case):
    work_dir = path.join(
        WORK_DIR, 'Color', case['case'] + case.get('extension', '.jpg'))
    source_dir = path.join(WORK_DIR, '..', '..', '..',
                           '..', 'jobs_launcher', 'common', 'img')

    copyfile(path.join(source_dir, 'passed.jpg'), work_dir)
