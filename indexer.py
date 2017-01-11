import os
import json
root_dir = 'media/upload/images'
blacklist = (
    'index.html',
    'index.json',
    '.DS_Store',
)
all_files = []
for root, dirs, files in os.walk(root_dir):
    all_files.extend([
        os.path.join(root, _)
        for _ in files
        if _ not in blacklist
    ])
print len(all_files)
with open('data/gallery_files.json', 'w') as f:
    json.dump(all_files, f, indent=2)
    print 'json dump done'
# /static/tumblr_images/youbeixing/tumblr_nzlke3VXTA1u6bsy0o1_540.jpg
print 'done'
