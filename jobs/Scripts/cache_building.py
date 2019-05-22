import maya.cmds as cmds
import maya.mel as mel

if not cmds.pluginInfo("RadeonProRender", q=True, loaded=True):
    cmds.loadPlugin("RadeonProRender")

cmds.sphere(radius=4)

cmds.setAttr("defaultRenderGlobals.currentRenderer", "FireRender", type="string")
cmds.fireRender(waitForItTwo=True)
mel.eval("renderIntoNewWindow render")

cmds.evalDeferred(cmds.quit(abort=True))