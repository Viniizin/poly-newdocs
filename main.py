import os

def getClassLink(className):
    # Find the actual link for the input classname by searching for the markdown file
    search_path = "docs/objects/"
    for root, dirs, files in os.walk(search_path):
        for file in files:
            if file.endswith(".md"):
                if file[:-3] == className:
                    filePath = os.path.join(root, file)
                    filePath = filePath[len(search_path):]
                    filePath = filePath[:-3]
                    if "enums/" in filePath:
                        return "[:polytoria-%s: %s](/objects/%s)" % ("Enum", className, filePath)
                    return "[:polytoria-%s: %s](/objects/%s)" % (className, className, filePath)
    return "?"

"Define macros"
def define_env(env):
     
                        
    """
    Used to generate the "Inherited from" links in the documentation.
    This runs custom logic to find the correct link for a given class name,
    as the class name is not always equvilent to the markdown file's path.

    This assumes that the class is correctly placed in the docs/objects/ folder
    """
    @env.macro
    def inherits(className):
        return "Inherits %s\n{ data-search-exclude }" % (getClassLink(className))

   
    @env.macro
    def ambiguous(className, description):
        return "!!! note \"Not to be confused with %s, %s\"" % (getClassLink(className), description)
    
    # Classes is an array of pairs of class names and descriptions
    @env.macro
    def ambiguousMultiple(classes):
        text = "!!! note \"Not to be confused with:\""
        for i in range(len(classes)):
            text += "\n    - %s (%s)\n" % (getClassLink(classes[i][0]), classes[i][1])
        return text
        

    


    @env.macro
    def notnewable():
        return """<div data-search-exclude markdown>
        
!!! warning "Not newable"
    This object cannot be created by scripts using `Instance.New()`
    
    </div>"""

    @env.macro
    def abstract():
        return """<div data-search-exclude markdown>
!!! danger "Abstract Object"
    This object exists only to serve as a foundation for other objects. It cannot be accessed directly, but its properties are documented below.
    
    Additionally, it cannot be created in the creator menu or with `Instance.New()`
</div>"""

    @env.macro
    def service():
        return """<div data-search-exclude markdown>
!!! example "Service Object"
    This object is automatically created by Polytoria. Additionally, scripts cannot change its parent.
</div>"""

    @env.macro
    def staticclass():
        return """<div data-search-exclude markdown>
!!! tip "Static Class"
    This object is a static class. It can be accessed by using it's name as a keyword.
    
    Additionally, it cannot be created in the creator menu or with `Instance.New()`
</div>"""

    @env.macro
    def serverexclusive():
        return "!!! warning \"This is only available to the server. It can only be accessed within server scripts.\""
    
    @env.macro
    def clientexclusive():
        return "!!! warning \"This is only available to the client. It can only be accessed within local scripts.\""

    @env.macro
    def nosync():
        return """<div data-search-exclude markdown>
!!! failure "Does not sync!"
    This object does not sync across the server and client. It is recommended to avoid changing its properties from %ss, as the changes will not be visible to players.
</div>""" % (getClassLink("Script"))
    
    @env.macro
    def readonly():
        return "!!! warning \"This property is read-only and cannot be modified.\""
    
    @env.macro
    def comingsoon():
        return "!!! failure \"This currently doesn't exist but has been promised by Polytoria developers.\""
    
    @env.macro
    def classLink(className):
        return getClassLink(className)


    """
    !!! NOT SAFE FOR PRODUCTION USE !!!
    """
    @env.macro
    def doc_env():
        "Document the environment"
        return {name:getattr(env, name) for name in dir(env) if not name.startswith('_')}

# define list of friendly names for method and property types
type_friendlyname_table = {
    "int": "number",
    "float": "number",
    "bool": "boolean",
    "array": "[]"
}

