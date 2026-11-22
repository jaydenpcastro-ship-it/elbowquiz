import bpy
for o in bpy.data.objects:
    n=o.name.lower()
    if o.type=='MESH' and n.endswith('.r') and any(k in n for k in ('triceps','biceps','brachialis','anconeus','supinator','pronator','brachioradialis','bicipital')):
        print('OBJ', o.name, len(o.data.vertices))
print('PROBE DONE')
