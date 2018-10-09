def role_prof(name):
    name,unit_name = name.split('@')
    if unit_name == 'manufacturing':
        return 'XXXX-----'
    if unit_name == 'sterilization':
        return '----XX---'
    if unit_name == 'quality':
        return '------XXX'