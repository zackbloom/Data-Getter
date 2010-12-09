import xml.dom.minidom

def fix_single_elems(struct):
    """
    Replace the value of dict entries which are single-item lists with the list entry.
    """
    if not isinstance(struct, dict):
        return struct

    for k, v in struct.iteritems():
        if isinstance(v, list):
            for i, val in enumerate(v):
                v[i] = fix_single_elems(val)

            if len(v) == 1:
                struct[k] = v[0]

    return struct
    
# Remainder of file taken from: 
# http://nonplatonic.com/ben.php?title=python_xml_to_dict_bow_to_my_recursive_g&more=1&c=1&tb=1&pb=1

def xmltodict(xmlstring):
    doc = xml.dom.minidom.parseString(xmlstring)
    remove_whilespace_nodes(doc.documentElement)
    return elementtodict(doc.documentElement)

def elementtodict(parent):
    child = parent.firstChild
    if (not child):
        return None
    elif (child.nodeType == xml.dom.minidom.Node.TEXT_NODE):
        return child.nodeValue
    
    d={}
    while child is not None:
        if (child.nodeType == xml.dom.minidom.Node.ELEMENT_NODE):
            try:
                d[child.tagName]
            except KeyError:
                d[child.tagName]=[]
            d[child.tagName].append(elementtodict(child))
        child = child.nextSibling
    return d

def remove_whilespace_nodes(node, unlink=True):
    remove_list = []
    for child in node.childNodes:
        if child.nodeType == xml.dom.Node.TEXT_NODE and not child.data.strip():
            remove_list.append(child)
        elif child.hasChildNodes():
            remove_whilespace_nodes(child, unlink)
    for node in remove_list:
        node.parentNode.removeChild(node)
        if unlink:
            node.unlink()