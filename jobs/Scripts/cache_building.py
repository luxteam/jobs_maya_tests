import maya.cmds as cmds
import maya.mel as mel
import os


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
        print("Preparation for rendering")
        cmds.setAttr('defaultRenderGlobals.currentRenderer', type='string' 'FireRender')
        cmds.setAttr("RadeonProRenderGlobals.completionCriteriaSeconds", 30)
        cmds.setAttr('defaultRenderGlobals.imageFormat', 8)
        
        mel.eval('fireRender -waitForItTwo')
        mel.eval('renderIntoNewWindow render')
        
        results_dir = os.path.abspath(os.path.join(os.getcwd(), '..', '..', 'Work', 'Results', 'Maya'))
        cmds.sysFile(results_dir, makeDir=True)
        test_case_path = os.path.join(results_dir, 'cache_building')
        cmds.renderWindowEditor('renderView', edit=1,  dst='color')
        cmds.renderWindowEditor('renderView', edit=1, com=1, writeImage=test_case_path)
        print("Render has been finished")
    except Exception as err:
        print("Error during rendering. {}".format(str(err)))
        cmds.quit(abort=True)
    finally:
        print("Quit")
        cmds.evalDeferred("cmds.quit(abort=True)")


cmds.evalDeferred("cache_building.main()")