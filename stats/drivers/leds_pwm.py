

def leds_pwm(tree,line):
    """Searches for a leds-pwm node

    Returns:
    --------
    list or None
        Lists all found leds that are controlled by leds-pwm. If no leds-pwm usage is
        found, None is returned.
    """
    try:
        leds = tree.match("pwm-leds")
    except Exception:
        return []


    # Node found, parse leds
    result = []

    if len(leds) > 0:
        for ledNode in leds:
            # At least one leds is found.
            # Parseing the leds
            for cn in ledNode.child_nodes():
                label = cn.get_fields("label")
                if not label is None:
                    label = str(label).replace("\"","")
                function = cn.get_fields("function")
                trigger = cn.get_fields("trigger,default-trigger")
                color = cn.get_fields("color")

                # For leds-pwm every led is active high by default
                modeStr = "ACTIVE_HIGH"
                activelow = cn.get_fields("active-low")
                if not activelow is None:
                    modeStr = "ACTIVE_LOW"

                result.append({"label": label, "mode": modeStr, "function": function, "trigger": trigger,"color":color})
    else:
        # No gpio-leds found!
        pass
    return result