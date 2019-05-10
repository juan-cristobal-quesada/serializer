'''
Created on 20 feb. 2019

@author: jcquesada
'''

import types
import base64
import serializable.Serializable as Serializable
import cPickle
import importlib

class Serializer(object):

    @classmethod
    def empty(cls,*args,**kwargs):
        return cls(*args,**kwargs)
    
    def __serialize_attribute_value(self, attr_value, readable=False):
        serialized_attribute_value = attr_value.serialize_attributes(readable=readable)
        inner_type_serializable = Serializable(serialized_attribute_value, 
                                               attr_value.__class__.__module__,
                                               attr_value.__class__.__name__)
        return inner_type_serializable
    
    def __deserialize_attribute_value(self, inner_type_serializable):
        module_name = inner_type_serializable.class_module
        module = importlib.import_module(module_name)
        class_name = inner_type_serializable.class_name
        class_type = getattr(module, class_name)
        o = class_type.empty()
        o.deserialize_attributes(inner_type_serializable.raw_value)
        return o

    def __r_serialize_list(self, l):
        result_list = []
        
        for e in l:
            if isinstance(e, self.__class__):
                e = self.__serialize_attribute_value(e)
            elif type(e) == types.ListType:
                e = self.__r_serialize_list(e)
            elif type(e) == types.DictType:
                e = self.__r_serialize_dict(e)
            result_list.append(e) 
        
        return result_list
    
    def __r_deserialize_list(self, l):
        result_list = []
        for e in l:
            if isinstance(e, Serializable):
                e = self.__deserialize_attribute_value(e)
            elif type(e) == types.ListType:
                e = self.__r_deserialize_list(e)
            elif type(e) == types.DictType:
                e = self.__r_deserialize_dict(e)
            result_list.append(e)
        return result_list
    
    def __r_deserialize_dict(self, d):
        result_dict = {}
        for k,v in d.iteritems():
            if isinstance(v, Serializable):
                v = self.__deserialize_attribute_value(v)
            elif type(v) == types.ListType:
                v = self.__r_deserialize_list(v)
            elif type(v) == types.DictType:
                v = self.__r_deserialize_dict(v)
            result_dict[k] = v
        
        return result_dict
        
    def __r_serialize_dict(self, d):
        result_dict = {}
        for k, v in d.iteritems():
            if isinstance(v, self.__class__):
                v = self.__serialize_attribute_value(v)
            elif type(v) == types.ListType:
                v = self.__r_serialize_list(v)
            elif type(v) == types.DictType:
                v = self.__r_serialize_dict(v)
            result_dict[k] = v
        return result_dict 
    
    def serialize_attributes(self):
        serialized_attributes_dict = {}
        for attr_name, attr_value in self.__dict__.iteritems():
            if isinstance(attr_value, Serializable):
                attr_value = self.__serialize_attribute_value(attr_value)
                
            elif type(attr_value) == types.ListType:
                attr_value = self.__r_serialize_list(attr_value)
        
            elif type(attr_value) == types.DictType:
                attr_value = self.__r_serialize_dict(attr_value)
                    
            if all(type(attr_value) != t for t in (types.BooleanType,
                                                   types.FloatType,
                                                   types.IntType,
                                                   types.LongType,
                                                   types.DictType,
                                                   types.ListType,
                                                   types.StringType,
                                                   types.UnicodeType)):
                continue
            serialized_attributes_dict[attr_name] = attr_value

        serialized_attributes_str = cPickle.dumps(serialized_attributes_dict, cPickle.HIGHEST_PROTOCOL)
        return base64.b64encode(serialized_attributes_str)    
    
    def deserialize_attributes(self, serialized_attributes_str):
        serialized_attributes_str = base64.b64decode(serialized_attributes_str)
        deserialized_attributes_dict = cPickle.loads(serialized_attributes_str)
        
        d_result = {}
        for attr_name, attr_value in deserialized_attributes_dict.iteritems():
            if type(attr_value) == types.ListType:
                attr_value = self.__r_deserialize_list(attr_value)
            elif type(attr_value) == types.DictType:
                attr_value = self.__r_deserialize_dict(attr_value)
            elif isinstance(attr_value, Serializable):
                attr_value = self.__deserialize_attribute_value(attr_value)
            d_result[attr_name] = attr_value
        
        deserialized_attributes_dict = d_result       
        self.__dict__.update(deserialized_attributes_dict)
    
    
    def serialize_whole(self):
        whole_object_serialized = cPickle.dumps(self, cPickle.HIGHEST_PROTOCOL)
        return base64.b64encode(whole_object_serialized)
        
    def deserialize_whole(self, whole_object_serialized):
        if type(whole_object_serialized) != types.StringType:
            raise TypeError('Expected <str>, found ' + str(type(whole_object_serialized)) + '.')
        
        b64decoded_object = base64.b64decode(whole_object_serialized)

        new_object = cPickle.loads(b64decoded_object)
        self.__dict__.update(new_object.__dict__)
        