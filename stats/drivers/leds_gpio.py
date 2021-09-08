



def __gpioleds_parseMode(mode):
    """Parses the mode bitfield of a leds-gpio node
    First bit indicates 0 = active high, 1 = active low
    According to
    linux-stable/Documentation/devicetree/bindings/gpio/gpio.txt

    All the other bits can be changed by software. We are only
    interested in the schematic basically

    Returns:
    --------
    String
        Either "ACTIVE HIGH" or "ACTIVE LOW" according to the set
        bits in mode.
    """
    if mode is None:
        return "UNKNOWN_gpio"

    bit0 = mode&1 != 0
    if bit0 == 0:
        return "ACTIVE_HIGH"
    else:
        return "ACTIVE_LOW"


def leds_gpio(tree,line):
    """Searches for a gpio-leds node and extracts the leds.
    See dt-binding documentation:
    linux-stable/Documentation/devicetree/bindings/leds

    Returns:
    --------
    list or None
        Returns a list of all found leds, if the gpio-leds
        node is found. Otherwise returns None
    """

    # Check if a gpio-leds node exists.
    try:
        leds = tree.match("gpio-leds")
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
                    label = str(label).replace("\"", "")
                function = cn.get_fields("function")
                trigger = cn.get_fields("trigger,default-trigger")
                color = cn.get_fields("color")
                try:
                    mode = cn.get_fields("gpios")[2]
                    modeStr = __gpioleds_parseMode(mode)
                except:
                    modeStr = "UNKNOWN_gpio"
                #print(f"Found led {label} on pin {pin} in {modeStr}")
                result.append( {"label":label, "mode":modeStr, "function": function, "trigger": trigger, "color":color})
    else:
        # No gpio-leds found!
        pass

    return result

