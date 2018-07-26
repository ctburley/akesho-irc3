class Storage():
    def __init__(self):
        self.data = {}
    
    def __setitem__(self, key, value, root=None):
        if root is not None:
            key = key.split('.', 1)
            root[key[0]] = self.__setitem__(key[1], value, root[key[0]].copy() if key[0] in root else {}) if len(key) > 1 else {**(root[key[0]] if key[0] in root else {}), **{'':value}}
            return root
        self.data = self.__setitem__(key, value, self.data.copy())
    
    def __getitem__(self, key, root=None):
        if root is not None:
            if '.' in key:
                key, keys = key.split('.', 1)
                return self.__getitem__(keys, root[key])
            return root[key]['']
        return self.__getitem__(key, self.data)

    
    def __delitem__(self, key, root=None):
        if root is None:
            self.__delitem__(key, self.data)
        else:
            if '.' in key:
                key, keys = key.split('.', 1)
                if key in root:
                    self.__delitem__(keys, root[key])
            else:
                del root[key]
