import os
import maya.cmds as cmds
import maya.mel as mel


def main():
    try:
        if not cmds.pluginInfo("RadeonProRender", query=True, loaded=True):
            print("[INFO] RadeonProRender plugin is not loaded. Loading RPR plugin ...")
            cmds.loadPlugin("RadeonProRender")
    except Exception as err:
        print("[ERROR] Failed to load RadeonProRender plugin. Error message: {}".format(str(err)))
        cmds.quit(abort=True)

    print("[INFO] RadeonProRender plugin has been successfully loaded.")

    try:
        print("[INFO] Preparing configurations for rendering...")
        cmds.setAttr('defaultRenderGlobals.currentRenderer', 'FireRender', type='string')
        cmds.athenaEnable(ae=False)
        engine = os.getenv('ENGINE', 'Tahoe')
        if engine == "Tahoe":
            cmds.setAttr('RadeonProRenderGlobals.tahoeVersion', 1)
        elif engine == "Northstar":
            cmds.setAttr('RadeonProRenderGlobals.tahoeVersion', 2)
        print("[INFO] Current render engine: {}.".format(engine))
        cmds.setAttr("RadeonProRenderGlobals.completionCriteriaSeconds", 0)
        cmds.setAttr('defaultRenderGlobals.imageFormat', 8)
        
        mel.eval('fireRender -waitForItTwo')
        mel.eval('renderIntoNewWindow render')
        
        results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Work', 'Results', 'Maya')
        cmds.sysFile(results_dir, makeDir=True)
        test_case_path = os.path.join(results_dir, 'cache_building')
        cmds.renderWindowEditor('renderView', edit=1,  dst='color')
        cmds.renderWindowEditor('renderView', edit=1, com=1, writeImage=test_case_path)
        print("[INFO] Render has been finished")
    except Exception as err:
        print("[ERROR] Failed to render the scene. Error message: {}".format(str(err)))
        cmds.quit(abort=True)
    finally:
        print("[INFO] Closing Maya.")
        cmds.evalDeferred("cmds.quit(abort=True)")


cmds.evalDeferred("cache_building.main()")
