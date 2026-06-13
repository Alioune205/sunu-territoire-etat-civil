import os
for root, dirs, files in os.walk('lib'):
    for file in files:
        if file.endswith('.dart'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'showModalBottomSheet' in content and 'useRootNavigator: true' not in content:
                content = content.replace('showModalBottomSheet(', 'showModalBottomSheet(\n      useRootNavigator: true,')
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated {path}")
