def resetAttributes():
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

def setUpDefaultNorthstarLights():
    cmds.setAttr('RPRPhysicalLight1.translateY', 4)
    cmds.setAttr('RPRPhysicalLight1.translateZ', -0.5)
    if (cmds.getAttr('RPRPhysicalLight1Shape.lightType') == 4):
        cmds.setAttr('RPRPhysicalLight1Shape.sphereLightRadius', 0.5)
    elif (cmds.getAttr('RPRPhysicalLight1Shape.lightType') == 5):
        cmds.setAttr('RPRPhysicalLight1Shape.diskLightRadius', 0.5)