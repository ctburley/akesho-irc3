class HuntStrings():
    def __init__(self):
        self.strings = {}
    
    def __setitem__(self, key, value, root=None):
        if root is not None:
            key = key.split('.', 1)
            root[key[0]] = self.__setitem__(key[1], value, root[key[0]].copy() if key[0] in root else {}) if len(key) > 1 else {**(root[key[0]] if key[0] in root else {}), **{'':value}}
            return root
        self.strings = self.__setitem__(key, value, self.strings.copy())
    
    def __getitem__(self, key, root=None):
        if root is not None:
            if '.' in key:
                key, keys = key.split('.', 1)
                return self.__getitem__(keys, root[key])
            return root[key]['']
        return self.__getitem__(key, self.strings)

    
    def __delitem__(self, key, root=None):
        if root is None:
            self.__delitem__(key, self.strings)
        else:
            if '.' in key:
                key, keys = key.split('.', 1)
                if key in root:
                    self.__delitem__(keys, root[key])
            else:
                del root[key]


    def load_defaults(self):
        self['default.hunt'] = 'deks'
        
        self['deks.gallery'] = 'this channel'
        self['deks.storage'] = 'deks'
        self['deks.help'] = 'welcome to shitty dek hunt, !fren or !beng, check your !deks and leader boards, !friendos and !bangers'
        
        self['deks.quarry'] = 'dek'
        self['deks.quarry.plural'] = 'deks'
        self['deks.quarry.release'] = 'there is a dek.'
        self['deks.quarry.reminder'] = '{spaces}flap.'
        
        self['deks.hunt'] = 'hunt'
        self['deks.hunt.enabled'] = 'the hunt is on.'
        self['deks.hunt.disabled'] = 'the hunt is not on.'
        self['deks.hunt.start'] = 'ok hot stuff, bring it on!'
        self['deks.hunt.stop'] = 'i see how it is, pansy!'
        self['deks.hunt.verbose'] = 'i will not be less verbose. repeat to toggle.'
        self['deks.hunt.quieter'] = 'i will now be less verbose. repeat to toggle.'
        
        self['deks.mine'] = 'deks'
        self['deks.deks'] = 'Hey, {nick}, ur fastest dek was {fastest}s, and slowest was {slowest}s, and you has {fren} dek frens protecting you from {beng} dek emines.'
        self['deks.deks.targeted'] = '{nick}, {target} has {fren} frens, {beng} emine; their fastest dek was {fastest}s, and slowest was {slowest}s.'
        
        self['deks.times'] = 'dektimes'
        self['deks.dektimes'] = "Fastest dekerino is {fastname} in {fastchannel} with {fastseconds} seconds. Longest time a dek has been free is {slowseconds} seconds. {slowname} ended that in {slowchannel}."
        
        self['deks.trigger.fren.top.cmd'] = 'friendos'
        self['deks.trigger.fren.top.string'] = ":: best friendos :: "
        self['deks.trigger.fren.top.sort'] = '>'
        self['deks.trigger.fren.timerecord.fast'] = "Wowee that is your fastest dek yet!"
        self['deks.trigger.fren.timerecord.slow'] = "That was your longest so far, what took you so long bby?"
        self['deks.trigger.fren.success'] = "henk henk henk! after {seconds} seconds; {nick}, {friends} deks now owe you a life debt. {timerecord}"
        self['deks.trigger.fren.failure'] = "there is no dek, why you do that?"

        self['deks.trigger.beng.top.cmd'] = 'bangers'
        self['deks.trigger.beng.top.string'] = ":: dem bangerinos :: "
        self['deks.trigger.beng.top.sort'] = '<'
        self['deks.trigger.beng.timerecord.fast'] = "Wowee that is your fastest dek yet! "
        self['deks.trigger.beng.timerecord.slow'] = "That was your longest so far, nearly got away! "
        self['deks.trigger.beng.success'] = "pew, pew, pew; {nick} kills a dek in the face in {seconds} seconds! {timerecord}Watching from the shadows are {beng} ghostly pairs of beady eyes."
        self['deks.trigger.beng.failure'] = "watch out, is no dek, no pew pew!"
    
