def removeEnvironment():
    objects = cmds.ls(g=True)
    for obj in objects:
        if cmds.objectType(obj) in ('RPRIBL', 'RPRSky'):
            transform = cmds.listRelatives(obj, p=True)[0]
            cmds.delete(transform)
