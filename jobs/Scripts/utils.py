def is_case_skipped(case, render_platform, engine):
    if case['status'] == 'skipped':
        return True

    if sum([render_platform & set(skip_conf) == set(skip_conf) for skip_conf in case.get('skip_config', '')]):
        for i in case['skip_config']:
            skip_config = set(i)
            if render_platform.intersection(skip_config) == skip_config:
                return True

    if any([eng for eng in case.get('skip_engine', []) if eng == engine]):
        return True

    return False 