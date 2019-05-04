import englishActions as actions
import pickle
import jsons as json
import time
import datetime
import hashlib

json.suppress_warnings()

memformat = "0.3.0"

class Thing:
    setTime = False
    def __init__(self, w=True, d="", t="string", a={}):
        self.writeable = w
        self.setData(d=d, t=t)
        if Thing.setTime:
            self.settime = time.time()
        else:
            self.settime = 0
        self.attributes = a

    def __str__(self):
        return str(self.getData()) + str(self.attributes)

    def __repr__(self):
        return repr(self.getData()) + repr(self.attributes)

    def setData(self, d="", t=None):
        if t == None:
            if isinstance(d, str):
                t = "string"
            elif d == None:
                t = "idea"
        self.dataType = t
        if self.dataType == "collection":
            if not isinstance(self.dataValue, list):
                self.dataValue = []
            if isinstance(d, Thing):
                self.dataValue.append(d)
            else:
                self.dataValue.append(Thing(d=d))
                print(d)
        else:   
            self.dataValue = d

    def removeData(self, d=None):
        if d == None:
            self.setData(d=None)
        elif self.dataType == "collection":
            self.dataValue.remove(d)

    def getData(self):
        if self.dataType == "string":
            return self.dataValue
        if self.dataType == "collection":
            v = []
            for i in self.dataValue:
                if isinstance(i, Link):
                    v.append("the " + i.getData())
                elif isinstance(i, Thing):
                    v.append("a " + i.getData())
                else:
                    v.append("a " + i)
            if len(v) > 1:
                v[-1] = v[-2] + " and " + v.pop(-1)
            return ", ".join(v)
        elif self.dataType == "idea":
            return None
        elif self.dataType == "functional":
            return self.dataValue()
        
    def get(self, key, value):
        return self.attributes.get(key, value)

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, value):
        self.attributes[key] = value
    
    def getRef(self):
        return self

class Link(Thing):
    links = []
    def __init__(self, path=""):
        self.path = path
        Link.links.append(self)
        self.ref = None

    def __str__(self):
        return str(self.ref)

    def __repr__(self):
        return "<" + self.path + "> "

    @classmethod
    def setLinks(cls):
        for self in cls.links:
            self.linkTo()

    @property
    def writeable(self):
        return self.ref.writeable

    @writeable.setter
    def writeable(self, w):
        self.ref.writeable = w

    def linkTo(self):
        global mem
        path = self.path.split(".")
        if isinstance(path, str):
            path = [path]
        placement = mem
        for l in path:
            placement = placement[l]
        self.ref = placement

    def setData(self, d="", t=None):
        return self.ref.setData(d, t)

    def removeData(self, d):
        return self.ref.setData(d)

    def getData(self):
        return self.ref.getData()

    def get(self, key, value):
        return self.ref.get(key, value)

    def __getitem__(self, key):
        return self.ref[key]

    def getRef(self):
        return self

def data_getTime():
    return str(datetime.datetime.now().strftime("%I:%M %p"))

def data_getDate():
    return str(datetime.datetime.now().strftime("%d %B, %Y"))

mem = {
    "green": Thing(w=False, d="green", t="string", a={
        }),
    "red": Thing(w=False, d="red", t="string", a={
        }),
    "blue": Thing(w=False, d="blue", t="string", a={
        }),
    "yellow": Thing(w=False, d="yellow", t="string", a={
        }),
    "orange": Thing(w=False, d="orange", t="string", a={
        }),
    "purple": Thing(w=False, d="purple", t="string", a={
        }),
    "pink": Thing(w=False, d="pink", t="string", a={
        }),
    "white": Thing(w=False, d="white", t="string", a={
        }),
    "black": Thing(w=False, d="black", t="string", a={
        }),
    "brown": Thing(w=False, d="brown", t="string", a={
        }),
    "cyan": Thing(w=False, d="cyan", t="string", a={
        }),
    "color": Thing(w=False, d=None, t="idea", a={
        "best": Link("green"),
        "worst": Link("pink"),
        }),
    "time": Thing(w=False, d=data_getTime, t="functional", a={
        }),
    "date": Thing(w=False, d=data_getDate, t="functional", a={
        }),
    "^USER": Thing(w=False, d=None, t="idea", a={ #I, me, mine
        }),
    "^MALE": Thing(w=False, d=None, t="idea", a={ #He, him, his
        }),
    "^FMAL": Thing(w=False, d=None, t="idea", a={ #She, her, hers
        }),
    }
