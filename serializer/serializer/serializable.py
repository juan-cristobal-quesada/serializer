'''
Created on 20 feb. 2019

@author: jcquesada
'''
class Serializable(dict):
    
    def __init__(self, serialized_attr_value):
        self['serializable_class'] = True 
        self['serializable_attribute_value'] = serialized_attr_value
    
    @property
    def raw_value(self):
        return self['serializable_attribute_value']