def setAttribute(pbr_attr, file_attr, value):
    file = cmds.shadingNode('file', asTexture=True, isColorManaged=True)
    cmds.connectAttr(file + '.' + file_attr,
                     'RPRToonMaterial1.' + pbr_attr, force=True)
    cmds.setAttr(file + '.fileTextureName', value, type='string')
    return file


def resetAttributes():
    pass
