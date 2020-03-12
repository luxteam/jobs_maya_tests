import maya.cmds as cmds
import maya.mel as mel


def main():
    print("Render simple object for build render cache.")
    
    try:
        if not cmds.pluginInfo("RadeonProRender", q=True, loaded=True):
            print("Plugin not loaded, try to load...")
            cmds.loadPlugin("RadeonProRender")
    except Exception as err:
        print("Error during plugin load. {}".format(str(err)))
        cmds.quit(abort=True)

    print("Plugin has been loaded")

    mel.eval('athenaEnable -ae false')

    try:
        print("Render sphere with RPR...")

        cmds.sphere(radius=4)

        cmds.setAttr("defaultRenderGlobals.currentRenderer", "FireRender", type="string")
        cmds.setAttr("RadeonProRenderGlobals.completionCriteriaSeconds", 1)
        cmds.setAttr("RadeonProRenderGlobals.completionCriteriaIterations", 1)
        cmds.fireRender(waitForItTwo=True)
        mel.eval("renderIntoNewWindow render")
        print("Render has been finished")
    except Exception as err:
        print("Error during rendering. {}".format(str(err)))
        cmds.quit(abort=True)
    finally:
        print("Quit")
        cmds.evalDeferred("cmds.quit(abort=True)")


cmds.evalDeferred("cache_building.main()")


