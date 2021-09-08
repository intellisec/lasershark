

def leds_pca955x(tree,line):
    """Searches for a leds-pca955x node

    Returns:
    --------
    list or None
        Lists all found leds behind a pca955x ic. If no pca955x usage is
        found, None is returned.
    """
    compatibleStrings = ["nxp,pca9550", "nxp,pca9551", "nxp,pca9552", "ibm,pca9552", "nxp,pca9553"]
    result = []


    # Check if one of the ICs is used
    for s in compatibleStrings:
        try:
            leds = tree.match(s)
        except Exception:
            continue

        if len(leds) > 0:
            for ledNode in leds:
                # At least one leds is found.
                # Parseing the leds
                for cn in ledNode.child_nodes():
                    typ = cn.get_fields("type")
                    if not type is None:
                        typ = str(typ)
                        if type == "<PCA955X_TYPE_LED>":
                            label = str(cn.get_fields("label")).replace("\"", "")
                            function = cn.get_fields("function")
                            color = cn.get_fields("color")
                            trigger = cn.get_fields("trigger,default-trigger")
                            modeStr = "UNKNOWN_pca955x"
                            # print(f"Found led {label} on pin {pin} in {modeStr}")
                            result.append({"label": label, "mode": modeStr, "function": function, "trigger": trigger,"color":color})
        else:
            # No gpio-leds found!
            pass

    return result