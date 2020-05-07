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
