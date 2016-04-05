
import e2vdom
import managers
import utils.uuid as uuid


class DummyAttribute(object):

    __slots__ = (
        "name",
        "value"
    )

    def __init__(self, name, value=0):
        self.name = name
        self.value = value
        
    def __repr__(self):
        return self.value


class DummyAttributes(object):

    __slots__ = ("attrs",)

    def __init__(self):
        self.attrs = {}

    def __getitem__(self, key):
        if key == "name":
            return DummyAttribute("name", "")

        elif key == "dynamic":
            return DummyAttribute("dynamic",1)

        if key not in self.attrs:
            self.attrs[key] = DummyAttribute(key)

        return self.attrs[key]

    def values(self):
        return self.attrs.values()


class DummyObject(object):

    def __init__(self, vdomtype, name, action_name):
        self.name = name
        self.actions = {
            "name": {}, 
            "id": {}
        }
        self.attributes = DummyAttributes()
        self.containers = {}
        self.dynamic = {(action_name, self.name): 1}
        self.id = str(uuid.uuid4())
        self.libraries = {}
        self.objects = {}
        self.objects_list = []
        self.objects_by_name = {self.name: self}
        self.order = 0
        self.type = vdomtype
        self.types = {self.type.id: self.type}
        
    def __repr__(self):
        return "VDOM Dyn Object(<%s name='%s'> %r )" % (
            self.type.name,
            self.name,
            self.attributes.attrs
        )

    def get_attributes(self):
        return self.attributes

    def set_attribute_ex(self, name, value, do_compute=True):
        old_value = self.attributes[name].value
        self.attributes[name].value = value
        return {
            "value": value,
            "old_value": old_value
        }        

    def get_objects_list(self):
        return self.objects_list

    def get_objects(self):
        return self.objects

    def add_child(self, child):
        self.objects_by_name[child.name] = child
        self.objects_list.append(child)
        self.objects[child.id] = child
        self.types[child.type.id] = child.type
        child.parent = self

    def regenerate_uuid(self, recursive=False):
        """
        Create new guids, if needed - recursively
        """
        self.id = str(uuid.uuid4())
        if not recursive:
            return
        
        all_objects = {self.id: self}
        self.objects = {}
        
        for child in self.objects_list:
            all_objects.update(child.regenerate_uuid(recursive=recursive))
            self.objects[child.id] = child
            
        return all_objects
    
    def all_objects(self):
        """
        Return dictionary with all objects
        """
        all_objects = {self.id: self}
        for child in self.objects_list:
            all_objects.update(child.all_objects())
            
        return all_objects
    
    def find_child_by_name(self, path):
        """
        Find child element by name
        """
        path = path.split(".")
        if self.name != path[0]:
            return None
        
        child = self
        for cname in path[1:]:
            child = child.objects_by_name.get(cname, None)
            if not child:
                return None
        
        return child
                    
    def all_types(self):
        """
        Return all child types
        """
        types = self.types.copy()
        for child in self.objects.itervalues():
            types.update(child.all_types())
            
        
        return types
            

def create_dummy_objects(vdomxml, parent=None):
    """
    Create set of dummy objects
    @vdomxml must have root object (container or something else) i.e.:
    <container>
      <text />
      <text />
    </container>
    
    or
    
    <container>
      <container>
        <text />
      </container>
      <container>
        <text />
      </container>
    </container>
    """
    
    objects = {}
    attr_map = {}
    
    type_obj = managers.xml_manager.get_type_by_name(vdomxml.lname)
    
    for attr_name in type_obj.get_attributes():
        attr_map[attr_name.lower()] = type_obj.get_attributes()[attr_name].default_value

    # parse attributes
    for attr_name in vdomxml.attributes:
        if attr_name in attr_map or attr_name == "name":
            attr_map[attr_name] = vdomxml.attributes[attr_name]

    for child in vdomxml.children:
        if child.lname == "attribute":
            attr_name = child.attributes["name"]

            if attr_name and attr_name in attr_map:
                attr_map[attr_name] = child.get_value_as_xml()

    dummy_obj = DummyObject(type_obj, attr_map["name"], e2vdom.virtual_context)
    objects[dummy_obj.id] = dummy_obj
    
    for key, value in attr_map.items():
        dummy_obj.set_attribute_ex(key, value)
        
    if parent:
        parent.add_child(dummy_obj)

    # walk through childs
    for child in vdomxml.children:
        if "attribute" == child.lname:
            continue

        child, child_objects = create_dummy_objects(child, dummy_obj)
        objects.update(child_objects)

    return dummy_obj, objects


def update_attributes(parent, attributes):
    """
    Update objects attributes recursively
    """
    cache = {}
    old_values = {}

    for attr, value in attributes.iteritems():
        # split key by '.'
        # last item in list 
        #   is target attribute name
        splitted_attr = attr.rsplit(".", 1)
        
        obj = None
        if len(splitted_attr) == 1:
            obj = parent
            
        elif splitted_attr[0] in cache:
            obj = cache[splitted_attr[0]]
            
        else:
            obj = parent
            for obj_name in splitted_attr[0].split("."):
                obj = obj.objects_by_name.get(obj_name, None)
                if not obj:
                    break
            
            else:    
                cache[splitted_attr[0]] = obj
            
        if obj:
            ret = obj.set_attribute_ex(splitted_attr[-1], value)
            old_values[attr] = ret['old_value']
    
    return old_values
            
 
def dynamic_render(dummy_object, objects_dict, parent=None):
    """
    Render dummy objects
    """
    application = managers.request_manager.get_request().application()
    
    for obj_id, obj in objects_dict.iteritems():
        application.all_dynamic_objects[obj_id] = obj
        
    result = managers.engine.render(
        application,
        dummy_object,
        parent,
        "vdom"
    )
    
    for obj_id, obj in objects_dict.iteritems():
        application.all_dynamic_objects.pop(obj_id, None)
    
    return result


def dummy_e2vdom(objects_dict):
    """
    Render dummy e2vdom objects
    """
    if not objects_dict:
        return ""
    
    out = ['<script>']
    for obj_id in objects_dict:
        out.append(
            '''var Obj_%s = {"eventEngine": {"eventDispatcher": {"eventArray": []}}};''' % obj_id.replace("-", "_")
        )
    out.append('</script>')
    
    return "\n".join(out)