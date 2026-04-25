import fs from 'node:fs'
import path from 'node:path'

const root = path.resolve(process.cwd(), 'out')
const appChunksRoot = path.join(root, '_next', 'static', 'chunks', 'app')

function listFiles(dir) {
  const out = []
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      out.push(...listFiles(full))
    } else {
      out.push(full)
    }
  }
  return out
}

function toStableJsName(fileName) {
  return fileName.replace(/-[0-9a-f]{8,}\.js$/i, '.js')
}

if (fs.existsSync(appChunksRoot)) {
  const replacements = []
  for (const file of listFiles(appChunksRoot)) {
    if (path.extname(file) !== '.js') continue
    const nextName = toStableJsName(path.basename(file))
    if (nextName === path.basename(file)) continue
    const target = path.join(path.dirname(file), nextName)
    fs.renameSync(file, target)
    replacements.push([path.basename(file), nextName])
  }

  if (replacements.length > 0) {
    for (const file of listFiles(root)) {
      const ext = path.extname(file).toLowerCase()
      if (!['.html', '.js', '.txt'].includes(ext)) continue
      let raw = fs.readFileSync(file, 'utf8')
      let changed = false
      for (const [from, to] of replacements) {
        if (raw.includes(from)) {
          raw = raw.split(from).join(to)
          changed = true
        }
      }
      if (changed) {
        fs.writeFileSync(file, raw, 'utf8')
      }
    }
  }
}
