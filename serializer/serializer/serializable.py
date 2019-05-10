'''
Created on 20 feb. 2019

@author: jcquesada
'''
class Serializable(dict):
    
    def __init__(self, serialized_attr_value, class_module, class_name):
        self['serializable_class_module'] = class_module
        self['serializable_class'] = class_name
        self['serializable_attribute_value'] = serialized_attr_value
    
    @property
    def raw_value(self):
        return self['serializable_attribute_value']
    
    @property
    def class_name(self):
        return self['serializable_class']
    @property
    def class_module(self):
        return self['serializable_class_module']