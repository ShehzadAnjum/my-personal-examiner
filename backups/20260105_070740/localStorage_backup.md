# localStorage Backup Instructions

The frontend caches explanations in browser localStorage. Follow these steps to backup:

## Step 1: Open Browser DevTools
- Press F12 (or Cmd+Option+I on Mac)
- Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
- Click **Local Storage** → your site URL

## Step 2: Export Explanation Cache
Run this in the browser console (F12 → Console):

```javascript
// Export all explanation cache entries
const backup = {};
for (let i = 0; i < localStorage.length; i++) {
  const key = localStorage.key(i);
  if (key && (key.startsWith('explanation_') || key.startsWith('cached_'))) {
    backup[key] = localStorage.getItem(key);
  }
}

// Download as JSON file
const blob = new Blob([JSON.stringify(backup, null, 2)], {type: 'application/json'});
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'localStorage_backup_' + new Date().toISOString().slice(0,10) + '.json';
a.click();
URL.revokeObjectURL(url);

console.log('✅ Backup downloaded! Keys exported:', Object.keys(backup).length);
```

## Step 3: Save the Downloaded File
Move the downloaded JSON file to this backup directory:
`backups/TIMESTAMP/localStorage_backup.json`

## Restore Instructions (If Needed)
```javascript
// Import from backup file
const input = document.createElement('input');
input.type = 'file';
input.accept = '.json';
input.onchange = async (e) => {
  const file = e.target.files[0];
  const text = await file.text();
  const backup = JSON.parse(text);

  for (const [key, value] of Object.entries(backup)) {
    localStorage.setItem(key, value);
  }
  console.log('✅ Restored', Object.keys(backup).length, 'entries');
};
input.click();
```
