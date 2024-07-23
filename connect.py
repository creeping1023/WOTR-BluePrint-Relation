# %%
import zipfile
zip_path = 'D:/Steam/steamapps/common/Pathfinder Second Adventure/blueprints.zip'

# %%
by_id = dict()

# %%
def get_id(data:dict):
    return data['AssetId']

def get_parent_id(data:dict):
    if 'ParentAsset' not in data['Data']: return None
    return data['Data']['ParentAsset']

def get_type_id(data:dict):
    return data['Data']['$type'].split(',')[0]


# %%
import re
regex = r"[0-9a-z]{32}"

# %%
parent_dict_actual = dict()
parent_dict_literal = dict()
children_dict = dict()

with zipfile.ZipFile(zip_path, 'r') as z:
    for file_info in z.infolist():
        with z.open(file_info) as file:
            path = file_info.filename
            if path.endswith('.jbp'):
                content = file.read().decode('utf-8')
                data = json.loads(content)
                id = get_id(data)
                by_id[get_id(data)] = path
                parent_id = get_parent_id(data)
                type_id = get_type_id(data)
                children = [c for c in re.findall(regex, content) if c!=id and c!=parent_id and c!=type_id]
                children_dict[id] = children
                for c in children:
                    if c not in parent_dict_actual:
                        parent_dict_actual[c] = set()
                    parent_dict_actual[c].add(id)
                if parent_id:
                    parent_dict_literal[id] = parent_id

# %%
import os
if not os.path.exists('data'):
    os.makedirs('data')

import json
keys = set(parent_dict_actual.keys()).union(set(parent_dict_literal.keys())).union(set(children_dict.keys()))
for id in keys:
    if id in by_id:
        parents = (id in parent_dict_actual and list(parent_dict_actual[id])) or (id in parent_dict_literal and [parent_dict_literal[id]]) or []
        parents = list(map(lambda x:by_id[x].replace('.jbp', ''), filter(lambda x: x in by_id, parents)))
        children = children_dict.get(id) or []
        children = list(map(lambda x:by_id[x].replace('.jbp', ''), filter(lambda x: x in by_id, children)))
        obj = {}
        if len(parents):
            obj['parents'] = parents
        if len(children):
            obj['children'] = children
        if len(parents) or len(children):
            path = by_id[id].replace('/', '~').replace('.jbp', '')
            with open(f'data/{path}.json', 'w') as f:
                json.dump(obj, f)