Thing.setTime = True

Link.setLinks()

memHash = hashlib.sha256()
memHash.update(json.dumps(mem).encode("ascii"))

memHeads = {
    "poss":{
        "i":"^USER",
        "me":"^USER",
        "my":"^USER",
        "mine":"^USER",
        "he":"^MALE",
        "him":"^MALE",
        "his":"^MALE",
        "she":"^FMAL",
        "her":"^FMAL",
        "hers":"^FMAL",
        },
    "nsubj":{
        "i":"^USER",
        "me":"^USER",
        "my":"^USER",
        "mine":"^USER",
        "he":"^MALE",
        "him":"^MALE",
        "his":"^MALE",
        "she":"^FMAL",
        "her":"^FMAL",
        "hers":"^FMAL",
        },
    }
memChildsPath = {
    "acomp": None,
    "attr": None,
    "amod":{
        "advmod": None,
        }
    }

def _close():
    global mem
    with open('englishActions/vbf.oam', mode="wb") as f:
        pickle.dump({"format": memformat, "memory": mem, "memory_hash": memHash.digest()}, f)

def _open():
    global mem
    try:
        with open('englishActions/vbf.oam', mode="rb") as f:
            try:
                rawdat = pickle.load(f)
                if rawdat["format"] == memformat:
                    if rawdat["memory_hash"] == memHash.digest():
                        mem = rawdat["memory"]
            except AttributeError:
                pass
    except EOFError:
        pass
    except FileNotFoundError:
        pass

def vb_be(root, subjects):
    global mem
    ret = ""
    interrogative = False
    for subject in subjects:
        for s in subject:
            if isinstance(s, str):
                if s[0] == u'W':
                    interrogative = True
                    break
            else:
                if s.tag_[0] == u'W':
                    interrogative = True
                    break
    if not interrogative:
        attributes = actions.getDependency(root, u'attr')
        for attr in attributes:
            if attr.tag_[0] == u'W':
                interrogative = True
                break
            for det in actions.getDependency(attr, u'det'):
                if det.tag_[0] == u'W':
                    interrogative = True
                    break
    if interrogative:
        for subject in subjects:
            for s in subject:
                if s.text != "what":
                    item = [s.text]
                    for head in memHeads.keys():
                        for h in actions.getDependency(s, head):
                            item.insert(0, memHeads[head].get(h.text.lower(), h.text.lower()))
                        if s.dep_ == head:
                            item[-1] = memHeads[head].get(s.text.lower(), s.text.lower())
                    vb_be_childsearch(memChildsPath, item, s)
                    path = mem
                    print(item)
                    for part in item:
                        p = path.get(part, Thing(d = None, t = "idea"))
                        path[part] = p
                        path = p
                    if path.getData() == None:
                        ret += "I don't know. "
                    else:
                        ret += path.getData()
    else:
        for subject in subjects:
            for s in subject:
                item = [s.text]
                for head in memHeads.keys():
                    for h in actions.getDependency(s, head):
                        item.insert(0, memHeads[head].get(h.text.lower(), h.text.lower()))
                    if s.dep_ == head:
                        item[-1] = memHeads[head].get(s.text.lower(), s.text.lower())
                vb_be_childsearch(memChildsPath, item, s)
                path = mem
                for part in item:
                    p = path.get(part, Thing(d = None, t = "idea"))
                    path[part] = p
                    path = p
                deps = ["acomp", "attr", "dobj"]
                for dep in deps:
                    val = actions.getDependency(root, dep)
                    if len(val) > 0:
                        if path.writeable:
                            path.setData(val[0].text)
                            ret += "okay. "
                        else:
                            if val[0].text != path.getData():
                                ret += "No, it's not. "
                            else:
                                ret += "Yes, it is. "
    return ret

def vb_be_childsearch(p, item, s):
    for child in p.keys():
        for c in actions.getDependency(s, child):
            item.append(c.text)
            if p[child] != None:
                vb_be_childsearch(p[child], item, c)
    #return item

