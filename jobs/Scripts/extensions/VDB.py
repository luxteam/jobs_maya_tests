def set_render_device(render_device):
    cmds.optionVar(rm='RPR_DevicesSelected')
    cmds.optionVar(iva=('RPR_DevicesSelected',
                        (render_device in ['gpu', 'dual'])))
    cmds.optionVar(iva=('RPR_DevicesSelected',
                        (render_device in ['cpu', 'dual'])))