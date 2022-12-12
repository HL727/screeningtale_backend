def convert_bool(vals: dict) -> dict:
    for key, val in vals.items():
        if type(val) == bool:
            if val == False:
                vals[key] = 0
            elif val == True:
                vals[key] = 1