def vb_like(root, subjects):
    global mem
    ret = ""
    interrogative = False
    for subject in subjects:
        for s in subject:
            if isinstance(s, str):
                if s[0] == u'W':
                    interrogative = True
                    break
            else:
                if s.tag_[0] == u'W':
                    interrogative = True
                    break
    if not interrogative:
        attributes = actions.getDependency(root, u'attr')
        for attr in attributes:
            if attr.tag_[0] == u'W':
                interrogative = True
                break
            for det in actions.getDependency(attr, u'det'):
                if det.tag_[0] == u'W':
                    interrogative = True
                    break
        for pobj in actions.getDependency(root, u'pobj'):
            if pobj.tag_[0] == u'W':
                interrogative = True
                break
        for dobj in actions.getDependency(root, u'dobj'):
            if dobj.tag_[0] == u'W':
                interrogative = True
                break
    if interrogative:
        for subject in subjects:
            for s in subject:
                if s.text != "what":
                    item = [s.text]
                    for head in memHeads.keys():
                        for h in actions.getDependency(s, head):
                            item.insert(0, memHeads[head].get(h.text.lower(), h.text.lower()))
                        if s.dep_ == head:
                            item[-1] = memHeads[head].get(s.text.lower(), s.text.lower())
                    item.append("likes")
                    vb_like_childsearch(memChildsPath, item, s)
                    path = mem
                    print(item)
                    for part in item:
                        p = path.get(part, Thing(d = None, t = "idea"))
                        path[part] = p
                        path = p
                    if path.getData() == None:
                        ret += "I don't know. "
                    else:
                        ret += path.getData()
    else:
        for subject in subjects:
            for s in subject:
                item = [s.text]
                for head in memHeads.keys():
                    for h in actions.getDependency(s, head):
                        item.insert(0, memHeads[head].get(h.text.lower(), h.text.lower()))
                    if s.dep_ == head:
                        item[-1] = memHeads[head].get(s.text.lower(), s.text.lower())
                item.append("likes")
                vb_like_childsearch(memChildsPath, item, s)
                path = mem
                print(item)
                for part in item:
                    p = path.get(part, Thing(d = None, t = "idea"))
                    path[part] = p
                    path = p
                deps = ["acomp", "attr", "dobj"]
                for dep in deps:
                    val = actions.getDependency(root, dep)
                    if len(val) > 0:
                        if path.writeable:
                            path.setData(val[0].text, t="collection")
                            ret += "okay. "
                        else:
                            if val[0].text != path.getData():
                                ret += "No, it's not. "
                            else:
                                ret += "Yes, it is. "
    return ret

def vb_like_childsearch(p, item, s):
    for child in p.keys():
        for c in actions.getDependency(s, child):
            item.append(c.text)
            if p[child] != None:
                vb_be_childsearch(p[child], item, c)
    #return item

def vb_need(root, subjects):
    global mem
    ret = ""
    interrogative = False
    for subject in subjects:
        for s in subject:
            if isinstance(s, str):
                if s[0] == u'W':
                    interrogative = True
                    break
            else:
                if s.tag_[0] == u'W':
                    interrogative = True
                    break
    if not interrogative:
        attributes = actions.getDependency(root, u'attr')
        for attr in attributes:
            if attr.tag_[0] == u'W':
                interrogative = True
                break
            for det in actions.getDependency(attr, u'det'):
                if det.tag_[0] == u'W':
                    interrogative = True
                    break
        for pobj in actions.getDependency(root, u'pobj'):
            if pobj.tag_[0] == u'W':
                interrogative = True
                break
        for dobj in actions.getDependency(root, u'dobj'):
            if dobj.tag_[0] == u'W':
                interrogative = True
                break
    if interrogative:
        for subject in subjects:
            for s in subject:
                if s.text != "what":
                    item = [s.text]
                    for head in memHeads.keys():
                        for h in actions.getDependency(s, head):
                            item.insert(0, memHeads[head].get(h.text.lower(), h.text.lower()))
                        if s.dep_ == head:
                            item[-1] = memHeads[head].get(s.text.lower(), s.text.lower())
                    item.append("needs")
                    vb_need_childsearch(memChildsPath, item, s)
                    path = mem
                    print(item)
                    for part in item:
                        p = path.get(part, Thing(d = None, t = "idea"))
                        path[part] = p
                        path = p
                    if path.getData() == None:
                        ret += "I don't know. "
                    else:
                        ret += path.getData()
    else:
        for subject in subjects:
            for s in subject:
                item = [s.text]
                for head in memHeads.keys():
                    for h in actions.getDependency(s, head):
                        item.insert(0, memHeads[head].get(h.text.lower(), h.text.lower()))
                    if s.dep_ == head:
                        item[-1] = memHeads[head].get(s.text.lower(), s.text.lower())
                item.append("needs")
                vb_need_childsearch(memChildsPath, item, s)
                path = mem
                print(item)
                for part in item:
                    p = path.get(part, Thing(d = None, t = "idea"))
                    path[part] = p
                    path = p
                deps = ["acomp", "attr", "dobj"]
                for dep in deps:
                    val = actions.getDependency(root, dep)
                    if len(val) > 0:
                        if path.writeable:
                            path.setData(val[0].text, t="collection")
                            ret += "okay. "
                        else:
                            if val[0].text != path.getData():
                                ret += "No, it's not. "
                            else:
                                ret += "Yes, it is. "
    return ret

