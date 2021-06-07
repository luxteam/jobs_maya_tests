import maya.cmds as cmds
import maya.mel as mel


def main():
    try:
        if not cmds.pluginInfo("RadeonProRender", query=True, loaded=True):
            print("Plugin not loaded, try to load...")
            cmds.loadPlugin("RadeonProRender")
    except Exception as err:
        print("Error during plugin load. {}".format(str(err)))
        cmds.quit(abort=True)

    print("Plugin has been loaded")

    try:
        cmds.setAttr('defaultRenderGlobals.currentRenderer', type='string' 'FireRender')
        cmds.setAttr("RadeonProRenderGlobals.completionCriteriaSeconds", 0)
        cmds.setAttr("RadeonProRenderGlobals.completionCriteriaIterations", 0)
        mel.eval('fireRender -waitForItTwo')
        mel.eval('renderIntoNewWindow render')
        print("Render has been finished")
    except Exception as err:
        print("Error during rendering. {}".format(str(err)))
        cmds.quit(abort=True)
    finally:
        print("Quit")
        cmds.evalDeferred("cmds.quit(abort=True)")


cmds.evalDeferred("cache_building.main()")