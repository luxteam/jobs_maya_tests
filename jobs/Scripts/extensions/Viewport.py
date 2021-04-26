def init_viewport(case):
    mel.eval('modelEditor -e -rom \"FireRenderOverride\" modelPanel4')
    rpr_render(case)

def save_viewport(case):
    for i in range(0, 100):
        cmds.refresh(currentView=True, fe='png', fn=WORK_DIR+'/Color/'+case['case']+'.jpg')