def property(name):
    value = name[3:] # in form "name:type=value"
    name = value.split(":")[0].strip()
    property_type = value.split(":")[1].strip()
    if property_type in type_friendlyname_table:
        property_type = type_friendlyname_table[property_type]
        
    default_value = ""
    type_text = property_type
    has_link = False
    if (getClassLink(property_type) != "?"):
        property_type = getClassLink(property_type)
        has_link = True
    else:
        property_type = "%s" % (property_type)
        
    split = property_type.split("=")
    if split[0] in type_friendlyname_table:
        split[0] = type_friendlyname_table[split[0]]
    if getClassLink(split[0]) != "?":
        split[0] = getClassLink(split[0])
        has_link = True
    if not has_link:
        split[0] = "`%s`" % (split[0])
    if len(split) > 1:
        property_type = split[0]
        default_value = split[1]
        type_text = "%s = `%s`" % (property_type, default_value)
    else:
        type_text = "%s" % (split[0])



    return "### :polytoria-Property: %s : %s { #%s data-toc-label=\"%s\" }" % (name, type_text, name, name)

def event(name):
    value = name[3:]
    name = value.split(":")[0].strip()

    parametersList = ""
    parameters = value.split(":")[1:]
    for i in range(len(parameters)):
        parameters[i] = parameters[i].strip()
        if parameters[i] in type_friendlyname_table:
            parameters[i] = type_friendlyname_table[parameters[i]]
        if getClassLink(parameters[i]) != "?":
            parameters[i] = getClassLink(parameters[i])
        else:
            parameters[i] = '`' + parameters[i] + '`'
    if len(parameters) > 0:
        parametersList = ": " + ", ".join(parameters)

    return "### :polytoria-Event: %s %s { #%s data-toc-label=\"%s\" }" % (name, parametersList, name, name)

def method(name):
    value = name[3:] # in form "name:type"
    name = value.split(":")[0].strip().split("(")[0].strip()

    property_type = ""
    has_link = False
    if 1 < len(value.split(":")):
        property_type = value.split(":")[1].strip()
        if property_type in type_friendlyname_table:
            property_type = type_friendlyname_table[property_type]
        if getClassLink(property_type) != "?":
            property_type = getClassLink(property_type)
            has_link = True
    else:
        property_type = "void"

    if has_link == False:
        property_type = "`" + property_type + "`"

    numOfParams = 0
    parametersList = ""
    
    if "(" in value:
        equals = []
        parameters = ''.join(value.split("("))
        parameters = parameters.split(")")[0].replace(name, '').split(',')
        print(parameters)
        for i in range(len(parameters)):
            if not ":" in parameters[i]:
                numOfParams = numOfParams + 1
                parameters[i] = parameters[i].replace(':', '').strip()

                equals = parameters[i].split('=')
                
                for v in range(len(equals)):
                    if equals[v] in type_friendlyname_table:
                        equals[v] = type_friendlyname_table[equals[v]]
                    if getClassLink(equals[v]) != "?":
                        equals[v] = getClassLink(equals[v])
                    else:
                        equals[v] = '`' + equals[v] + '`'

            parameters[i] = ' = '.join(equals)

        print(numOfParams)
        if numOfParams > 0:
            parametersList = "<small class=\"parameters-text\">Method Parameters: " + ', '.join(parameters) + "</small>\n"

    return "%s### :polytoria-Method: %s → %s { #%s data-toc-label=\"%s\" }" % (parametersList, name, property_type, name, name)

def on_pre_page_macros(env):
    #find headers with { macroName } at the end and replace with the associated macro
    markdown_text = env.markdown
    lines = markdown_text.split("\n")
    for i in range(len(lines)):
        if lines[i].endswith("{ property }"):
            lines[i] = property(lines[i][:-len("{ property }")])
        elif lines[i].endswith("{ event }"):
            lines[i] = event(lines[i][:-len("{ event }")])
        elif lines[i].endswith("{ method }"):
            lines[i] = method(lines[i][:-len("{ method }")])
    markdown_text = "\n".join(lines)
    env.markdown = markdown_text
