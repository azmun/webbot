def shallowFlatten(xs):
    ret = []
    for x in xs:
        if isinstance(x, (list, tuple)):
            ret.extend(x)
        else:
            ret.append(x)
    return ret
