


def leds_pca9532(tree,line):
    """Searches for a leds-pca9532 node

    Returns:
    --------
    list or None
        Lists all found leds behind a pca9532 ic. If no pca9532 usage is
        found, None is returned.
    """

    compatibleStrings = ["nxp,pca9530","nxp,pca9531","nxp,pca9532","nxp,pca9533"]
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
                        if typ == "<PCA9532_TYPE_LED>":
                            label = str(cn.get_fields("label")).replace("\"", "")
                            function = cn.get_fields("function")
                            color = cn.get_fields("color")
                            trigger = cn.get_fields("trigger,default-trigger")
                            modeStr = "UNKNOWN_pca9532"
                            # print(f"Found led {label} on pin {pin} in {modeStr}")
                            result.append({"label": label, "mode": modeStr, "function": function, "trigger": trigger,"color":color})
        else:
            # No gpio-leds found!
            pass


    return result