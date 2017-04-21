"""
This script convert bibtex generated from DBLP (tier 1, standard)
to json

"""
import simplejson as js
import sys
import re

# Process an extracted entry
def process_entry(entry):
    processed = {}
    # Find the publication type
    pub_type = re.search(r'@\w+?{.+?,', entry)
    if pub_type == None:
        raise LookupError("Missing publication type - bib entry: %s"%entry)
    else:
        type_key = pub_type.group()
        idx_t = type_key.index('{')
        processed['pubtype'] = type_key[1:idx_t]
        processed['key'] = type_key[idx_t+1: -1]
    # Find other key value pairs
    entry = entry.replace(type_key, '')
    items = entry.split('},')
    for item in items:
        item = item.replace('{', '').replace('}', '')
        key, value = item.split('=', 1)
        if key.strip() in ['author', 'editor']:
            value = [v.strip() for v in value.split(' and ')]
        else:
            value = value.strip()
        processed[key.strip()] = value
    # Get a desciption item for different type of publications
    desc = []
    if processed['pubtype'] == 'inproceedings':
#        print processed['pubtype']
        desc.append('In %s'%processed['booktitle'])
        if processed.get('pages'):
            desc.append('pp.%s'%processed['pages'])
        desc.append(processed['publisher'])
#        print ', '.join(desc)

    elif processed['pubtype'] == 'proceedings':
#        print processed['pubtype']
        desc.append(processed['series'])
        desc.append('volume %s'%processed['volume'])
        desc.append(processed['publisher'])
#        print ', '.join(desc)

    elif processed['pubtype'] == 'article':
#        print processed['pubtype']
        desc.append(processed['journal'])
        vol = []
        vol.append('%s'%processed['volume'])
        if processed.get('number'):
             vol.append('(%s)'%processed['number'])
        desc.append(''.join(vol))
        if processed.get('pages'):
            desc.append('pp.%s'%processed['pages'])
        desc.append(processed['year'])
#        print ', '.join(desc)

    elif processed['pubtype'] == 'book':
#        print processed['pubtype']
        desc.append(processed['series'])
        desc.append(processed['volume'])
        desc.append(processed['publisher'])
        desc.append(processed['year'])
#        print ', '.join(desc)

    elif processed['pubtype'] == 'incollection':
#        print processed['pubtype']
        desc.append(processed['booktitle'])
        desc.append(processed['series']),
        desc.append('volume %s'%processed['volume']),
        if processed.get('pages'):
            desc.append(processed['pages'])
        desc.append(processed['year'])
#        print ', '.join(desc)
    else:
         raise ValueError('Undefined type: %s'%entry)
 
    processed['desc'] = ', '.join(desc)

    return processed

def process_bib(f):
    entries = []
    entry = [] 
    for line in f:
        line = line.strip()
        if line.startswith('@'):
            # A new entry
            if not entry == []:
                entries.append(process_entry(' '.join(entry)))
                entry = [] 
        # Store the line to the current entry
        entry.append(line)
    if not entry == []:
        entries.append(process_entry(' '.join(entry)))
    return entries

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "usage: python bib2json.py bibfile"
   
    entries = [] 
    with open(sys.argv[1]) as f:
        entries = process_bib(f)
    print(js.dumps(entries))