def vb_need_childsearch(p, item, s):
    for child in p.keys():
        for c in actions.getDependency(s, child):
            item.append(c.text)
            if p[child] != None:
                vb_be_childsearch(p[child], item, c)
    #return item

def vb_want(root, subjects):
    global mem
    ret = ""
    interrogative = False
    for subject in subjects:
        for s in subject:
            if isinstance(s, str):
                if s[0] == u'W':
                    interrogative = True
                    break
            else:
                if s.tag_[0] == u'W':
                    interrogative = True
                    break
    if not interrogative:
        attributes = actions.getDependency(root, u'attr')
        for attr in attributes:
            if attr.tag_[0] == u'W':
                interrogative = True
                break
            for det in actions.getDependency(attr, u'det'):
                if det.tag_[0] == u'W':
                    interrogative = True
                    break
        for pobj in actions.getDependency(root, u'pobj'):
            if pobj.tag_[0] == u'W':
                interrogative = True
                break
        for dobj in actions.getDependency(root, u'dobj'):
            if dobj.tag_[0] == u'W':
                interrogative = True
                break
    if interrogative:
        for subject in subjects:
            for s in subject:
                if s.text != "what":
                    item = [s.text]
                    for head in memHeads.keys():
                        for h in actions.getDependency(s, head):
                            item.insert(0, memHeads[head].get(h.text.lower(), h.text.lower()))
                        if s.dep_ == head:
                            item[-1] = memHeads[head].get(s.text.lower(), s.text.lower())
                    item.append("wants")
                    vb_want_childsearch(memChildsPath, item, s)
                    path = mem
                    print(item)
                    for part in item:
                        p = path.get(part, Thing(d = None, t = "idea"))
                        path[part] = p
                        path = p
                    if path.getData() == None:
                        ret += "I don't know. "
                    else:
                        ret += path.getData()
    else:
        for subject in subjects:
            for s in subject:
                item = [s.text]
                for head in memHeads.keys():
                    for h in actions.getDependency(s, head):
                        item.insert(0, memHeads[head].get(h.text.lower(), h.text.lower()))
                    if s.dep_ == head:
                        item[-1] = memHeads[head].get(s.text.lower(), s.text.lower())
                item.append("wants")
                vb_want_childsearch(memChildsPath, item, s)
                path = mem
                print(item)
                for part in item:
                    p = path.get(part, Thing(d = None, t = "idea"))
                    path[part] = p
                    path = p
                deps = ["acomp", "attr", "dobj"]
                for dep in deps:
                    val = actions.getDependency(root, dep)
                    if len(val) > 0:
                        if path.writeable:
                            path.setData(val[0].text, t="collection")
                            ret += "okay. "
                        else:
                            if val[0].text != path.getData():
                                ret += "No, it's not. "
                            else:
                                ret += "Yes, it is. "
    return ret

def vb_want_childsearch(p, item, s):
    for child in p.keys():
        for c in actions.getDependency(s, child):
            item.append(c.text)
            if p[child] != None:
                vb_be_childsearch(p[child], item, c)
    #return item

    
vbz = {
    "be":vb_be,
    "like":vb_like,
    "appreciate":vb_like,
    "love":vb_like,
    "need":vb_need,
    "require":vb_need,
    "want":vb_want,
    "desire":vb_want,
    "wish":vb_want,
    "demand":vb_want,
    "covet":vb_want,
    "crave":vb_want,
    "hanker":vb_want,
    "hunger":vb_want,
    "lust":vb_want,
    "pine":vb_want,
    "long":vb_want,
    "strive":vb_want,
    "thirst":vb_want,
    "fancy":vb_want,
    }