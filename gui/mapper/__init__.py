from adapters import auto_map
# a mapper map an object to a form
# the mapper have to method, load and dump.
# a mapper associate objects properties to form elements

# if that forms elements are known, they can set/get information from them
# if not, you have to add to give your adaptator

# please note that a mapper never check constraint on the data, this is the object job.




class InterfaceMapper(object):
    """
    An interface mapper associate an object properties with adapters.
    vith load and dump method, you can synchrosize the adapters and the object
    properties values
    """
    def __init__(self,adapters):
        """
        Initialize the Mapper.

        Adapters have to be a dictionay. Key are object's properties, values are adapters
        """
        self._adapters = adapters

    def update(self,adapters):
        self._adapters.update(adapters)

    def load(self,object):
        """Set all the object properties to adapters values"""
        for key,val in self._adapters.iteritems():
            setattr(object,key,val.get())
    def dump(self,object):
        """Set all the adapters values to object properties"""
        for key,val in self._adapters.iteritems():
            val.set(getattr(object,key))
    def load_dict(self):
        dict = {}
        for key,val in self._adapters.iteritems():
            dict[key] = val.get()
        return dict


        
def interface_auto_map(widgets):
    """
    Return an InterfaceMapper with all the widget associated with their
    corresponding adapter, if exists. Otherwise, return KeyError
    """

    return InterfaceMapper(auto_map(widgets))
